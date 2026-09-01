from __future__ import annotations

import os
from datetime import datetime
from typing import Iterator

# Configuración JWT previa a imports de auth.
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "qa-modulo2-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ACTIVE_USER_STATUS_NAME", "Activo")
os.environ.setdefault("ADMIN_ROLE_NAME", "Administrador")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import utils as auth_utils
from app.catalogos import models as catalog_models
from app.clientes import models as cliente_models
from app.clientes import router as clientes_router
from app.database import Base, get_db
from app.solicitudes import models as solicitud_models
from app.solicitudes import router as solicitudes_router
from app.usuarios import models as user_models
from app.auth import models as auth_models


# =============================================================================
# BASE AISLADA EN MEMORIA
# =============================================================================
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(TEST_ENGINE, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)


MODULE2_TABLES = [
    user_models.Area.__table__,
    user_models.Permiso.__table__,
    user_models.Rol.__table__,
    user_models.RolPermiso.__table__,
    user_models.EstadoUsuario.__table__,
    user_models.Usuario.__table__,
    catalog_models.Cargo.__table__,
    catalog_models.Modalidad.__table__,
    catalog_models.TipoContrato.__table__,
    catalog_models.CategoriaHabilidad.__table__,
    catalog_models.Habilidad.__table__,
    catalog_models.NivelHabilidad.__table__,
    catalog_models.EstadoSolicitud.__table__,
    catalog_models.PrioridadSolicitud.__table__,
    cliente_models.Empresa.__table__,
    cliente_models.Cliente.__table__,
    solicitud_models.Solicitud.__table__,
    solicitud_models.SolicitudHabilidad.__table__,
    solicitud_models.HistorialSolicitud.__table__,
        # Recuperación de contraseña
    auth_models.PasswordResetToken.__table__,
]


app_test = FastAPI(title="QA Módulo 2")
app_test.include_router(clientes_router.router)
app_test.include_router(solicitudes_router.router)


def override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app_test.dependency_overrides[get_db] = override_get_db


PERMISSIONS = [
    "CAT_ADMIN",
    "SOL_CREATE",
    "SOL_VIEW",
    "SOL_UPDATE",
    "SOL_DELETE",
]


class SeedInfo(dict):
    pass


def _make_user(
    db: Session,
    *,
    role: user_models.Rol,
    state: user_models.EstadoUsuario,
    area: user_models.Area,
    seq: int,
    email: str,
) -> user_models.Usuario:
    user = user_models.Usuario(
        usr_rol_id=role.rol_id,
        usr_estado_usuario_id=state.esusr_id,
        usr_area_id=area.area_id,
        usr_nombres=f"QA{seq}",
        usr_apellido_paterno="ModuloDos",
        usr_apellido_materno=None,
        usr_rut_sin_dv=f"200000{seq:02d}",
        usr_dv=str(seq % 10),
        usr_telefono=f"900000{seq:03d}",
        usr_email=email,
        usr_contrasena=auth_utils.hash_password("PasswordQA123!"),
    )
    db.add(user)
    db.flush()
    return user


def _seed_database() -> SeedInfo:
    db = TestingSessionLocal()
    try:
        activo = user_models.EstadoUsuario(esusr_nombre="Activo", esusr_descripcion="Activo")
        inactivo = user_models.EstadoUsuario(esusr_nombre="Inactivo", esusr_descripcion="Inactivo")
        area = user_models.Area(area_nombre="QA M2", area_descripcion="QA Módulo 2")
        db.add_all([activo, inactivo, area])
        db.flush()

        permission_objs = {
            name: user_models.Permiso(per_nombre=name, per_descripcion=f"QA {name}")
            for name in PERMISSIONS
        }
        db.add_all(permission_objs.values())
        db.flush()

        def role(name: str, permissions: list[str]) -> user_models.Rol:
            r = user_models.Rol(
                rol_nombre=name,
                rol_descripcion=f"Rol QA {name}",
                permisos=[permission_objs[p] for p in permissions],
            )
            db.add(r)
            db.flush()
            return r

        admin_role = role("Administrador", PERMISSIONS)
        recruiter_role = role("Reclutador", ["SOL_VIEW", "SOL_UPDATE"])
        cat_role = role("QACatalogos", ["CAT_ADMIN"])
        view_role = role("QAView", ["SOL_VIEW"])
        update_role = role("QAUpdate", ["SOL_UPDATE"])
        delete_role = role("QADelete", ["SOL_DELETE"])
        no_perm_role = role("QANoPerm", [])

        admin = _make_user(
            db, role=admin_role, state=activo, area=area, seq=1,
            email="admin.m2@sakura.cl",
        )
        recruiter = _make_user(
            db, role=recruiter_role, state=activo, area=area, seq=2,
            email="recruiter.m2@sakura.cl",
        )
        inactive_recruiter = _make_user(
            db, role=recruiter_role, state=inactivo, area=area, seq=3,
            email="inactive.recruiter.m2@sakura.cl",
        )
        cat_user = _make_user(
            db, role=cat_role, state=activo, area=area, seq=4,
            email="catalog.m2@sakura.cl",
        )
        view_user = _make_user(
            db, role=view_role, state=activo, area=area, seq=5,
            email="view.m2@sakura.cl",
        )
        update_user = _make_user(
            db, role=update_role, state=activo, area=area, seq=6,
            email="update.m2@sakura.cl",
        )
        delete_user = _make_user(
            db, role=delete_role, state=activo, area=area, seq=7,
            email="delete.m2@sakura.cl",
        )
        no_perm_user = _make_user(
            db, role=no_perm_role, state=activo, area=area, seq=8,
            email="noperm.m2@sakura.cl",
        )

        cargo = catalog_models.Cargo(crgo_nombre="Backend QA", crgo_descripcion="Cargo QA")
        modalidad = catalog_models.Modalidad(mdld_nombre="Remoto", mdld_descripcion="Remoto QA")
        contrato = catalog_models.TipoContrato(tpct_nombre="Indefinido", tpct_descripcion="Contrato QA")
        prioridad = catalog_models.PrioridadSolicitud(prsol_nombre="Alta", prsol_descripcion="Prioridad QA")
        habilidad1 = catalog_models.Habilidad(hab_nombre="Python QA", hab_descripcion="Python")
        habilidad2 = catalog_models.Habilidad(hab_nombre="FastAPI QA", hab_descripcion="FastAPI")
        habilidad3 = catalog_models.Habilidad(hab_nombre="Docker QA", hab_descripcion="Docker")
        nivel = catalog_models.NivelHabilidad(
            nvhb_nombre="Avanzado", nvhb_descripcion="Avanzado QA", nvhb_puntaje_base=10, nvhb_duracion=1
        )
        db.add_all([cargo, modalidad, contrato, prioridad, habilidad1, habilidad2, habilidad3, nivel])

        estados = {}
        for name in ["Pendiente", "En Publicacion", "En Entrevistas", "Cancelado", "Cerrado", "Pausado"]:
            obj = catalog_models.EstadoSolicitud(essl_nombre=name, essl_descripcion=f"Estado {name}")
            db.add(obj)
            db.flush()
            estados[name] = obj.essl_id

        empresa = cliente_models.Empresa(emp_nombre="Empresa QA Base", emp_identificacion="QA-BASE-001")
        db.add(empresa)
        db.flush()
        cliente = cliente_models.Cliente(
            cli_nombre="Cliente QA Base",
            cli_empresa_id=empresa.emp_id,
            cli_cargo_empresa_id=cargo.crgo_id,
            cli_area_empresa_id=area.area_id,
            cli_email="cliente.base@sakura.cl",
            cli_telefono1="911111111",
        )
        db.add(cliente)
        db.commit()

        return SeedInfo(
            admin_id=admin.usr_id,
            recruiter_id=recruiter.usr_id,
            inactive_recruiter_id=inactive_recruiter.usr_id,
            cat_user_id=cat_user.usr_id,
            view_user_id=view_user.usr_id,
            update_user_id=update_user.usr_id,
            delete_user_id=delete_user.usr_id,
            no_perm_user_id=no_perm_user.usr_id,
            area_id=area.area_id,
            cargo_id=cargo.crgo_id,
            modalidad_id=modalidad.mdld_id,
            contrato_id=contrato.tpct_id,
            prioridad_id=prioridad.prsol_id,
            habilidad1_id=habilidad1.hab_id,
            habilidad2_id=habilidad2.hab_id,
            habilidad3_id=habilidad3.hab_id,
            nivel_id=nivel.nvhb_id,
            empresa_id=empresa.emp_id,
            cliente_id=cliente.cli_id,
            estados=estados,
        )
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=TEST_ENGINE, tables=list(reversed(MODULE2_TABLES)))
    Base.metadata.create_all(bind=TEST_ENGINE, tables=MODULE2_TABLES)
    app_test.state.seed_info = _seed_database()
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE, tables=list(reversed(MODULE2_TABLES)))


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app_test) as c:
        yield c


@pytest.fixture
def seed_info() -> SeedInfo:
    return app_test.state.seed_info


def _token(user_id: int) -> str:
    return auth_utils.create_access_token({"sub": str(user_id), "email": "qa@sakura.cl"})


def _headers(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(user_id)}"}


def _empresa_payload(suffix: str = "1") -> dict:
    return {
        "emp_nombre": f"Empresa QA {suffix}",
        "emp_identificacion": f"QA-{suffix}",
    }


def _cliente_payload(seed: SeedInfo, suffix: str = "1", empresa_id: int | None = None) -> dict:
    return {
        "cli_nombre": f"Cliente QA {suffix}",
        "cli_empresa_id": empresa_id or seed["empresa_id"],
        "cli_cargo_empresa_id": seed["cargo_id"],
        "cli_area_empresa_id": seed["area_id"],
        "cli_email": f"cliente.{suffix}@sakura.cl",
        "cli_email2": f"cliente2.{suffix}@sakura.cl",
        "cli_telefono1": f"91234{int(suffix[-3:]) if suffix[-3:].isdigit() else 100:05d}"[:12],
        "cli_telefono2": f"92234{int(suffix[-3:]) if suffix[-3:].isdigit() else 100:05d}"[:12],
    }


def _solicitud_payload(seed: SeedInfo, *, title: str = "Solicitud QA", assigned_id: int | None = None) -> dict:
    return {
        "sol_titulo": title,
        "sol_descripcion": "Solicitud de prueba automatizada",
        "sol_observacion": "Creación QA",
        "sol_cantidad_vacantes": 2,
        "sol_salario_min": 1000,
        "sol_salario_max": 2000,
        "sol_fecha_inicio_busqueda": "2026-08-12T09:00:00",
        "sol_fecha_cierre_busqueda": "2026-08-30T18:00:00",
        "sol_fecha_inicio_cliente": "2026-09-01T09:00:00",
        "sol_hora_inicio_jornada": "09:00:00",
        "sol_hora_fin_jornada": "18:00:00",
        "sol_cargo_id": seed["cargo_id"],
        "sol_prioridad_id": seed["prioridad_id"],
        "sol_cliente_id": seed["cliente_id"],
        "sol_usuario_asignado_id": assigned_id or seed["recruiter_id"],
        "sol_modalidad_id": seed["modalidad_id"],
        "sol_tipo_contrato_id": seed["contrato_id"],
        "habilidades": [
            {
                "solhb_habilidad_id": seed["habilidad1_id"],
                "solhb_nivel_habilidad_id": seed["nivel_id"],
                "solhb_anios_experiencia_req": 2,
                "solhb_es_excluyente": True,
            },
            {
                "solhb_habilidad_id": seed["habilidad2_id"],
                "solhb_nivel_habilidad_id": seed["nivel_id"],
                "solhb_anios_experiencia_req": 1,
                "solhb_es_excluyente": False,
            },
        ],
    }


def _create_request(client: TestClient, seed: SeedInfo, *, title: str = "Solicitud QA") -> dict:
    response = client.post(
        "/solicitudes",
        json=_solicitud_payload(seed, title=title),
        headers=_headers(seed["admin_id"]),
    )
    assert response.status_code == 201, response.text
    return response.json()


# =============================================================================
# SEGURIDAD / RBAC
# =============================================================================

def test_clientes_sin_token_retorna_401(client: TestClient):
    assert client.get("/clientes").status_code == 401


def test_clientes_sin_cat_admin_retorna_403(client: TestClient, seed_info: SeedInfo):
    assert client.get("/clientes", headers=_headers(seed_info["no_perm_user_id"])).status_code == 403


def test_solicitudes_sin_token_retorna_401(client: TestClient):
    assert client.get("/solicitudes").status_code == 401


def test_solicitudes_sin_sol_view_retorna_403(client: TestClient, seed_info: SeedInfo):
    assert client.get("/solicitudes", headers=_headers(seed_info["no_perm_user_id"])).status_code == 403


def test_crear_solicitud_sin_sol_create_retorna_403(client: TestClient, seed_info: SeedInfo):
    response = client.post(
        "/solicitudes",
        json=_solicitud_payload(seed_info),
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 403


# =============================================================================
# EMPRESAS
# =============================================================================

def test_crud_empresa_completo(client: TestClient, seed_info: SeedInfo):
    headers = _headers(seed_info["cat_user_id"])
    create = client.post("/clientes/empresas", json=_empresa_payload("101"), headers=headers)
    assert create.status_code == 201, create.text
    empresa_id = create.json()["emp_id"]

    get_one = client.get(f"/clientes/empresas/{empresa_id}", headers=headers)
    assert get_one.status_code == 200
    assert get_one.json()["emp_nombre"] == "Empresa QA 101"

    put = client.put(
        f"/clientes/empresas/{empresa_id}",
        json={"emp_nombre": "Empresa QA 101 PUT", "emp_identificacion": "QA-101-PUT"},
        headers=headers,
    )
    assert put.status_code == 200
    assert put.json()["emp_nombre"] == "Empresa QA 101 PUT"

    patch = client.patch(
        f"/clientes/empresas/{empresa_id}",
        json={"emp_nombre": "Empresa QA 101 PATCH"},
        headers=headers,
    )
    assert patch.status_code == 200

    listing = client.get("/clientes/empresas", params={"q": "101 PATCH"}, headers=headers)
    assert listing.status_code == 200
    assert any(x["emp_id"] == empresa_id for x in listing.json())

    delete = client.delete(f"/clientes/empresas/{empresa_id}", headers=headers)
    assert delete.status_code == 204
    assert client.get(f"/clientes/empresas/{empresa_id}", headers=headers).status_code == 404


def test_empresa_patch_vacio_422(client: TestClient, seed_info: SeedInfo):
    response = client.patch(
        f"/clientes/empresas/{seed_info['empresa_id']}",
        json={},
        headers=_headers(seed_info["cat_user_id"]),
    )
    assert response.status_code == 422


def test_empresa_duplicada_409(client: TestClient, seed_info: SeedInfo):
    headers = _headers(seed_info["cat_user_id"])
    payload = _empresa_payload("202")
    assert client.post("/clientes/empresas", json=payload, headers=headers).status_code == 201
    assert client.post("/clientes/empresas", json=payload, headers=headers).status_code == 409


def test_empresa_con_clientes_no_se_puede_borrar(client: TestClient, seed_info: SeedInfo):
    response = client.delete(
        f"/clientes/empresas/{seed_info['empresa_id']}",
        headers=_headers(seed_info["cat_user_id"]),
    )
    assert response.status_code == 409


def test_empresa_inexistente_404(client: TestClient, seed_info: SeedInfo):
    assert client.get(
        "/clientes/empresas/999999", headers=_headers(seed_info["cat_user_id"])
    ).status_code == 404


# =============================================================================
# CLIENTES
# =============================================================================

def test_crud_cliente_completo(client: TestClient, seed_info: SeedInfo):
    headers = _headers(seed_info["cat_user_id"])
    create = client.post("/clientes", json=_cliente_payload(seed_info, "301"), headers=headers)
    assert create.status_code == 201, create.text
    cliente_id = create.json()["cli_id"]

    assert client.get(f"/clientes/{cliente_id}", headers=headers).status_code == 200

    put_payload = _cliente_payload(seed_info, "302")
    put_payload["cli_nombre"] = "Cliente QA PUT"
    put = client.put(f"/clientes/{cliente_id}", json=put_payload, headers=headers)
    assert put.status_code == 200, put.text

    patch = client.patch(
        f"/clientes/{cliente_id}", json={"cli_nombre": "Cliente QA PATCH"}, headers=headers
    )
    assert patch.status_code == 200
    assert patch.json()["cli_nombre"] == "Cliente QA PATCH"

    search = client.get("/clientes", params={"q": "PATCH"}, headers=headers)
    assert search.status_code == 200
    assert any(x["cli_id"] == cliente_id for x in search.json())

    delete = client.delete(f"/clientes/{cliente_id}", headers=headers)
    assert delete.status_code == 204
    assert client.get(f"/clientes/{cliente_id}", headers=headers).status_code == 404


def test_cliente_filtra_por_empresa(client: TestClient, seed_info: SeedInfo):
    response = client.get(
        "/clientes",
        params={"empresa_id": seed_info["empresa_id"]},
        headers=_headers(seed_info["cat_user_id"]),
    )
    assert response.status_code == 200
    assert response.json()
    assert all(x["cli_empresa_id"] == seed_info["empresa_id"] for x in response.json())


def test_cliente_empresa_inexistente_422(client: TestClient, seed_info: SeedInfo):
    payload = _cliente_payload(seed_info, "401", empresa_id=999999)
    response = client.post("/clientes", json=payload, headers=_headers(seed_info["cat_user_id"]))
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["cli_cargo_empresa_id", "cli_area_empresa_id"])
def test_cliente_fk_inexistente_422(client: TestClient, seed_info: SeedInfo, field: str):
    payload = _cliente_payload(seed_info, "402")
    payload[field] = 999999
    response = client.post("/clientes", json=payload, headers=_headers(seed_info["cat_user_id"]))
    assert response.status_code == 422


def test_cliente_email_invalido_422(client: TestClient, seed_info: SeedInfo):
    payload = _cliente_payload(seed_info, "403")
    payload["cli_email"] = "correo-invalido"
    response = client.post("/clientes", json=payload, headers=_headers(seed_info["cat_user_id"]))
    assert response.status_code == 422


def test_cliente_emails_iguales_422(client: TestClient, seed_info: SeedInfo):
    payload = _cliente_payload(seed_info, "404")
    payload["cli_email2"] = payload["cli_email"]
    response = client.post("/clientes", json=payload, headers=_headers(seed_info["cat_user_id"]))
    assert response.status_code == 422


def test_cliente_telefonos_iguales_422(client: TestClient, seed_info: SeedInfo):
    payload = _cliente_payload(seed_info, "405")
    payload["cli_telefono2"] = payload["cli_telefono1"]
    response = client.post("/clientes", json=payload, headers=_headers(seed_info["cat_user_id"]))
    assert response.status_code == 422


def test_cliente_email_duplicado_409(client: TestClient, seed_info: SeedInfo):
    headers = _headers(seed_info["cat_user_id"])
    payload1 = _cliente_payload(seed_info, "406")
    payload2 = _cliente_payload(seed_info, "407")
    payload2["cli_email"] = payload1["cli_email"]
    assert client.post("/clientes", json=payload1, headers=headers).status_code == 201
    assert client.post("/clientes", json=payload2, headers=headers).status_code == 409


def test_cliente_patch_vacio_422(client: TestClient, seed_info: SeedInfo):
    response = client.patch(
        f"/clientes/{seed_info['cliente_id']}", json={}, headers=_headers(seed_info["cat_user_id"])
    )
    assert response.status_code == 422


def test_cliente_con_solicitud_no_se_puede_borrar(client: TestClient, seed_info: SeedInfo):
    _create_request(client, seed_info)
    response = client.delete(
        f"/clientes/{seed_info['cliente_id']}", headers=_headers(seed_info["cat_user_id"])
    )
    assert response.status_code == 409


# =============================================================================
# CREACIÓN / VALIDACIONES DE SOLICITUD
# =============================================================================

def test_crear_solicitud_genera_codigo_y_auditoria(client: TestClient, seed_info: SeedInfo):
    result = _create_request(client, seed_info)
    assert result["sol_codigo"] == "SOL-000001"
    assert result["sol_usuario_creador_id"] == seed_info["admin_id"]
    assert result["sol_estado_solicitud_id"] == seed_info["estados"]["Pendiente"]
    assert result["sol_fecha_creacion"] is not None
    assert any(h["solhb_es_excluyente"] is True for h in result["habilidades"])

    history = client.get(
        f"/solicitudes/{result['sol_id']}/historial",
        headers=_headers(seed_info["admin_id"]),
    )
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["hsol_usuario_id"] == seed_info["admin_id"]


def test_codigo_solicitud_incremental(client: TestClient, seed_info: SeedInfo):
    a = _create_request(client, seed_info, title="Solicitud 1")
    b = _create_request(client, seed_info, title="Solicitud 2")
    assert a["sol_codigo"] == "SOL-000001"
    assert b["sol_codigo"] == "SOL-000002"


def test_solicitud_rechaza_campos_controlados_por_backend(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["sol_codigo"] = "SOL-999999"
    payload["sol_usuario_creador_id"] = 999
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_sin_habilidades_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["habilidades"] = []
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_sin_habilidad_excluyente_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    for h in payload["habilidades"]:
        h["solhb_es_excluyente"] = False
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_habilidad_repetida_payload_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["habilidades"][1]["solhb_habilidad_id"] = seed_info["habilidad1_id"]
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    ["sol_cliente_id", "sol_cargo_id", "sol_prioridad_id", "sol_modalidad_id", "sol_tipo_contrato_id"],
)
def test_solicitud_fk_inexistente_422(client: TestClient, seed_info: SeedInfo, field: str):
    payload = _solicitud_payload(seed_info)
    payload[field] = 999999
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_habilidad_inexistente_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["habilidades"][0]["solhb_habilidad_id"] = 999999
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_nivel_habilidad_inexistente_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["habilidades"][0]["solhb_nivel_habilidad_id"] = 999999
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_usuario_asignado_debe_ser_reclutador_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info, assigned_id=seed_info["admin_id"])
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_reclutador_inactivo_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info, assigned_id=seed_info["inactive_recruiter_id"])
    response = client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"]))
    assert response.status_code == 422


def test_solicitud_salario_invalido_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["sol_salario_min"] = 3000
    payload["sol_salario_max"] = 1000
    assert client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"])).status_code == 422


def test_solicitud_horario_invalido_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["sol_hora_inicio_jornada"] = "18:00:00"
    payload["sol_hora_fin_jornada"] = "09:00:00"
    assert client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"])).status_code == 422


def test_solicitud_fechas_invalidas_422(client: TestClient, seed_info: SeedInfo):
    payload = _solicitud_payload(seed_info)
    payload["sol_fecha_inicio_busqueda"] = "2026-09-10T09:00:00"
    payload["sol_fecha_cierre_busqueda"] = "2026-09-01T09:00:00"
    assert client.post("/solicitudes", json=payload, headers=_headers(seed_info["admin_id"])).status_code == 422


# =============================================================================
# CONSULTA / ACTUALIZACIÓN / FILTROS
# =============================================================================

def test_get_solicitud_inexistente_404(client: TestClient, seed_info: SeedInfo):
    assert client.get(
        "/solicitudes/999999", headers=_headers(seed_info["view_user_id"])
    ).status_code == 404


def test_patch_solicitud_vacio_422(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.patch(
        f"/solicitudes/{req['sol_id']}", json={}, headers=_headers(seed_info["update_user_id"])
    )
    assert response.status_code == 422


def test_put_y_patch_solicitud(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    put_payload = _solicitud_payload(seed_info, title="Solicitud PUT")
    put_payload.pop("habilidades")
    put = client.put(
        f"/solicitudes/{req['sol_id']}", json=put_payload, headers=_headers(seed_info["update_user_id"])
    )
    assert put.status_code == 200, put.text
    assert put.json()["sol_titulo"] == "Solicitud PUT"

    patch = client.patch(
        f"/solicitudes/{req['sol_id']}",
        json={"sol_titulo": "Solicitud PATCH"},
        headers=_headers(seed_info["update_user_id"]),
    )
    assert patch.status_code == 200
    assert patch.json()["sol_titulo"] == "Solicitud PATCH"


def test_listado_solicitudes_busqueda_y_filtros(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info, title="Especial Backend QA")
    headers = _headers(seed_info["view_user_id"])

    queries = [
        {"q": "Especial"},
        {"estado_id": seed_info["estados"]["Pendiente"]},
        {"prioridad_id": seed_info["prioridad_id"]},
        {"cargo_id": seed_info["cargo_id"]},
        {"cliente_id": seed_info["cliente_id"]},
        {"usuario_asignado_id": seed_info["recruiter_id"]},
        {"modalidad_id": seed_info["modalidad_id"]},
        {"tipo_contrato_id": seed_info["contrato_id"]},
        {"fecha_desde": "2020-01-01T00:00:00"},
        {"fecha_hasta": "2030-01-01T00:00:00"},
    ]
    for params in queries:
        response = client.get("/solicitudes", params=params, headers=headers)
        assert response.status_code == 200, (params, response.text)
        assert any(x["sol_id"] == req["sol_id"] for x in response.json()), params


def test_paginacion_solicitudes(client: TestClient, seed_info: SeedInfo):
    _create_request(client, seed_info, title="Página 1")
    _create_request(client, seed_info, title="Página 2")
    response = client.get(
        "/solicitudes", params={"skip": 0, "limit": 1}, headers=_headers(seed_info["view_user_id"])
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


# =============================================================================
# HABILIDADES
# =============================================================================

def test_listar_habilidades(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.get(
        f"/solicitudes/{req['sol_id']}/habilidades", headers=_headers(seed_info["view_user_id"])
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_agregar_habilidad(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    payload = [{
        "solhb_habilidad_id": seed_info["habilidad3_id"],
        "solhb_nivel_habilidad_id": seed_info["nivel_id"],
        "solhb_anios_experiencia_req": 1,
        "solhb_es_excluyente": False,
    }]
    response = client.post(
        f"/solicitudes/{req['sol_id']}/habilidades",
        json=payload,
        headers=_headers(seed_info["update_user_id"]),
    )
    assert response.status_code == 201, response.text
    assert len(response.json()) == 3


def test_agregar_habilidad_duplicada_409(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    payload = [{
        "solhb_habilidad_id": seed_info["habilidad1_id"],
        "solhb_nivel_habilidad_id": seed_info["nivel_id"],
        "solhb_anios_experiencia_req": 2,
        "solhb_es_excluyente": True,
    }]
    response = client.post(
        f"/solicitudes/{req['sol_id']}/habilidades",
        json=payload,
        headers=_headers(seed_info["update_user_id"]),
    )
    assert response.status_code == 409


def test_agregar_habilidades_vacio_422(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/habilidades",
        json=[],
        headers=_headers(seed_info["update_user_id"]),
    )
    assert response.status_code == 422


def test_actualizar_habilidad(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.patch(
        f"/solicitudes/{req['sol_id']}/habilidades/{seed_info['habilidad2_id']}",
        json={"solhb_anios_experiencia_req": 5},
        headers=_headers(seed_info["update_user_id"]),
    )
    assert response.status_code == 200
    assert response.json()["solhb_anios_experiencia_req"] == 5


def test_no_se_puede_desmarcar_ultima_excluyente_409(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.patch(
        f"/solicitudes/{req['sol_id']}/habilidades/{seed_info['habilidad1_id']}",
        json={"solhb_es_excluyente": False},
        headers=_headers(seed_info["update_user_id"]),
    )
    assert response.status_code == 409


def test_no_se_puede_eliminar_ultima_excluyente_409(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.delete(
        f"/solicitudes/{req['sol_id']}/habilidades/{seed_info['habilidad1_id']}",
        headers=_headers(seed_info["update_user_id"]),
    )
    assert response.status_code == 409


def test_eliminar_excluyente_si_existe_otra(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    add = client.post(
        f"/solicitudes/{req['sol_id']}/habilidades",
        json=[{
            "solhb_habilidad_id": seed_info["habilidad3_id"],
            "solhb_nivel_habilidad_id": seed_info["nivel_id"],
            "solhb_anios_experiencia_req": 1,
            "solhb_es_excluyente": True,
        }],
        headers=_headers(seed_info["update_user_id"]),
    )
    assert add.status_code == 201
    delete = client.delete(
        f"/solicitudes/{req['sol_id']}/habilidades/{seed_info['habilidad1_id']}",
        headers=_headers(seed_info["update_user_id"]),
    )
    assert delete.status_code == 204


# =============================================================================
# FLUJO DE ESTADOS / AUDITORÍA
# =============================================================================

def _change_state(client: TestClient, seed: SeedInfo, req_id: int, target: str, user_id: int, obs: str | None = None):
    body = {"sol_estado_solicitud_id": seed["estados"][target]}
    if obs is not None:
        body["observacion"] = obs
    return client.patch(
        f"/solicitudes/{req_id}/estado",
        json=body,
        headers=_headers(user_id),
    )


def test_pendiente_a_en_curso(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = _change_state(client, seed_info, req["sol_id"], "En Publicacion", seed_info["update_user_id"])
    assert response.status_code == 200, response.text
    assert response.json()["sol_estado_solicitud_id"] == seed_info["estados"]["En Publicacion"]


def test_transicion_pendiente_a_pausado_no_permitida_409(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = _change_state(client, seed_info, req["sol_id"], "Pausado", seed_info["update_user_id"], "Pausa")
    assert response.status_code == 409


def test_cancelado_requiere_observacion_422(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = _change_state(client, seed_info, req["sol_id"], "Cancelado", seed_info["delete_user_id"])
    assert response.status_code == 422


def test_cancelado_requiere_sol_delete_403(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = _change_state(
        client, seed_info, req["sol_id"], "Cancelado", seed_info["update_user_id"], "Cliente cancela"
    )
    assert response.status_code == 403


def test_pendiente_a_cancelado_con_sol_delete(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = _change_state(
        client, seed_info, req["sol_id"], "Cancelado", seed_info["delete_user_id"], "Cliente cancela"
    )
    assert response.status_code == 200, response.text


def test_en_curso_pausado_y_reanudar(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    assert _change_state(client, seed_info, req["sol_id"], "En Publicacion", seed_info["update_user_id"]).status_code == 200
    no_obs = _change_state(client, seed_info, req["sol_id"], "Pausado", seed_info["update_user_id"])
    assert no_obs.status_code == 422
    paused = _change_state(client, seed_info, req["sol_id"], "Pausado", seed_info["update_user_id"], "Pausa temporal")
    assert paused.status_code == 200
    resumed = _change_state(client, seed_info, req["sol_id"], "En Publicacion", seed_info["update_user_id"])
    assert resumed.status_code == 200


def test_en_entrevistas_a_cerrado_requiere_sol_delete_y_observacion(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    assert _change_state(client, seed_info, req["sol_id"], "En Publicacion", seed_info["update_user_id"]).status_code == 200
    assert _change_state(client, seed_info, req["sol_id"], "En Entrevistas", seed_info["update_user_id"]).status_code == 200

    # Cerrado sigue siendo una transición terminal: requiere SOL_DELETE.
    forbidden = _change_state(
        client, seed_info, req["sol_id"], "Cerrado", seed_info["update_user_id"], "Cierre sin permiso"
    )
    assert forbidden.status_code == 403

    # Nuevo requisito: al igual que Pausado y Cancelado, Cerrado exige observación.
    without_observation = _change_state(
        client, seed_info, req["sol_id"], "Cerrado", seed_info["delete_user_id"]
    )
    assert without_observation.status_code == 422

    observation = "Proceso finalizado; se cierra la solicitud con las vacantes cubiertas."
    closed = _change_state(
        client, seed_info, req["sol_id"], "Cerrado", seed_info["delete_user_id"], observation
    )
    assert closed.status_code == 200, closed.text
    assert closed.json()["sol_estado_solicitud_id"] == seed_info["estados"]["Cerrado"]

    # La observación queda asociada al cambio de estado en el historial existente.
    history = client.get(
        f"/solicitudes/{req['sol_id']}/historial",
        headers=_headers(seed_info["view_user_id"]),
    )
    assert history.status_code == 200
    rows = history.json()
    assert rows[-1]["hsol_estado_actual_id"] == seed_info["estados"]["Cerrado"]
    assert rows[-1]["hsol_usuario_id"] == seed_info["delete_user_id"]
    assert rows[-1]["hsol_comentario"] == observation


def test_estado_terminal_no_permite_transiciones(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    assert _change_state(
        client, seed_info, req["sol_id"], "Cancelado", seed_info["delete_user_id"], "Fin"
    ).status_code == 200
    response = _change_state(client, seed_info, req["sol_id"], "En Publicacion", seed_info["update_user_id"])
    assert response.status_code == 409


def test_historial_registra_usuario_y_observacion(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    assert _change_state(client, seed_info, req["sol_id"], "En Publicacion", seed_info["update_user_id"]).status_code == 200
    assert _change_state(
        client, seed_info, req["sol_id"], "Pausado", seed_info["update_user_id"], "Cliente pidió pausa"
    ).status_code == 200

    history = client.get(
        f"/solicitudes/{req['sol_id']}/historial", headers=_headers(seed_info["view_user_id"])
    )
    assert history.status_code == 200
    rows = history.json()
    assert len(rows) == 3
    assert rows[-1]["hsol_usuario_id"] == seed_info["update_user_id"]
    assert rows[-1]["hsol_comentario"] == "Cliente pidió pausa"


# =============================================================================
# EVALUACIÓN DE EXCLUYENTES
# =============================================================================

def test_evaluacion_candidato_cumple_excluyentes(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[{"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 3}],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 200
    assert response.json()["cumple_excluyentes"] is True
    assert response.json()["descartado_automaticamente"] is False


def test_evaluacion_candidato_no_cumple_por_experiencia(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[{"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 0}],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cumple_excluyentes"] is False
    # Regla vigente M2/M3: la evaluación es informativa y no cambia automáticamente
    # el estado de postulación del candidato.
    assert body["descartado_automaticamente"] is False
    assert body["habilidades_faltantes"]
    assert body["habilidades_faltantes"][0]["habilidad_id"] == seed_info["habilidad1_id"]
    assert "Experiencia insuficiente" in body["habilidades_faltantes"][0]["motivo"]


def test_evaluacion_candidato_no_cumple_por_habilidad_faltante(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cumple_excluyentes"] is False
    assert body["descartado_automaticamente"] is False
    assert body["habilidades_faltantes"]
    assert body["habilidades_faltantes"][0]["habilidad_id"] == seed_info["habilidad1_id"]
    assert "no informada" in body["habilidades_faltantes"][0]["motivo"].lower()




def test_evaluacion_excluyentes_requiere_sol_view(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[{"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 3}],
        headers=_headers(seed_info["no_perm_user_id"]),
    )
    assert response.status_code == 403


def test_evaluacion_excluyentes_sin_token_401(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[{"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 3}],
    )
    assert response.status_code == 401


def test_evaluacion_excluyentes_solicitud_inexistente_404(client: TestClient, seed_info: SeedInfo):
    response = client.post(
        "/solicitudes/999999/evaluar-candidato",
        json=[{"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 3}],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 404


def test_evaluacion_excluyentes_payload_invalido_422(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[{"habilidad_id": 0, "anios_experiencia": -1}],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 422


def test_evaluacion_excluyentes_ignora_habilidades_no_excluyentes(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[
            {"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 2},
            {"habilidad_id": seed_info["habilidad2_id"], "anios_experiencia": 0},
        ],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cumple_excluyentes"] is True
    assert body["descartado_automaticamente"] is False
    assert body["habilidades_faltantes"] == []


def test_evaluacion_excluyentes_no_modifica_solicitud(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    before = client.get(
        f"/solicitudes/{req['sol_id']}",
        headers=_headers(seed_info["view_user_id"]),
    ).json()

    response = client.post(
        f"/solicitudes/{req['sol_id']}/evaluar-candidato",
        json=[{"habilidad_id": seed_info["habilidad1_id"], "anios_experiencia": 0}],
        headers=_headers(seed_info["view_user_id"]),
    )
    assert response.status_code == 200
    assert response.json()["descartado_automaticamente"] is False

    after = client.get(
        f"/solicitudes/{req['sol_id']}",
        headers=_headers(seed_info["view_user_id"]),
    ).json()
    assert after["sol_estado_solicitud_id"] == before["sol_estado_solicitud_id"]
    assert after["sol_usuario_creador_id"] == before["sol_usuario_creador_id"]


# =============================================================================
# CONTRATO DE API
# =============================================================================

def test_no_existe_delete_fisico_solicitud(client: TestClient, seed_info: SeedInfo):
    req = _create_request(client, seed_info)
    response = client.delete(
        f"/solicitudes/{req['sol_id']}", headers=_headers(seed_info["admin_id"])
    )
    assert response.status_code == 405


def test_extra_field_rechazado_en_empresa_cliente_y_solicitud(client: TestClient, seed_info: SeedInfo):
    empresa = _empresa_payload("900")
    empresa["campo_extra"] = "x"
    assert client.post(
        "/clientes/empresas", json=empresa, headers=_headers(seed_info["cat_user_id"])
    ).status_code == 422

    cliente = _cliente_payload(seed_info, "901")
    cliente["campo_extra"] = "x"
    assert client.post(
        "/clientes", json=cliente, headers=_headers(seed_info["cat_user_id"])
    ).status_code == 422

    solicitud = _solicitud_payload(seed_info)
    solicitud["campo_extra"] = "x"
    assert client.post(
        "/solicitudes", json=solicitud, headers=_headers(seed_info["admin_id"])
    ).status_code == 422
