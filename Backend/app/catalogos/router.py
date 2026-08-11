from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.catalogos import models, schemas
from app.catalogos.crud import (
    CatalogCRUD,
    CatalogIntegrityError,
    CatalogValidationError,
)
from app.database import get_db


router = APIRouter(prefix="/catalogos")


# ==========================================================
# CONFIGURACIÓN DECLARATIVA DE CADA CATÁLOGO
# ==========================================================

@dataclass(frozen=True)
class CatalogRouteConfig:
    path: str
    tag: str
    entity_label: str
    crud: CatalogCRUD
    read_schema: type[BaseModel]
    create_schema: type[BaseModel]
    update_schema: type[BaseModel]
    filter_field: str | None = None
    filter_query_param: str | None = None


def _http_409(exc: CatalogIntegrityError) -> HTTPException:
    detail: dict[str, Any] = {"message": exc.message}
    if exc.constraint:
        detail["constraint"] = exc.constraint
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def _register_catalog_routes(config: CatalogRouteConfig) -> None:
    """
    Registra el CRUD REST completo de un catálogo.

    Cada catálogo conserva un tag propio en Swagger/OpenAPI, aunque internamente
    reutilice la misma implementación CRUD. Esto reduce duplicación sin perder
    claridad documental ni endpoints específicos.
    """

    path = f"/{config.path}"
    item_path = f"/{config.path}/{{item_id}}"
    read_schema = config.read_schema
    create_schema = config.create_schema
    update_schema = config.update_schema

    if config.filter_field and config.filter_query_param:

        def list_items(
            q: str | None = Query(
                default=None,
                description="Búsqueda parcial, sin distinguir mayúsculas/minúsculas",
            ),
            skip: int = Query(default=0, ge=0),
            limit: int = Query(default=100, ge=1, le=500),
            parent_id: int | None = Query(
                default=None,
                ge=1,
                alias=config.filter_query_param,
                description=f"Filtro por {config.filter_query_param}",
            ),
            db: Session = Depends(get_db),
        ):
            try:
                return config.crud.list(
                    db,
                    skip=skip,
                    limit=limit,
                    search=q,
                    filters={config.filter_field: parent_id},
                )
            except CatalogValidationError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=exc.message,
                ) from exc

    else:

        def list_items(
            q: str | None = Query(
                default=None,
                description="Búsqueda parcial, sin distinguir mayúsculas/minúsculas",
            ),
            skip: int = Query(default=0, ge=0),
            limit: int = Query(default=100, ge=1, le=500),
            db: Session = Depends(get_db),
        ):
            return config.crud.list(
                db,
                skip=skip,
                limit=limit,
                search=q,
            )

    def get_item(item_id: int, db: Session = Depends(get_db)):
        instance = config.crud.get(db, item_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{config.entity_label} no encontrado",
            )
        return instance

    def create_item(payload: create_schema, db: Session = Depends(get_db)):
        try:
            return config.crud.create(db, payload)
        except CatalogValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=exc.message,
            ) from exc
        except CatalogIntegrityError as exc:
            raise _http_409(exc) from exc

    def replace_item(
        item_id: int,
        payload: create_schema,
        db: Session = Depends(get_db),
    ):
        instance = config.crud.get(db, item_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{config.entity_label} no encontrado",
            )
        try:
            return config.crud.replace(db, instance, payload)
        except CatalogValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=exc.message,
            ) from exc
        except CatalogIntegrityError as exc:
            raise _http_409(exc) from exc

    def patch_item(
        item_id: int,
        payload: update_schema,
        db: Session = Depends(get_db),
    ):
        instance = config.crud.get(db, item_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{config.entity_label} no encontrado",
            )
        try:
            return config.crud.update(db, instance, payload)
        except CatalogValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=exc.message,
            ) from exc
        except CatalogIntegrityError as exc:
            raise _http_409(exc) from exc

    def delete_item(item_id: int, db: Session = Depends(get_db)) -> Response:
        instance = config.crud.get(db, item_id)
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{config.entity_label} no encontrado",
            )
        try:
            config.crud.delete(db, instance)
        except CatalogIntegrityError as exc:
            raise _http_409(exc) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # Nombres únicos evitan colisiones de operation_id en OpenAPI.
    op_prefix = config.path.replace("-", "_")

    router.add_api_route(
        path,
        list_items,
        methods=["GET"],
        response_model=list[read_schema],
        tags=[config.tag],
        summary=f"Listar {config.entity_label}",
        name=f"listar_{op_prefix}",
        operation_id=f"listar_{op_prefix}",
    )
    router.add_api_route(
        item_path,
        get_item,
        methods=["GET"],
        response_model=read_schema,
        tags=[config.tag],
        summary=f"Obtener {config.entity_label} por ID",
        name=f"obtener_{op_prefix}",
        operation_id=f"obtener_{op_prefix}",
    )
    router.add_api_route(
        path,
        create_item,
        methods=["POST"],
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        tags=[config.tag],
        summary=f"Crear {config.entity_label}",
        name=f"crear_{op_prefix}",
        operation_id=f"crear_{op_prefix}",
    )
    router.add_api_route(
        item_path,
        replace_item,
        methods=["PUT"],
        response_model=read_schema,
        tags=[config.tag],
        summary=f"Reemplazar {config.entity_label}",
        name=f"reemplazar_{op_prefix}",
        operation_id=f"reemplazar_{op_prefix}",
    )
    router.add_api_route(
        item_path,
        patch_item,
        methods=["PATCH"],
        response_model=read_schema,
        tags=[config.tag],
        summary=f"Editar parcialmente {config.entity_label}",
        name=f"editar_{op_prefix}",
        operation_id=f"editar_{op_prefix}",
    )
    router.add_api_route(
        item_path,
        delete_item,
        methods=["DELETE"],
        status_code=status.HTTP_204_NO_CONTENT,
        tags=[config.tag],
        summary=f"Eliminar {config.entity_label}",
        name=f"eliminar_{op_prefix}",
        operation_id=f"eliminar_{op_prefix}",
    )


# ==========================================================
# REPOSITORIES / CRUD POR CATÁLOGO
# ==========================================================

pais_crud = CatalogCRUD(
    models.Pais,
    id_field="pais_id",
    search_fields=("pais_nombre",),
    required_fields=("pais_nombre",),
)
region_crud = CatalogCRUD(
    models.Region,
    id_field="reg_id",
    search_fields=("reg_nombre",),
    allowed_filter_fields=("reg_pais_id",),
    required_fields=("reg_nombre",),
)
comuna_crud = CatalogCRUD(
    models.Comuna,
    id_field="com_id",
    search_fields=("com_nombre",),
    allowed_filter_fields=("com_region_id",),
    required_fields=("com_nombre",),
)

tipo_institucion_crud = CatalogCRUD(
    models.TipoInstitucion,
    id_field="tint_id",
    search_fields=("tint_tipo_institucion",),
    required_fields=("tint_tipo_institucion",),
)
institucion_crud = CatalogCRUD(
    models.Institucion,
    id_field="inst_id",
    search_fields=("inst_nombre",),
    allowed_filter_fields=("inst_tipo_institucion_id",),
    required_fields=("inst_nombre",),
)
carrera_crud = CatalogCRUD(
    models.Carrera,
    id_field="crra_id",
    search_fields=("crra_nombre",),
    required_fields=("crra_nombre",),
)
nivel_educacional_crud = CatalogCRUD(
    models.NivelEducacional,
    id_field="nved_id",
    search_fields=("nved_nombre",),
    required_fields=("nved_nombre",),
)

habilidad_crud = CatalogCRUD(
    models.Habilidad,
    id_field="hab_id",
    search_fields=("hab_nombre", "hab_descripcion"),
    required_fields=("hab_nombre",),
)
nivel_habilidad_crud = CatalogCRUD(
    models.NivelHabilidad,
    id_field="nvhb_id",
    search_fields=("nvhb_nombre", "nvhb_descripcion"),
    required_fields=("nvhb_nombre",),
)
cargo_crud = CatalogCRUD(
    models.Cargo,
    id_field="crgo_id",
    search_fields=("crgo_nombre", "crgo_descripcion"),
    required_fields=("crgo_nombre",),
)
modalidad_crud = CatalogCRUD(
    models.Modalidad,
    id_field="mdld_id",
    search_fields=("mdld_nombre", "mdld_descripcion"),
    required_fields=("mdld_nombre",),
)
tipo_contrato_crud = CatalogCRUD(
    models.TipoContrato,
    id_field="tpct_id",
    search_fields=("tpct_nombre", "tpct_descripcion"),
    required_fields=("tpct_nombre",),
)
disponibilidad_crud = CatalogCRUD(
    models.Disponibilidad,
    id_field="disp_id",
    search_fields=("disp_nombre",),
    required_fields=("disp_nombre",),
)

estado_solicitud_crud = CatalogCRUD(
    models.EstadoSolicitud,
    id_field="essl_id",
    search_fields=("essl_nombre", "essl_descripcion"),
    required_fields=("essl_nombre",),
)
prioridad_solicitud_crud = CatalogCRUD(
    models.PrioridadSolicitud,
    id_field="prsol_id",
    search_fields=("prsol_nombre", "prsol_descripcion"),
    required_fields=("prsol_nombre",),
)
estado_solicitud_candidato_crud = CatalogCRUD(
    models.EstadoSolicitudCandidato,
    id_field="essc_id",
    search_fields=("essc_nombre", "essc_descripcion"),
    required_fields=("essc_nombre",),
)
motivo_rechazo_crud = CatalogCRUD(
    models.MotivoRechazo,
    id_field="mtrc_id",
    search_fields=("mtrc_nombre", "mtrc_descripcion"),
    required_fields=("mtrc_nombre",),
)
estado_cuestionario_candidato_crud = CatalogCRUD(
    models.EstadoCuestionarioCandidato,
    id_field="escc_id",
    search_fields=("escc_nombre",),
    required_fields=("escc_nombre",),
)
estado_entrevista_crud = CatalogCRUD(
    models.EstadoEntrevista,
    id_field="esev_id",
    search_fields=("esev_nombre", "esev_descripcion"),
    required_fields=("esev_nombre",),
)
tipo_entrevista_crud = CatalogCRUD(
    models.TipoEntrevista,
    id_field="tpet_id",
    search_fields=("tpet_nombre", "tpet_descripcion"),
    required_fields=("tpet_nombre",),
)
nombre_resultado_crud = CatalogCRUD(
    models.NombreResultado,
    id_field="nore_id",
    search_fields=("nore_nombre",),
    required_fields=("nore_nombre",),
)


# ==========================================================
# REGISTRO DE RUTAS
# ==========================================================

CATALOGS = (
    # Geografía
    CatalogRouteConfig(
        "paises", "Catálogo - Países", "país", pais_crud,
        schemas.PaisRead, schemas.PaisCreate, schemas.PaisUpdate,
    ),
    CatalogRouteConfig(
        "regiones", "Catálogo - Regiones", "región", region_crud,
        schemas.RegionRead, schemas.RegionCreate, schemas.RegionUpdate,
        filter_field="reg_pais_id", filter_query_param="pais_id",
    ),
    CatalogRouteConfig(
        "comunas","Catálogo - Comunas", "comuna", comuna_crud,
        schemas.ComunaRead, schemas.ComunaCreate, schemas.ComunaUpdate,
        filter_field="com_region_id", filter_query_param="region_id",
    ),

    # Educación e instituciones
    CatalogRouteConfig(
        "tipos-institucion", "Catálogo - Tipos de Institución", "tipo de institución",
        tipo_institucion_crud,
        schemas.TipoInstitucionRead, schemas.TipoInstitucionCreate,
        schemas.TipoInstitucionUpdate,
    ),
    CatalogRouteConfig(
        "instituciones", "Catálogo - Instituciones", "institución", institucion_crud,
        schemas.InstitucionRead, schemas.InstitucionCreate, schemas.InstitucionUpdate,
        filter_field="inst_tipo_institucion_id", filter_query_param="tipo_institucion_id",
    ),
    CatalogRouteConfig(
        "carreras", "Catálogo - Carreras", "carrera", carrera_crud,
        schemas.CarreraRead, schemas.CarreraCreate, schemas.CarreraUpdate,
    ),
    CatalogRouteConfig(
        "niveles-educacionales", "Catálogo - Niveles Educacionales", "nivel educacional",
        nivel_educacional_crud,
        schemas.NivelEducacionalRead, schemas.NivelEducacionalCreate,
        schemas.NivelEducacionalUpdate,
    ),

    # Puesto y experiencia
    CatalogRouteConfig(
        "habilidades", "Catálogo - Habilidades", "habilidad", habilidad_crud,
        schemas.HabilidadRead, schemas.HabilidadCreate, schemas.HabilidadUpdate,
    ),
    CatalogRouteConfig(
        "niveles-habilidad", "Catálogo - Niveles de Habilidad", "nivel de habilidad",
        nivel_habilidad_crud,
        schemas.NivelHabilidadRead, schemas.NivelHabilidadCreate,
        schemas.NivelHabilidadUpdate,
    ),
    CatalogRouteConfig(
        "cargos", "Catálogo - Cargos", "cargo", cargo_crud,
        schemas.CargoRead, schemas.CargoCreate, schemas.CargoUpdate,
    ),
    CatalogRouteConfig(
        "modalidades", "Catálogo - Modalidades", "modalidad", modalidad_crud,
        schemas.ModalidadRead, schemas.ModalidadCreate, schemas.ModalidadUpdate,
    ),
    CatalogRouteConfig(
        "tipos-contrato", "Catálogo - Tipos de Contrato", "tipo de contrato",
        tipo_contrato_crud,
        schemas.TipoContratoRead, schemas.TipoContratoCreate,
        schemas.TipoContratoUpdate,
    ),
    CatalogRouteConfig(
        "disponibilidades", "Catálogo - Disponibilidades", "disponibilidad",
        disponibilidad_crud,
        schemas.DisponibilidadRead, schemas.DisponibilidadCreate,
        schemas.DisponibilidadUpdate,
    ),

    # Reclutamiento y estados
    CatalogRouteConfig(
        "estados-solicitud", "Catálogo - Estados de Solicitud", "estado de solicitud",
        estado_solicitud_crud,
        schemas.EstadoSolicitudRead, schemas.EstadoSolicitudCreate,
        schemas.EstadoSolicitudUpdate,
    ),
    CatalogRouteConfig(
        "prioridades-solicitud", "Catálogo - Prioridades de Solicitud", "prioridad de solicitud",
        prioridad_solicitud_crud,
        schemas.PrioridadSolicitudRead, schemas.PrioridadSolicitudCreate,
        schemas.PrioridadSolicitudUpdate, 
    ),
    CatalogRouteConfig(
        "estados-solicitud-candidato", "Catálogo - Estados de Postulación",
        "estado de solicitud de candidato", estado_solicitud_candidato_crud,
        schemas.EstadoSolicitudCandidatoRead, schemas.EstadoSolicitudCandidatoCreate,
        schemas.EstadoSolicitudCandidatoUpdate,
    ),
    CatalogRouteConfig(
        "motivos-rechazo", "Catálogo - Motivos de Rechazo", "motivo de rechazo",
        motivo_rechazo_crud,
        schemas.MotivoRechazoRead, schemas.MotivoRechazoCreate,
        schemas.MotivoRechazoUpdate,
    ),
    CatalogRouteConfig(
        "estados-cuestionario-candidato", "Catálogo - Estados de Cuestionario",
        "estado de cuestionario de candidato", estado_cuestionario_candidato_crud,
        schemas.EstadoCuestionarioCandidatoRead,
        schemas.EstadoCuestionarioCandidatoCreate,
        schemas.EstadoCuestionarioCandidatoUpdate,
    ),
    CatalogRouteConfig(
        "estados-entrevista", "Catálogo - Estados de Entrevista", "estado de entrevista",
        estado_entrevista_crud,
        schemas.EstadoEntrevistaRead, schemas.EstadoEntrevistaCreate,
        schemas.EstadoEntrevistaUpdate,
    ),
    CatalogRouteConfig(
        "tipos-entrevista", "Catálogo - Tipos de Entrevista", "tipo de entrevista",
        tipo_entrevista_crud,
        schemas.TipoEntrevistaRead, schemas.TipoEntrevistaCreate,
        schemas.TipoEntrevistaUpdate,
    ),
    CatalogRouteConfig(
        "nombres-resultado", "Catálogo - Resultados de Evaluación", "resultado",
        nombre_resultado_crud,
        schemas.NombreResultadoRead, schemas.NombreResultadoCreate,
        schemas.NombreResultadoUpdate,
    ),
)

for catalog_config in CATALOGS:
    _register_catalog_routes(catalog_config)
