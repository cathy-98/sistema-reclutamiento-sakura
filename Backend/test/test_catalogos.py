from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.catalogos import models
from app.catalogos.router import router as catalogos_router
from app.database import Base, get_db


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


CATALOG_TABLES = [
    models.Pais.__table__,
    models.Region.__table__,
    models.Comuna.__table__,
    models.TipoInstitucion.__table__,
    models.Institucion.__table__,
    models.Carrera.__table__,
    models.NivelEducacional.__table__,
    models.Habilidad.__table__,
    models.NivelHabilidad.__table__,
    models.Cargo.__table__,
    models.Modalidad.__table__,
    models.TipoContrato.__table__,
    models.Disponibilidad.__table__,
    models.EstadoSolicitud.__table__,
    models.PrioridadSolicitud.__table__,
    models.EstadoSolicitudCandidato.__table__,
    models.MotivoRechazo.__table__,
    models.EstadoCuestionarioCandidato.__table__,
    models.EstadoEntrevista.__table__,
    models.TipoEntrevista.__table__,
    models.NombreResultado.__table__,
]


test_app = FastAPI(title="Sakura - QA Catálogos")
test_app.include_router(catalogos_router)


def override_get_db():
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


test_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine, tables=CATALOG_TABLES)
    Base.metadata.create_all(bind=engine, tables=CATALOG_TABLES)
    yield
    Base.metadata.drop_all(bind=engine, tables=CATALOG_TABLES)


@dataclass(frozen=True)
class DependencyDefinition:
    resource: str
    id_field: str
    export_as: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class CatalogTestCase:
    resource: str
    id_field: str
    create_payload: dict[str, Any]
    put_payload: dict[str, Any]
    patch_payload: dict[str, Any]
    dependencies: tuple[DependencyDefinition, ...] = field(default_factory=tuple)
    filter_param: str | None = None
    filter_context_key: str | None = None


def resolve_payload(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str) and value.startswith("$"):
            context_key = value[1:]
            if context_key not in context:
                raise AssertionError(f"Variable de contexto '{context_key}' no disponible")
            result[key] = context[context_key]
        else:
            result[key] = value
    return result


def create_dependencies(
    client: TestClient,
    dependencies: tuple[DependencyDefinition, ...],
) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for dependency in dependencies:
        payload = resolve_payload(dependency.payload, context)
        response = client.post(f"/catalogos/{dependency.resource}", json=payload)
        assert response.status_code == 201, (
            f"Error creando dependencia {dependency.resource}: "
            f"{response.status_code} {response.text}"
        )
        body = response.json()
        assert dependency.id_field in body
        context[dependency.export_as] = body[dependency.id_field]
    return context


def assert_payload_fields(body: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, expected_value in expected.items():
        assert key in body, f"Campo '{key}' no retornado"
        assert body[key] == expected_value, (
            f"Campo '{key}': esperado={expected_value!r}, obtenido={body[key]!r}"
        )


PAIS_DEP = DependencyDefinition(
    resource="paises",
    id_field="pais_id",
    export_as="pais_id",
    payload={"pais_nombre": "QA País Padre"},
)

REGION_DEP = DependencyDefinition(
    resource="regiones",
    id_field="reg_id",
    export_as="region_id",
    payload={"reg_pais_id": "$pais_id", "reg_nombre": "QA Región Padre"},
)

TIPO_INST_DEP = DependencyDefinition(
    resource="tipos-institucion",
    id_field="tint_id",
    export_as="tipo_institucion_id",
    payload={"tint_tipo_institucion": "QA Tipo Institución"},
)


CASES = [
    CatalogTestCase("paises", "pais_id", {"pais_nombre": "QA País"}, {"pais_nombre": "QA País PUT"}, {"pais_nombre": "QA País PATCH"}),
    CatalogTestCase("regiones", "reg_id", {"reg_pais_id": "$pais_id", "reg_nombre": "QA Región"}, {"reg_pais_id": "$pais_id", "reg_nombre": "QA Región PUT"}, {"reg_nombre": "QA Región PATCH"}, (PAIS_DEP,), "pais_id", "pais_id"),
    CatalogTestCase("comunas", "com_id", {"com_region_id": "$region_id", "com_nombre": "QA Comuna"}, {"com_region_id": "$region_id", "com_nombre": "QA Comuna PUT"}, {"com_nombre": "QA Comuna PATCH"}, (PAIS_DEP, REGION_DEP), "region_id", "region_id"),
    CatalogTestCase("tipos-institucion", "tint_id", {"tint_tipo_institucion": "QA Instituto"}, {"tint_tipo_institucion": "QA Universidad"}, {"tint_tipo_institucion": "QA Centro"}),
    CatalogTestCase("instituciones", "inst_id", {"inst_nombre": "QA Instituto", "inst_tipo_institucion_id": "$tipo_institucion_id"}, {"inst_nombre": "QA Inst PUT", "inst_tipo_institucion_id": "$tipo_institucion_id"}, {"inst_nombre": "QA Inst PATCH"}, (TIPO_INST_DEP,), "tipo_institucion_id", "tipo_institucion_id"),
    CatalogTestCase("carreras", "crra_id", {"crra_nombre": "QA Ingeniería Software"}, {"crra_nombre": "QA Ingeniería Informática"}, {"crra_nombre": "QA Ingeniería PATCH"}),
    CatalogTestCase("niveles-educacionales", "nved_id", {"nved_nombre": "QA Profesional"}, {"nved_nombre": "QA Magíster"}, {"nved_nombre": "QA Doctorado"}),
    CatalogTestCase("habilidades", "hab_id", {"hab_nombre": "QA Python", "hab_descripcion": "Habilidad prueba Python"}, {"hab_nombre": "QA FastAPI", "hab_descripcion": "Actualización PUT"}, {"hab_descripcion": "Actualización PATCH"}),
    CatalogTestCase("niveles-habilidad", "nvhb_id", {"nvhb_nombre": "QA Junior", "nvhb_descripcion": "Nivel QA inicial", "nvhb_puntaje_base": 20, "nvhb_duracion": 12}, {"nvhb_nombre": "QA Senior", "nvhb_descripcion": "Nivel actualizado", "nvhb_puntaje_base": 80, "nvhb_duracion": 60}, {"nvhb_puntaje_base": 90}),
    CatalogTestCase("cargos", "crgo_id", {"crgo_nombre": "QA Developer", "crgo_descripcion": "Cargo de prueba"}, {"crgo_nombre": "QA Backend", "crgo_descripcion": "Cargo PUT"}, {"crgo_descripcion": "Cargo PATCH"}),
    CatalogTestCase("modalidades", "mdld_id", {"mdld_nombre": "QA Remoto", "mdld_descripcion": "Modalidad QA"}, {"mdld_nombre": "QA Híbrido", "mdld_descripcion": "Modalidad PUT"}, {"mdld_descripcion": "Modalidad PATCH"}),
    CatalogTestCase("tipos-contrato", "tpct_id", {"tpct_nombre": "QA Plazo", "tpct_descripcion": "Contrato QA"}, {"tpct_nombre": "QA Indefinido", "tpct_descripcion": "Contrato PUT"}, {"tpct_descripcion": "Contrato PATCH"}),
    CatalogTestCase("disponibilidades", "disp_id", {"disp_nombre": "QA Inmediata"}, {"disp_nombre": "QA 30 días"}, {"disp_nombre": "QA 15 días"}),
    CatalogTestCase("estados-solicitud", "essl_id", {"essl_nombre": "QA Abierta", "essl_descripcion": "Estado inicial QA"}, {"essl_nombre": "QA Cerrada", "essl_descripcion": "Estado PUT"}, {"essl_descripcion": "Estado PATCH"}),
    CatalogTestCase("prioridades-solicitud", "prsol_id", {"prsol_nombre": "QA Alta", "prsol_descripcion": "Prioridad QA"}, {"prsol_nombre": "QA Media", "prsol_descripcion": "Prioridad PUT"}, {"prsol_descripcion": "Prioridad PATCH"}),
    CatalogTestCase("estados-solicitud-candidato", "essc_id", {"essc_nombre": "QA Postulado", "essc_descripcion": "Estado candidato QA"}, {"essc_nombre": "QA Evaluando", "essc_descripcion": "Estado candidato PUT"}, {"essc_descripcion": "Estado candidato PATCH"}),
    CatalogTestCase("motivos-rechazo", "mtrc_id", {"mtrc_nombre": "QA Experiencia", "mtrc_descripcion": "Motivo de prueba"}, {"mtrc_nombre": "QA Técnico", "mtrc_descripcion": "Motivo PUT"}, {"mtrc_descripcion": "Motivo PATCH"}),
    CatalogTestCase("estados-cuestionario-candidato", "escc_id", {"escc_nombre": "QA Pendiente"}, {"escc_nombre": "QA Respondido"}, {"escc_nombre": "QA Evaluado"}),
    CatalogTestCase("estados-entrevista", "esev_id", {"esev_nombre": "QA Agendada", "esev_descripcion": "Entrevista QA"}, {"esev_nombre": "QA Realizada", "esev_descripcion": "Entrevista PUT"}, {"esev_descripcion": "Entrevista PATCH"}),
    CatalogTestCase("tipos-entrevista", "tpet_id", {"tpet_nombre": "QA Técnica", "tpet_descripcion": "Tipo entrevista QA"}, {"tpet_nombre": "QA RRHH", "tpet_descripcion": "Tipo entrevista PUT"}, {"tpet_descripcion": "Tipo entrevista PATCH"}),
    CatalogTestCase("nombres-resultado", "nore_id", {"nore_nombre": "QA Aprobado"}, {"nore_nombre": "QA Observado"}, {"nore_nombre": "QA Revisión"}),
]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.resource)
def test_catalogo_crud_completo(client: TestClient, case: CatalogTestCase):
    context = create_dependencies(client, case.dependencies)

    # 1. POST
    create_payload = resolve_payload(case.create_payload, context)
    response = client.post(f"/catalogos/{case.resource}", json=create_payload)
    assert response.status_code == 201, response.text
    created = response.json()
    assert case.id_field in created
    item_id = created[case.id_field]
    assert isinstance(item_id, int)
    assert_payload_fields(created, create_payload)

    # 2. GET lista
    response = client.get(f"/catalogos/{case.resource}")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert any(item.get(case.id_field) == item_id for item in items)

    # 3. GET por ID
    response = client.get(f"/catalogos/{case.resource}/{item_id}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched[case.id_field] == item_id
    assert_payload_fields(fetched, create_payload)

    # 3B. Filtro jerárquico
    if case.filter_param and case.filter_context_key:
        parent_id = context[case.filter_context_key]
        response = client.get(
            f"/catalogos/{case.resource}",
            params={case.filter_param: parent_id},
        )
        assert response.status_code == 200
        assert any(item.get(case.id_field) == item_id for item in response.json())

    # 4. PUT
    put_payload = resolve_payload(case.put_payload, context)
    response = client.put(
        f"/catalogos/{case.resource}/{item_id}",
        json=put_payload,
    )
    assert response.status_code == 200, response.text
    assert response.json()[case.id_field] == item_id
    assert_payload_fields(response.json(), put_payload)

    # 5. PATCH
    patch_payload = resolve_payload(case.patch_payload, context)
    response = client.patch(
        f"/catalogos/{case.resource}/{item_id}",
        json=patch_payload,
    )
    assert response.status_code == 200, response.text
    assert response.json()[case.id_field] == item_id
    assert_payload_fields(response.json(), patch_payload)

    # 6. DELETE
    response = client.delete(f"/catalogos/{case.resource}/{item_id}")
    assert response.status_code == 204
    assert response.content == b""

    # 7. GET post eliminación
    response = client.get(f"/catalogos/{case.resource}/{item_id}")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_id_inexistente_retorna_404(client: TestClient):
    response = client.get("/catalogos/paises/999999")
    assert response.status_code == 404


def test_patch_vacio_retorna_422(client: TestClient):
    create_response = client.post(
        "/catalogos/paises",
        json={"pais_nombre": "QA PATCH vacío"},
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["pais_id"]

    response = client.patch(f"/catalogos/paises/{item_id}", json={})
    assert response.status_code == 422


def test_registro_duplicado_retorna_409(client: TestClient):
    payload = {"pais_nombre": "QA País Duplicado"}
    assert client.post("/catalogos/paises", json=payload).status_code == 201
    assert client.post("/catalogos/paises", json=payload).status_code == 409


def test_filtro_region_por_pais(client: TestClient):
    pais_response = client.post(
        "/catalogos/paises",
        json={"pais_nombre": "QA Chile"},
    )
    assert pais_response.status_code == 201
    pais_id = pais_response.json()["pais_id"]

    region_response = client.post(
        "/catalogos/regiones",
        json={"reg_pais_id": pais_id, "reg_nombre": "QA Metropolitana"},
    )
    assert region_response.status_code == 201
    reg_id = region_response.json()["reg_id"]

    response = client.get("/catalogos/regiones", params={"pais_id": pais_id})
    assert response.status_code == 200
    assert any(item["reg_id"] == reg_id for item in response.json())
