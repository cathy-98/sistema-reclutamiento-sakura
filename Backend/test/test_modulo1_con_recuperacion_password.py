from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Iterator

# IMPORTANTE: definir configuración JWT ANTES de importar app.auth.utils/dependencies.
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "qa-test-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ACTIVE_USER_STATUS_NAME", "Activo")
os.environ.setdefault("DELETED_USER_STATUS_NAME", "Eliminado")
os.environ.setdefault("ADMIN_ROLE_NAME", "Administrador")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import models as auth_models
from app.auth import password_reset_service
from app.auth import router as auth_router
from app.auth import utils as auth_utils
from app.auth.email_service import EmailDeliveryError
from app.database import Base, get_db
from app.usuarios import models
from app.usuarios import router as usuarios_router


# =============================================================================
# BASE DE DATOS AISLADA
# =============================================================================
# SQLite en memoria evita tocar PostgreSQL de desarrollo/producción.
# StaticPool garantiza que todos los threads del TestClient compartan
# la misma base en memoria.
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


MODULE1_TABLES = [
    models.Area.__table__,
    models.Permiso.__table__,
    models.Rol.__table__,
    models.RolPermiso.__table__,
    models.EstadoUsuario.__table__,
    models.Usuario.__table__,
    auth_models.PasswordResetToken.__table__,
]


# =============================================================================
# APLICACIÓN FASTAPI EXCLUSIVA PARA EL MÓDULO 1
# =============================================================================
app_test = FastAPI(title="QA Módulo 1")
app_test.include_router(auth_router.router)
app_test.include_router(usuarios_router.router)


def override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app_test.dependency_overrides[get_db] = override_get_db


# =============================================================================
# DATOS QA BASE
# =============================================================================
PERMISSIONS = [
    "USR_CREATE",
    "USR_VIEW",
    "USR_UPDATE",
    "USR_DELETE",
]

ADMIN_EMAIL = "admin.qa@sakura.cl"
ADMIN_PASSWORD = "AdminQA123!"
VIEWER_EMAIL = "viewer.qa@sakura.cl"
VIEWER_PASSWORD = "ViewerQA123!"
NO_PERM_EMAIL = "noperm.qa@sakura.cl"
NO_PERM_PASSWORD = "NoPermQA123!"
INACTIVE_EMAIL = "inactive.qa@sakura.cl"
INACTIVE_PASSWORD = "InactiveQA123!"


class SeedInfo(dict):
    pass


def _seed_database() -> SeedInfo:
    db = TestingSessionLocal()
    try:
        activo = models.EstadoUsuario(
            esusr_nombre="Activo",
            esusr_descripcion="Cuenta habilitada",
        )
        inactivo = models.EstadoUsuario(
            esusr_nombre="Inactivo",
            esusr_descripcion="Cuenta deshabilitada",
        )
        bloqueado = models.EstadoUsuario(
            esusr_nombre="Bloqueado",
            esusr_descripcion="Cuenta bloqueada",
        )
        eliminado = models.EstadoUsuario(
            esusr_nombre="Eliminado",
            esusr_descripcion="Baja lógica",
        )
        area = models.Area(
            area_nombre="QA",
            area_descripcion="Área para automatización",
        )
        db.add_all([activo, inactivo, bloqueado, eliminado, area])
        db.flush()

        permisos = [
            models.Permiso(
                per_nombre=name,
                per_descripcion=f"Permiso QA {name}",
            )
            for name in PERMISSIONS
        ]
        db.add_all(permisos)
        db.flush()

        admin_role = models.Rol(
            rol_nombre="Administrador",
            rol_descripcion="Administrador QA",
            permisos=list(permisos),
        )
        viewer_role = models.Rol(
            rol_nombre="QAViewer",
            rol_descripcion="Solo lectura",
            permisos=[p for p in permisos if p.per_nombre == "USR_VIEW"],
        )
        no_perm_role = models.Rol(
            rol_nombre="QANoPerm",
            rol_descripcion="Sin permisos",
            permisos=[],
        )
        db.add_all([admin_role, viewer_role, no_perm_role])
        db.flush()

        admin = models.Usuario(
            usr_rol_id=admin_role.rol_id,
            usr_estado_usuario_id=activo.esusr_id,
            usr_area_id=area.area_id,
            usr_nombres="Admin",
            usr_apellido_paterno="QA",
            usr_apellido_materno=None,
            usr_rut_sin_dv="10000001",
            usr_dv="1",
            usr_telefono="900000001",
            usr_email=ADMIN_EMAIL,
            usr_contrasena=auth_utils.hash_password(ADMIN_PASSWORD),
        )
        viewer = models.Usuario(
            usr_rol_id=viewer_role.rol_id,
            usr_estado_usuario_id=activo.esusr_id,
            usr_area_id=area.area_id,
            usr_nombres="Viewer",
            usr_apellido_paterno="QA",
            usr_apellido_materno=None,
            usr_rut_sin_dv="10000002",
            usr_dv="2",
            usr_telefono="900000002",
            usr_email=VIEWER_EMAIL,
            usr_contrasena=auth_utils.hash_password(VIEWER_PASSWORD),
        )
        no_perm = models.Usuario(
            usr_rol_id=no_perm_role.rol_id,
            usr_estado_usuario_id=activo.esusr_id,
            usr_area_id=area.area_id,
            usr_nombres="SinPerm",
            usr_apellido_paterno="QA",
            usr_apellido_materno=None,
            usr_rut_sin_dv="10000003",
            usr_dv="3",
            usr_telefono="900000003",
            usr_email=NO_PERM_EMAIL,
            usr_contrasena=auth_utils.hash_password(NO_PERM_PASSWORD),
        )
        inactive = models.Usuario(
            usr_rol_id=viewer_role.rol_id,
            usr_estado_usuario_id=inactivo.esusr_id,
            usr_area_id=area.area_id,
            usr_nombres="Inactive",
            usr_apellido_paterno="QA",
            usr_apellido_materno=None,
            usr_rut_sin_dv="10000004",
            usr_dv="4",
            usr_telefono="900000004",
            usr_email=INACTIVE_EMAIL,
            usr_contrasena=auth_utils.hash_password(INACTIVE_PASSWORD),
        )
        db.add_all([admin, viewer, no_perm, inactive])
        db.commit()

        return SeedInfo(
            activo_id=activo.esusr_id,
            inactivo_id=inactivo.esusr_id,
            bloqueado_id=bloqueado.esusr_id,
            eliminado_id=eliminado.esusr_id,
            area_id=area.area_id,
            admin_role_id=admin_role.rol_id,
            viewer_role_id=viewer_role.rol_id,
            no_perm_role_id=no_perm_role.rol_id,
            admin_id=admin.usr_id,
            viewer_id=viewer.usr_id,
            no_perm_id=no_perm.usr_id,
            inactive_id=inactive.usr_id,
            permission_ids={p.per_nombre: p.per_id for p in permisos},
        )
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=TEST_ENGINE, tables=MODULE1_TABLES)
    Base.metadata.create_all(bind=TEST_ENGINE, tables=MODULE1_TABLES)
    _seed_database()
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE, tables=MODULE1_TABLES)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app_test) as api_client:
        yield api_client


@pytest.fixture
def seed_info() -> SeedInfo:
    db = TestingSessionLocal()
    try:
        activo = db.scalar(
            select(models.EstadoUsuario).where(models.EstadoUsuario.esusr_nombre == "Activo")
        )
        inactivo = db.scalar(
            select(models.EstadoUsuario).where(models.EstadoUsuario.esusr_nombre == "Inactivo")
        )
        eliminado = db.scalar(
            select(models.EstadoUsuario).where(models.EstadoUsuario.esusr_nombre == "Eliminado")
        )
        area = db.scalar(select(models.Area).where(models.Area.area_nombre == "QA"))
        admin_role = db.scalar(select(models.Rol).where(models.Rol.rol_nombre == "Administrador"))
        viewer_role = db.scalar(select(models.Rol).where(models.Rol.rol_nombre == "QAViewer"))
        no_perm_role = db.scalar(select(models.Rol).where(models.Rol.rol_nombre == "QANoPerm"))
        admin = db.scalar(select(models.Usuario).where(models.Usuario.usr_email == ADMIN_EMAIL))
        viewer = db.scalar(select(models.Usuario).where(models.Usuario.usr_email == VIEWER_EMAIL))
        no_perm = db.scalar(select(models.Usuario).where(models.Usuario.usr_email == NO_PERM_EMAIL))
        inactive = db.scalar(select(models.Usuario).where(models.Usuario.usr_email == INACTIVE_EMAIL))
        permisos = list(db.scalars(select(models.Permiso)).all())
        return SeedInfo(
            activo_id=activo.esusr_id,
            inactivo_id=inactivo.esusr_id,
            eliminado_id=eliminado.esusr_id,
            area_id=area.area_id,
            admin_role_id=admin_role.rol_id,
            viewer_role_id=viewer_role.rol_id,
            no_perm_role_id=no_perm_role.rol_id,
            admin_id=admin.usr_id,
            viewer_id=viewer.usr_id,
            no_perm_id=no_perm.usr_id,
            inactive_id=inactive.usr_id,
            permission_ids={p.per_nombre: p.per_id for p in permisos},
        )
    finally:
        db.close()


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]
    assert body["expires_in"] == auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return body["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token(client: TestClient) -> str:
    return _login(client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
def viewer_token(client: TestClient) -> str:
    return _login(client, VIEWER_EMAIL, VIEWER_PASSWORD)


@pytest.fixture
def no_perm_token(client: TestClient) -> str:
    return _login(client, NO_PERM_EMAIL, NO_PERM_PASSWORD)


# =============================================================================
# AUTH / JWT
# =============================================================================
def test_login_correcto(client: TestClient):
    token = _login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert token.count(".") == 2


def test_login_password_incorrecta_retorna_401(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": "PasswordIncorrecta"},
    )
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_login_usuario_inexistente_retorna_401(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": "noexiste@sakura.cl", "password": "Password123!"},
    )
    assert response.status_code == 401


def test_login_usuario_inactivo_retorna_403(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"email": INACTIVE_EMAIL, "password": INACTIVE_PASSWORD},
    )
    assert response.status_code == 403


def test_auth_me_sin_token_retorna_401(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_auth_me_token_invalido_retorna_401(client: TestClient):
    response = client.get(
        "/auth/me",
        headers=_headers("token.que.no-es-valido"),
    )
    assert response.status_code == 401


def test_auth_me_token_expirado_retorna_401(client: TestClient, seed_info: SeedInfo):
    expired = auth_utils.create_access_token(
        {"sub": str(seed_info["admin_id"]), "email": ADMIN_EMAIL},
        expires_delta=timedelta(seconds=-1),
    )
    response = client.get("/auth/me", headers=_headers(expired))
    assert response.status_code == 401


def test_auth_me_token_valido_retorna_usuario(client: TestClient, admin_token: str):
    response = client.get("/auth/me", headers=_headers(admin_token))
    assert response.status_code == 200
    body = response.json()
    assert body["usr_email"] == ADMIN_EMAIL
    assert "USR_VIEW" in body["permisos"]


def test_change_password_password_actual_incorrecta(client: TestClient, admin_token: str):
    response = client.post(
        "/auth/change-password",
        headers=_headers(admin_token),
        json={"password_actual": "Incorrecta123!", "password_nueva": "NuevaClave123!"},
    )
    assert response.status_code == 400


def test_change_password_misma_password_retorna_400(client: TestClient, admin_token: str):
    response = client.post(
        "/auth/change-password",
        headers=_headers(admin_token),
        json={"password_actual": ADMIN_PASSWORD, "password_nueva": ADMIN_PASSWORD},
    )
    assert response.status_code == 400


def test_change_password_correcto_invalida_password_anterior(client: TestClient, admin_token: str):
    new_password = "AdminNueva123!"
    response = client.post(
        "/auth/change-password",
        headers=_headers(admin_token),
        json={"password_actual": ADMIN_PASSWORD, "password_nueva": new_password},
    )
    assert response.status_code == 204

    old_login = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": new_password},
    )
    assert new_login.status_code == 200


# =============================================================================
# RBAC / AUTORIZACIÓN
# =============================================================================
def test_usuarios_sin_token_retorna_401(client: TestClient):
    response = client.get("/usuarios/")
    assert response.status_code == 401


def test_usuario_sin_permiso_retorna_403(client: TestClient, no_perm_token: str):
    response = client.get("/usuarios/", headers=_headers(no_perm_token))
    assert response.status_code == 403


def test_usuario_con_usr_view_puede_listar(client: TestClient, viewer_token: str):
    response = client.get("/usuarios/", headers=_headers(viewer_token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_no_admin_no_puede_crear_rol(client: TestClient, viewer_token: str):
    response = client.post(
        "/usuarios/roles",
        headers=_headers(viewer_token),
        json={"rol_nombre": "QANewRole", "rol_descripcion": "No debe crearse"},
    )
    assert response.status_code == 403


# =============================================================================
# CRUD DE USUARIOS
# =============================================================================
def _user_payload(seed_info: SeedInfo, *, email: str = "nuevo.qa@sakura.cl", rut: str = "20000001"):
    return {
        "usr_nombres": "Nuevo",
        "usr_apellido_paterno": "Usuario",
        "usr_apellido_materno": "QA",
        "usr_rut_sin_dv": rut,
        "usr_dv": "K",
        "usr_telefono": "911111111",
        "usr_email": email,
        "usr_rol_id": seed_info["viewer_role_id"],
        "usr_estado_usuario_id": seed_info["activo_id"],
        "usr_area_id": seed_info["area_id"],
        "usr_contrasena": "NuevoUsuario123!",
    }


def test_crud_usuario_completo(client: TestClient, admin_token: str, seed_info: SeedInfo):
    headers = _headers(admin_token)
    payload = _user_payload(seed_info)

    # POST
    response = client.post("/usuarios/", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    created = response.json()
    user_id = created["usr_id"]
    assert created["usr_email"] == payload["usr_email"]
    assert "usr_contrasena" not in created

    # GET lista + búsqueda
    response = client.get(
        "/usuarios/",
        headers=headers,
        params={"q": payload["usr_email"], "limit": 500},
    )
    assert response.status_code == 200
    assert any(item["usr_id"] == user_id for item in response.json())

    # GET filtros
    response = client.get(
        "/usuarios/",
        headers=headers,
        params={
            "rol_id": seed_info["viewer_role_id"],
            "estado_id": seed_info["activo_id"],
            "area_id": seed_info["area_id"],
            "limit": 500,
        },
    )
    assert response.status_code == 200
    assert any(item["usr_id"] == user_id for item in response.json())

    # GET ID
    response = client.get(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["usr_id"] == user_id

    # GET permisos usuario
    response = client.get(f"/usuarios/{user_id}/permisos", headers=headers)
    assert response.status_code == 200
    assert response.json() == ["USR_VIEW"]

    # PUT
    put_payload = {
        "usr_nombres": "Reemplazo",
        "usr_apellido_paterno": "Usuario",
        "usr_apellido_materno": None,
        "usr_rut_sin_dv": "20000001",
        "usr_dv": "K",
        "usr_telefono": "922222222",
        "usr_email": "reemplazo.qa@sakura.cl",
        "usr_rol_id": seed_info["viewer_role_id"],
        "usr_estado_usuario_id": seed_info["activo_id"],
        "usr_area_id": seed_info["area_id"],
    }
    response = client.put(f"/usuarios/{user_id}", headers=headers, json=put_payload)
    assert response.status_code == 200, response.text
    assert response.json()["usr_nombres"] == "Reemplazo"

    # PATCH
    response = client.patch(
        f"/usuarios/{user_id}",
        headers=headers,
        json={"usr_telefono": "933333333"},
    )
    assert response.status_code == 200
    assert response.json()["usr_telefono"] == "933333333"

    # RESET PASSWORD
    response = client.post(
        f"/usuarios/{user_id}/reset-password",
        headers=headers,
        json={"nueva_contrasena": "ResetQA123!"},
    )
    assert response.status_code == 204

    response = client.post(
        "/auth/login",
        json={"email": put_payload["usr_email"], "password": "ResetQA123!"},
    )
    assert response.status_code == 200

    # DELETE = baja lógica
    response = client.delete(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 204

    # El usuario sigue físicamente existente pero queda Eliminado.
    response = client.get(f"/usuarios/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["estado"]["esusr_nombre"] == "Eliminado"

    # Ya no puede autenticarse.
    response = client.post(
        "/auth/login",
        json={"email": put_payload["usr_email"], "password": "ResetQA123!"},
    )
    assert response.status_code == 403


def test_usuario_get_inexistente_404(client: TestClient, admin_token: str):
    response = client.get("/usuarios/999999", headers=_headers(admin_token))
    assert response.status_code == 404


def test_usuario_patch_vacio_422(client: TestClient, admin_token: str, seed_info: SeedInfo):
    response = client.patch(
        f"/usuarios/{seed_info['viewer_id']}",
        headers=_headers(admin_token),
        json={},
    )
    assert response.status_code == 422


def test_usuario_email_duplicado_409(client: TestClient, admin_token: str, seed_info: SeedInfo):
    payload = _user_payload(seed_info, email=ADMIN_EMAIL, rut="20000002")
    response = client.post("/usuarios/", headers=_headers(admin_token), json=payload)
    assert response.status_code == 409


def test_usuario_rut_duplicado_409(client: TestClient, admin_token: str, seed_info: SeedInfo):
    payload = _user_payload(seed_info, email="otro.qa@sakura.cl", rut="10000001")
    payload["usr_dv"] = "1"
    response = client.post("/usuarios/", headers=_headers(admin_token), json=payload)
    assert response.status_code == 409


@pytest.mark.parametrize(
    "field,value",
    [
        ("usr_rol_id", 999999),
        ("usr_estado_usuario_id", 999999),
        ("usr_area_id", 999999),
    ],
)
def test_usuario_fk_inexistente_422(
    client: TestClient,
    admin_token: str,
    seed_info: SeedInfo,
    field: str,
    value: int,
):
    payload = _user_payload(seed_info, email=f"fk-{field}@sakura.cl", rut=str(30000000 + len(field)))
    payload[field] = value
    response = client.post("/usuarios/", headers=_headers(admin_token), json=payload)
    assert response.status_code == 422, response.text


def test_usuario_rut_incompleto_422(client: TestClient, admin_token: str, seed_info: SeedInfo):
    payload = _user_payload(seed_info, email="rut-incompleto@sakura.cl", rut="40000001")
    payload["usr_dv"] = None
    response = client.post("/usuarios/", headers=_headers(admin_token), json=payload)
    assert response.status_code == 422


def test_admin_no_puede_auto_eliminarse(client: TestClient, admin_token: str, seed_info: SeedInfo):
    response = client.delete(
        f"/usuarios/{seed_info['admin_id']}",
        headers=_headers(admin_token),
    )
    assert response.status_code == 409


# =============================================================================
# CRUD ROLES / PERMISOS / RELACIÓN RBAC
# =============================================================================
def test_crud_rol_completo(client: TestClient, admin_token: str):
    headers = _headers(admin_token)
    response = client.post(
        "/usuarios/roles",
        headers=headers,
        json={"rol_nombre": "QATemporal", "rol_descripcion": "Temporal"},
    )
    assert response.status_code == 201
    role_id = response.json()["rol_id"]

    assert client.get(f"/usuarios/roles/{role_id}", headers=headers).status_code == 200

    response = client.put(
        f"/usuarios/roles/{role_id}",
        headers=headers,
        json={"rol_nombre": "QATempPut", "rol_descripcion": "PUT"},
    )
    assert response.status_code == 200
    assert response.json()["rol_nombre"] == "QATempPut"

    response = client.patch(
        f"/usuarios/roles/{role_id}",
        headers=headers,
        json={"rol_descripcion": "PATCH"},
    )
    assert response.status_code == 200

    assert client.delete(f"/usuarios/roles/{role_id}", headers=headers).status_code == 204
    assert client.get(f"/usuarios/roles/{role_id}", headers=headers).status_code == 404


def test_rol_duplicado_409(client: TestClient, admin_token: str):
    response = client.post(
        "/usuarios/roles",
        headers=_headers(admin_token),
        json={"rol_nombre": "Administrador", "rol_descripcion": "Duplicado"},
    )
    assert response.status_code == 409


def test_rol_asignado_usuario_no_se_puede_borrar(client: TestClient, admin_token: str, seed_info: SeedInfo):
    response = client.delete(
        f"/usuarios/roles/{seed_info['viewer_role_id']}",
        headers=_headers(admin_token),
    )
    assert response.status_code == 409


def test_crud_permiso_completo(client: TestClient, admin_token: str):
    headers = _headers(admin_token)
    response = client.post(
        "/usuarios/permisos",
        headers=headers,
        json={"per_nombre": "QA_TMP", "per_descripcion": "Temporal"},
    )
    assert response.status_code == 201
    permission_id = response.json()["per_id"]

    assert client.get(f"/usuarios/permisos/{permission_id}", headers=headers).status_code == 200

    response = client.put(
        f"/usuarios/permisos/{permission_id}",
        headers=headers,
        json={"per_nombre": "QA_TMP2", "per_descripcion": "PUT"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/usuarios/permisos/{permission_id}",
        headers=headers,
        json={"per_descripcion": "PATCH"},
    )
    assert response.status_code == 200

    assert client.delete(f"/usuarios/permisos/{permission_id}", headers=headers).status_code == 204
    assert client.get(f"/usuarios/permisos/{permission_id}", headers=headers).status_code == 404


def test_permiso_duplicado_409(client: TestClient, admin_token: str):
    response = client.post(
        "/usuarios/permisos",
        headers=_headers(admin_token),
        json={"per_nombre": "USR_VIEW", "per_descripcion": "Duplicado"},
    )
    assert response.status_code == 409


def test_reemplazar_agregar_y_quitar_permisos_de_rol(
    client: TestClient,
    admin_token: str,
    seed_info: SeedInfo,
):
    headers = _headers(admin_token)

    # Rol temporal
    response = client.post(
        "/usuarios/roles",
        headers=headers,
        json={"rol_nombre": "QARBAC", "rol_descripcion": "Prueba RBAC"},
    )
    assert response.status_code == 201
    role_id = response.json()["rol_id"]

    view_id = seed_info["permission_ids"]["USR_VIEW"]
    create_id = seed_info["permission_ids"]["USR_CREATE"]

    # PUT reemplaza set completo
    response = client.put(
        f"/usuarios/roles/{role_id}/permisos",
        headers=headers,
        json={"permiso_ids": [view_id]},
    )
    assert response.status_code == 200
    assert [p["per_nombre"] for p in response.json()["permisos"]] == ["USR_VIEW"]

    # POST agrega uno
    response = client.post(
        f"/usuarios/roles/{role_id}/permisos/{create_id}",
        headers=headers,
    )
    assert response.status_code == 200
    names = {p["per_nombre"] for p in response.json()["permisos"]}
    assert names == {"USR_VIEW", "USR_CREATE"}

    # GET permisos del rol
    response = client.get(f"/usuarios/roles/{role_id}/permisos", headers=headers)
    assert response.status_code == 200
    assert {p["per_nombre"] for p in response.json()} == {"USR_VIEW", "USR_CREATE"}

    # DELETE quita permiso
    response = client.delete(
        f"/usuarios/roles/{role_id}/permisos/{create_id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert {p["per_nombre"] for p in response.json()["permisos"]} == {"USR_VIEW"}

    # Quitar de nuevo debe ser 404
    response = client.delete(
        f"/usuarios/roles/{role_id}/permisos/{create_id}",
        headers=headers,
    )
    assert response.status_code == 404


def test_reemplazar_permisos_con_id_inexistente_422(client: TestClient, admin_token: str, seed_info: SeedInfo):
    response = client.put(
        f"/usuarios/roles/{seed_info['viewer_role_id']}/permisos",
        headers=_headers(admin_token),
        json={"permiso_ids": [999999]},
    )
    assert response.status_code == 422


def test_reemplazar_permisos_con_ids_duplicados_422(client: TestClient, admin_token: str, seed_info: SeedInfo):
    permission_id = seed_info["permission_ids"]["USR_VIEW"]
    response = client.put(
        f"/usuarios/roles/{seed_info['viewer_role_id']}/permisos",
        headers=_headers(admin_token),
        json={"permiso_ids": [permission_id, permission_id]},
    )
    assert response.status_code == 422


# =============================================================================
# CRUD ÁREAS Y ESTADOS
# =============================================================================
def test_crud_area_completo(client: TestClient, admin_token: str):
    headers = _headers(admin_token)
    response = client.post(
        "/usuarios/areas",
        headers=headers,
        json={"area_nombre": "QA Temp", "area_descripcion": "Temporal"},
    )
    assert response.status_code == 201
    area_id = response.json()["area_id"]

    assert client.get(f"/usuarios/areas/{area_id}", headers=headers).status_code == 200

    response = client.put(
        f"/usuarios/areas/{area_id}",
        headers=headers,
        json={"area_nombre": "QA Temp PUT", "area_descripcion": "PUT"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/usuarios/areas/{area_id}",
        headers=headers,
        json={"area_descripcion": "PATCH"},
    )
    assert response.status_code == 200

    assert client.delete(f"/usuarios/areas/{area_id}", headers=headers).status_code == 204
    assert client.get(f"/usuarios/areas/{area_id}", headers=headers).status_code == 404


def test_area_en_uso_no_se_puede_borrar(client: TestClient, admin_token: str, seed_info: SeedInfo):
    response = client.delete(
        f"/usuarios/areas/{seed_info['area_id']}",
        headers=_headers(admin_token),
    )
    assert response.status_code == 409


def test_crud_estado_completo(client: TestClient, admin_token: str):
    headers = _headers(admin_token)
    response = client.post(
        "/usuarios/estados",
        headers=headers,
        json={"esusr_nombre": "QATempEstado", "esusr_descripcion": "Temporal"},
    )
    assert response.status_code == 201
    estado_id = response.json()["esusr_id"]

    assert client.get(f"/usuarios/estados/{estado_id}", headers=headers).status_code == 200

    response = client.put(
        f"/usuarios/estados/{estado_id}",
        headers=headers,
        json={"esusr_nombre": "QATempEstado2", "esusr_descripcion": "PUT"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/usuarios/estados/{estado_id}",
        headers=headers,
        json={"esusr_descripcion": "PATCH"},
    )
    assert response.status_code == 200

    assert client.delete(f"/usuarios/estados/{estado_id}", headers=headers).status_code == 204
    assert client.get(f"/usuarios/estados/{estado_id}", headers=headers).status_code == 404


def test_estado_en_uso_no_se_puede_borrar(client: TestClient, admin_token: str, seed_info: SeedInfo):
    response = client.delete(
        f"/usuarios/estados/{seed_info['activo_id']}",
        headers=_headers(admin_token),
    )
    assert response.status_code == 409


# =============================================================================
# VALIDACIONES HTTP / SCHEMAS
# =============================================================================
def test_password_corta_usuario_create_422(client: TestClient, admin_token: str, seed_info: SeedInfo):
    payload = _user_payload(seed_info, email="shortpass@sakura.cl", rut="50000001")
    payload["usr_contrasena"] = "1234"
    response = client.post("/usuarios/", headers=_headers(admin_token), json=payload)
    assert response.status_code == 422


def test_email_invalido_usuario_create_422(client: TestClient, admin_token: str, seed_info: SeedInfo):
    payload = _user_payload(seed_info, email="correo-invalido", rut="50000002")
    response = client.post("/usuarios/", headers=_headers(admin_token), json=payload)
    assert response.status_code == 422


def test_extra_field_rechazado_422(client: TestClient, admin_token: str):
    response = client.post(
        "/usuarios/roles",
        headers=_headers(admin_token),
        json={
            "rol_nombre": "QAXtra",
            "rol_descripcion": "Con campo extra",
            "campo_inexistente": True,
        },
    )
    assert response.status_code == 422


# =============================================================================
# RECUPERACIÓN DE CONTRASEÑA / FORGOT PASSWORD
# =============================================================================
def _capturar_correo_reset(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Sustituye Gmail SMTP por una función local y devuelve los envíos capturados."""
    enviados: list[dict] = []

    def fake_send_password_reset_email(*, to_email: str, token: str, expiration_minutes: int) -> None:
        enviados.append(
            {
                "to_email": to_email,
                "token": token,
                "expiration_minutes": expiration_minutes,
            }
        )

    monkeypatch.setattr(
        auth_router,
        "send_password_reset_email",
        fake_send_password_reset_email,
    )
    return enviados


def _obtener_tokens_reset() -> list[auth_models.PasswordResetToken]:
    db = TestingSessionLocal()
    try:
        return list(
            db.scalars(
                select(auth_models.PasswordResetToken).order_by(
                    auth_models.PasswordResetToken.prst_id.asc()
                )
            ).all()
        )
    finally:
        db.close()


def test_forgot_password_usuario_activo_crea_token_sin_enviar_gmail(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    seed_info: SeedInfo,
):
    enviados = _capturar_correo_reset(monkeypatch)

    response = client.post(
        "/auth/forgot-password",
        json={"email": ADMIN_EMAIL},
    )

    assert response.status_code == 202, response.text
    assert response.json()["message"] == password_reset_service.GENERIC_FORGOT_PASSWORD_MESSAGE
    assert len(enviados) == 1
    assert enviados[0]["to_email"] == ADMIN_EMAIL
    assert enviados[0]["expiration_minutes"] == 30

    raw_token = enviados[0]["token"]
    assert isinstance(raw_token, str)
    assert len(raw_token) >= 32

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    registro = tokens[0]
    assert registro.prst_usuario_id == seed_info["admin_id"]
    assert registro.prst_token_hash == password_reset_service.hash_reset_token(raw_token)
    assert registro.prst_token_hash != raw_token
    assert registro.prst_fecha_uso is None
    assert registro.prst_fecha_revocacion is None


def test_forgot_password_email_inexistente_responde_202_y_no_envia_correo(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    response = client.post(
        "/auth/forgot-password",
        json={"email": "no.existe@sakura.cl"},
    )

    assert response.status_code == 202
    assert response.json()["message"] == password_reset_service.GENERIC_FORGOT_PASSWORD_MESSAGE
    assert enviados == []
    assert _obtener_tokens_reset() == []


def test_forgot_password_usuario_inactivo_responde_202_y_no_envia_correo(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    response = client.post(
        "/auth/forgot-password",
        json={"email": INACTIVE_EMAIL},
    )

    assert response.status_code == 202
    assert response.json()["message"] == password_reset_service.GENERIC_FORGOT_PASSWORD_MESSAGE
    assert enviados == []
    assert _obtener_tokens_reset() == []


def test_forgot_password_nueva_solicitud_revoca_token_anterior(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    first = client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL})
    second = client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL})

    assert first.status_code == 202
    assert second.status_code == 202
    assert len(enviados) == 2
    assert enviados[0]["token"] != enviados[1]["token"]

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 2
    assert tokens[0].prst_fecha_revocacion is not None
    assert tokens[0].prst_fecha_uso is None
    assert tokens[1].prst_fecha_revocacion is None
    assert tokens[1].prst_fecha_uso is None


def test_forgot_password_fallo_envio_revoca_token_y_mantiene_respuesta_generica(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_delivery_failure(*, to_email: str, token: str, expiration_minutes: int) -> None:
        raise EmailDeliveryError("SMTP simulado no disponible")

    monkeypatch.setattr(
        auth_router,
        "send_password_reset_email",
        fake_delivery_failure,
    )

    response = client.post(
        "/auth/forgot-password",
        json={"email": ADMIN_EMAIL},
    )

    assert response.status_code == 202
    assert response.json()["message"] == password_reset_service.GENERIC_FORGOT_PASSWORD_MESSAGE

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    assert tokens[0].prst_fecha_revocacion is not None
    assert tokens[0].prst_fecha_uso is None


def test_reset_password_token_valido_cambia_password_y_marca_token_usado(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)
    nueva_password = "AdminRecuperada123!"

    forgot = client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL})
    assert forgot.status_code == 202
    token = enviados[0]["token"]

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": nueva_password},
    )
    assert response.status_code == 204, response.text

    old_login = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": ADMIN_EMAIL, "password": nueva_password},
    )
    assert new_login.status_code == 200

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    assert tokens[0].prst_fecha_uso is not None


def test_reset_password_token_usado_no_puede_reutilizarse(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    assert client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL}).status_code == 202
    token = enviados[0]["token"]

    first = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": "PrimeraNueva123!"},
    )
    assert first.status_code == 204

    second = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": "SegundaNueva123!"},
    )
    assert second.status_code == 400


def test_reset_password_token_inexistente_retorna_400(client: TestClient):
    token_inexistente = "x" * 64
    response = client.post(
        "/auth/reset-password",
        json={"token": token_inexistente, "nueva_contrasena": "NuevaClave123!"},
    )
    assert response.status_code == 400


def test_reset_password_token_expirado_retorna_410(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    assert client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL}).status_code == 202
    token = enviados[0]["token"]

    db = TestingSessionLocal()
    try:
        registro = db.scalar(
            select(auth_models.PasswordResetToken).where(
                auth_models.PasswordResetToken.prst_token_hash
                == password_reset_service.hash_reset_token(token)
            )
        )
        assert registro is not None
        registro.prst_fecha_expiracion = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": "NuevaClave123!"},
    )
    assert response.status_code == 410

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    assert tokens[0].prst_fecha_revocacion is not None


def test_reset_password_no_permite_misma_password_actual(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    assert client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL}).status_code == 202
    token = enviados[0]["token"]

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": ADMIN_PASSWORD},
    )
    assert response.status_code == 400

    # El token sigue pendiente porque la contraseña no llegó a cambiarse.
    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    assert tokens[0].prst_fecha_uso is None
    assert tokens[0].prst_fecha_revocacion is None


def test_change_password_revoca_token_recuperacion_pendiente(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    admin_token: str,
):
    enviados = _capturar_correo_reset(monkeypatch)

    assert client.post("/auth/forgot-password", json={"email": ADMIN_EMAIL}).status_code == 202
    token = enviados[0]["token"]

    response = client.post(
        "/auth/change-password",
        headers=_headers(admin_token),
        json={"password_actual": ADMIN_PASSWORD, "password_nueva": "CambioPropio123!"},
    )
    assert response.status_code == 204

    reset = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": "NoDebeAplicarse123!"},
    )
    assert reset.status_code == 400

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    assert tokens[0].prst_fecha_revocacion is not None


def test_reset_administrativo_revoca_token_recuperacion_pendiente(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    admin_token: str,
    seed_info: SeedInfo,
):
    enviados = _capturar_correo_reset(monkeypatch)

    assert client.post("/auth/forgot-password", json={"email": VIEWER_EMAIL}).status_code == 202
    token = enviados[0]["token"]

    admin_reset = client.post(
        f"/usuarios/{seed_info['viewer_id']}/reset-password",
        headers=_headers(admin_token),
        json={"nueva_contrasena": "ViewerResetAdmin123!"},
    )
    assert admin_reset.status_code == 204

    reset = client.post(
        "/auth/reset-password",
        json={"token": token, "nueva_contrasena": "NoDebeAplicarse123!"},
    )
    assert reset.status_code == 400

    tokens = _obtener_tokens_reset()
    assert len(tokens) == 1
    assert tokens[0].prst_fecha_revocacion is not None


def test_reset_password_token_demasiado_corto_retorna_422(client: TestClient):
    response = client.post(
        "/auth/reset-password",
        json={"token": "corto", "nueva_contrasena": "NuevaClave123!"},
    )
    assert response.status_code == 422


def test_forgot_password_email_invalido_retorna_422(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    enviados = _capturar_correo_reset(monkeypatch)

    response = client.post(
        "/auth/forgot-password",
        json={"email": "correo-invalido"},
    )
    assert response.status_code == 422
    assert enviados == []
