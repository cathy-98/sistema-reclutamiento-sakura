
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Iterator

# JWT de QA antes de importar dependencias de auth.
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "qa-modulo4-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz",
)
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ACTIVE_USER_STATUS_NAME", "Activo")
os.environ.setdefault("DELETED_USER_STATUS_NAME", "Eliminado")
os.environ.setdefault("ADMIN_ROLE_NAME", "Administrador")

import pytest
from types import SimpleNamespace

import app.auth.dependencies as auth_dependencies
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import utils as auth_utils
from app.database import Base, get_db
from app.usuarios import models as user_models
from app.cuestionarios import models as m4_models
from app.cuestionarios import router as m4_router


# =============================================================================
# SQLITE AISLADO
# =============================================================================

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@event.listens_for(TEST_ENGINE, "connect")
def _fk_on(dbapi_connection, _record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)

USER_TABLES = [
    user_models.Area.__table__,
    user_models.Permiso.__table__,
    user_models.Rol.__table__,
    user_models.RolPermiso.__table__,
    user_models.EstadoUsuario.__table__,
    user_models.Usuario.__table__,
]

M4_TABLES = [
    m4_models.Cuestionario.__table__,
    m4_models.Pregunta.__table__,
    m4_models.OpcionRespuesta.__table__,
    m4_models.PreguntaCuestionario.__table__,
    m4_models.CandidatoCuestionario.__table__,
    m4_models.RespuestaPregunta.__table__,
]

SUPPORT_TABLES_DDL = [
    """
    CREATE TABLE tbl_habilidad (
        hab_id INTEGER PRIMARY KEY,
        hab_nombre VARCHAR(200) NOT NULL
    )
    """,
    """
    CREATE TABLE tbl_nivel_habilidad (
        nvhb_id INTEGER PRIMARY KEY,
        nvhb_nombre VARCHAR(100) NOT NULL,
        nvhb_descripcion VARCHAR(500),
        nvhb_puntaje_base INTEGER NOT NULL,
        nvhb_duracion INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE tbl_solicitud (
        sol_id INTEGER PRIMARY KEY,
        sol_codigo VARCHAR(20) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE tbl_disponibilidad (
        disp_id INTEGER PRIMARY KEY,
        disp_nombre VARCHAR(100) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE tbl_candidato (
        cand_id INTEGER PRIMARY KEY,
        cand_email VARCHAR(255) NOT NULL UNIQUE,
        cand_password VARCHAR(255),
        cand_nombres VARCHAR(150),
        cand_apellido_paterno VARCHAR(150),
        cand_apellido_materno VARCHAR(150),
        cand_fecha_nacimiento DATE,
        cand_telefono VARCHAR(50),
        cand_rut_sin_dv INTEGER,
        cand_dv INTEGER,
        cand_disponibilidad_id INTEGER,
        cand_resumen_profesional VARCHAR(2000),
        cand_fecha_creacion DATETIME,
        cand_url_1 VARCHAR(2000),
        cand_titulo VARCHAR(300),
        cand_estado_usuario_id INTEGER NOT NULL,
        cand_cv_urls VARCHAR(2000),
        FOREIGN KEY(cand_disponibilidad_id) REFERENCES tbl_disponibilidad(disp_id)
    )
    """,
    """
    CREATE TABLE tbl_solicitud_candidato (
        slcd_id INTEGER PRIMARY KEY,
        slcd_candidato_id INTEGER NOT NULL,
        slcd_solicitud_id INTEGER NOT NULL,
        slcd_estado_solicitud_candidato_id INTEGER DEFAULT 1
    )
    """,
    """
    CREATE TABLE tbl_estado_cuestionario_candidato (
        escc_id INTEGER PRIMARY KEY,
        escc_nombre VARCHAR(100) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE tbl_estado_solicitud_candidato (
        essc_id INTEGER PRIMARY KEY,
        essc_nombre VARCHAR(100) NOT NULL UNIQUE
    )
    """,
]

app_test = FastAPI(title="QA Módulo 4")
app_test.include_router(m4_router)

def override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app_test.dependency_overrides[get_db] = override_get_db


PERMISSIONS = ["CUEST_CREATE", "CUEST_ASSIGN", "CUEST_VIEW"]
ADMIN_EMAIL = "admin.m4@sakura.cl"
CREATE_EMAIL = "creator.m4@sakura.cl"
ASSIGN_EMAIL = "assign.m4@sakura.cl"
VIEW_EMAIL = "view.m4@sakura.cl"
NOPERM_EMAIL = "noperm.m4@sakura.cl"


def _create_schema():
    Base.metadata.create_all(bind=TEST_ENGINE, tables=USER_TABLES + M4_TABLES)
    with TEST_ENGINE.begin() as conn:
        for ddl in SUPPORT_TABLES_DDL:
            conn.execute(text(ddl))


def _drop_schema():
    with TEST_ENGINE.begin() as conn:
        for table in [
            "tbl_solicitud_candidato",
            "tbl_candidato",
            "tbl_disponibilidad",
            "tbl_solicitud",
            "tbl_nivel_habilidad",
            "tbl_habilidad",
            "tbl_estado_cuestionario_candidato",
            "tbl_estado_solicitud_candidato",
        ]:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
    Base.metadata.drop_all(bind=TEST_ENGINE, tables=M4_TABLES + USER_TABLES)


def _seed():
    db = TestingSessionLocal()
    try:
        activo = user_models.EstadoUsuario(
            esusr_nombre="Activo",
            esusr_descripcion="Activo",
        )
        inactivo = user_models.EstadoUsuario(
            esusr_nombre="Inactivo",
            esusr_descripcion="Inactivo",
        )
        eliminado = user_models.EstadoUsuario(
            esusr_nombre="Eliminado",
            esusr_descripcion="Eliminado",
        )
        area = user_models.Area(
            area_nombre="QA M4",
            area_descripcion="QA M4",
        )
        db.add_all([activo, inactivo, eliminado, area])
        db.flush()

        perms = {}
        for name in PERMISSIONS:
            p = user_models.Permiso(
                per_nombre=name,
                per_descripcion=f"Permiso {name}",
            )
            db.add(p)
            db.flush()
            perms[name] = p

        roles = {
            "admin": user_models.Rol(
                rol_nombre="Administrador",
                rol_descripcion="Todos M4",
                permisos=list(perms.values()),
            ),
            "create": user_models.Rol(
                rol_nombre="M4Create",
                rol_descripcion="Create",
                permisos=[perms["CUEST_CREATE"]],
            ),
            "assign": user_models.Rol(
                rol_nombre="M4Assign",
                rol_descripcion="Assign",
                permisos=[perms["CUEST_ASSIGN"]],
            ),
            "view": user_models.Rol(
                rol_nombre="M4View",
                rol_descripcion="View",
                permisos=[perms["CUEST_VIEW"]],
            ),
            "none": user_models.Rol(
                rol_nombre="M4None",
                rol_descripcion="None",
                permisos=[],
            ),
        }
        db.add_all(list(roles.values()))
        db.flush()

        def user(email, role):
            return user_models.Usuario(
                usr_rol_id=role.rol_id,
                usr_estado_usuario_id=activo.esusr_id,
                usr_area_id=area.area_id,
                usr_nombres="QA",
                usr_apellido_paterno="M4",
                usr_apellido_materno=None,
                usr_rut_sin_dv=str(70000000 + role.rol_id),
                usr_dv="1",
                usr_telefono=f"9{role.rol_id:08d}",
                usr_email=email,
                usr_contrasena=auth_utils.hash_password("Temporal123!"),
            )

        users = {
            "admin": user(ADMIN_EMAIL, roles["admin"]),
            "create": user(CREATE_EMAIL, roles["create"]),
            "assign": user(ASSIGN_EMAIL, roles["assign"]),
            "view": user(VIEW_EMAIL, roles["view"]),
            "none": user(NOPERM_EMAIL, roles["none"]),
        }
        db.add_all(list(users.values()))
        db.flush()

        # Catálogos y soporte.
        db.execute(text("INSERT INTO tbl_habilidad(hab_id, hab_nombre) VALUES (1,'Python'),(2,'PostgreSQL')"))
        db.execute(text("""
            INSERT INTO tbl_nivel_habilidad
                (nvhb_id,nvhb_nombre,nvhb_descripcion,nvhb_puntaje_base,nvhb_duracion)
            VALUES
                (2,'Trainee','QA',5,1),
                (3,'Junior','QA',15,1),
                (4,'Semi Senior','QA',30,3),
                (5,'Senior','QA',50,5)
        """))
        db.execute(text("""
            INSERT INTO tbl_estado_cuestionario_candidato(escc_id,escc_nombre)
            VALUES
                (1,'Asignado'),
                (2,'En Progreso'),
                (3,'Finalizado'),
                (4,'Vencido'),
                (5,'Cancelado'),
                (6,'Error Tecnico')
        """))
        db.execute(text("""
            INSERT INTO tbl_estado_solicitud_candidato(essc_id,essc_nombre)
            VALUES
                (1,'En revision'),
                (2,'En entrevista'),
                (3,'Inhabilitado'),
                (4,'Seleccionado'),
                (5,'Descartado'),
                (6,'Contratado')
        """))
        db.execute(text("INSERT INTO tbl_solicitud(sol_id,sol_codigo) VALUES (1,'SOL-000001'),(2,'SOL-000002'),(3,'SOL-000003')"))
        db.execute(text("INSERT INTO tbl_disponibilidad(disp_id,disp_nombre) VALUES (1,'Inmediata')"))
        db.execute(
            text("""
                INSERT INTO tbl_candidato(
                    cand_id,
                    cand_email,
                    cand_password,
                    cand_nombres,
                    cand_apellido_paterno,
                    cand_apellido_materno,
                    cand_fecha_nacimiento,
                    cand_telefono,
                    cand_rut_sin_dv,
                    cand_dv,
                    cand_disponibilidad_id,
                    cand_resumen_profesional,
                    cand_fecha_creacion,
                    cand_url_1,
                    cand_titulo,
                    cand_estado_usuario_id,
                    cand_cv_urls
                )
                VALUES
                    (
                        1,'candidate.one@sakura.cl','qa-hash','Candidate','One',NULL,
                        NULL,'911111111',30000001,1,1,'QA M4',CURRENT_TIMESTAMP,
                        NULL,'QA Candidate',:activo,NULL
                    ),
                    (
                        2,'candidate.two@sakura.cl','qa-hash','Candidate','Two',NULL,
                        NULL,'922222222',30000002,2,1,'QA M4',CURRENT_TIMESTAMP,
                        NULL,'QA Candidate',:activo,NULL
                    ),
                    (
                        3,'candidate.inactive@sakura.cl','qa-hash','Candidate','Inactive',NULL,
                        NULL,'933333333',30000003,3,1,'QA M4',CURRENT_TIMESTAMP,
                        NULL,'QA Candidate',:inactivo,NULL
                    )
            """),
            {"activo": activo.esusr_id, "inactivo": inactivo.esusr_id},
        )
        db.execute(text("""
            INSERT INTO tbl_solicitud_candidato
                (slcd_id,slcd_candidato_id,slcd_solicitud_id,slcd_estado_solicitud_candidato_id)
            VALUES
                (1,1,1,1),
                (2,2,1,1),
                (3,1,2,1)
        """))
        db.commit()

        return {
            "activo_id": activo.esusr_id,
            "admin_id": users["admin"].usr_id,
            "create_id": users["create"].usr_id,
            "assign_id": users["assign"].usr_id,
            "view_id": users["view"].usr_id,
            "none_id": users["none"].usr_id,
        }
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_database():
    _drop_schema()
    _create_schema()
    _seed()
    yield
    _drop_schema()


@pytest.fixture
def client():
    with TestClient(app_test) as c:
        yield c


def _token(user_id: int, email: str, principal_type: str = "usuario"):
    return auth_utils.create_access_token(
        {"sub": str(user_id), "email": email, "principal_type": principal_type}
    )


def _user_id(email: str):
    db = TestingSessionLocal()
    try:
        return db.scalar(select(user_models.Usuario.usr_id).where(user_models.Usuario.usr_email == email))
    finally:
        db.close()


@pytest.fixture
def admin_token():
    return _token(_user_id(ADMIN_EMAIL), ADMIN_EMAIL)


@pytest.fixture
def create_token():
    return _token(_user_id(CREATE_EMAIL), CREATE_EMAIL)


@pytest.fixture
def assign_token():
    return _token(_user_id(ASSIGN_EMAIL), ASSIGN_EMAIL)


@pytest.fixture
def view_token():
    return _token(_user_id(VIEW_EMAIL), VIEW_EMAIL)


@pytest.fixture
def noperm_token():
    return _token(_user_id(NOPERM_EMAIL), NOPERM_EMAIL)


@pytest.fixture
def candidate1_token():
    return _token(1, "candidate.one@sakura.cl", "candidato")


@pytest.fixture
def candidate2_token():
    return _token(2, "candidate.two@sakura.cl", "candidato")


def H(token):
    return {"Authorization": f"Bearer {token}"}


def _create_question(client, token, *, level_id=5, text_value="Pregunta QA", habilidad_id=1):
    r = client.post(
        "/preguntas",
        headers=H(token),
        json={
            "preg_texto_pregunta": text_value,
            "preg_habilidad_id": habilidad_id,
            "preg_nivel_habilidad_id": level_id,
        },
    )
    assert r.status_code == 201, r.text
    qid = r.json()["preg_id"]
    return qid


def _add_simple_options(client, token, question_id):
    r1 = client.post(
        f"/preguntas/{question_id}/opciones",
        headers=H(token),
        json={"opcr_texto_opcion": "Incorrecta", "opcr_es_correcta": False},
    )
    assert r1.status_code == 201, r1.text
    r2 = client.post(
        f"/preguntas/{question_id}/opciones",
        headers=H(token),
        json={"opcr_texto_opcion": "Correcta", "opcr_es_correcta": True},
    )
    assert r2.status_code == 201, r2.text
    return r1.json()["opcr_id"], r2.json()["opcr_id"]


def _create_questionnaire(client, token, *, solicitud_id=1, porcentaje=70, name="Cuestionario QA"):
    r = client.post(
        "/cuestionarios",
        headers=H(token),
        json={
            "cues_nombre": name,
            "cues_descripcion": "QA M4",
            "cues_porcentaje_aprobacion": porcentaje,
            "cues_solicitud_id": solicitud_id,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["cues_id"]


def _valid_questionnaire(client, token, *, solicitud_id=1, percentage=70):
    q1 = _create_question(client, token, level_id=5, text_value="Pregunta Senior")
    wrong1, correct1 = _add_simple_options(client, token, q1)
    q2 = _create_question(client, token, level_id=4, text_value="Pregunta Semi Senior")
    wrong2, correct2 = _add_simple_options(client, token, q2)
    questionnaire_id = _create_questionnaire(
        client, token, solicitud_id=solicitud_id, porcentaje=percentage
    )
    assert client.post(
        f"/cuestionarios/{questionnaire_id}/preguntas/{q1}", headers=H(token)
    ).status_code == 200
    assert client.post(
        f"/cuestionarios/{questionnaire_id}/preguntas/{q2}", headers=H(token)
    ).status_code == 200
    return {
        "questionnaire_id": questionnaire_id,
        "q1": q1,
        "q2": q2,
        "wrong1": wrong1,
        "correct1": correct1,
        "wrong2": wrong2,
        "correct2": correct2,
    }


def _assign(client, token, questionnaire_id, candidate_id=1, days=2):
    expires = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    r = client.post(
        f"/cuestionarios/{questionnaire_id}/asignar",
        headers=H(token),
        json={"candidato_id": candidate_id, "fecha_vencimiento": expires},
    )
    assert r.status_code == 201, r.text
    return r.json()["cdcu_id"]


def _future_expiration(days=2):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _assignment_count_db(questionnaire_id=None, candidate_id=None):
    db = TestingSessionLocal()
    try:
        stmt = select(m4_models.CandidatoCuestionario)
        if questionnaire_id is not None:
            stmt = stmt.where(
                m4_models.CandidatoCuestionario.cdcu_cuestionario_id == questionnaire_id
            )
        if candidate_id is not None:
            stmt = stmt.where(
                m4_models.CandidatoCuestionario.cdcu_candidato_id == candidate_id
            )
        return len(list(db.scalars(stmt)))
    finally:
        db.close()


# =============================================================================
# SEGURIDAD / RBAC
# =============================================================================

def test_internal_endpoint_sin_token_401(client):
    assert client.get("/preguntas").status_code == 401


def test_usuario_sin_permiso_403(client, noperm_token):
    assert client.get("/preguntas", headers=H(noperm_token)).status_code == 403


def test_cuest_create_administra_banco(client, create_token):
    qid = _create_question(client, create_token)
    assert client.get(f"/preguntas/{qid}", headers=H(create_token)).status_code == 200


def test_cuest_assign_no_administra_banco(client, assign_token):
    r = client.post(
        "/preguntas",
        headers=H(assign_token),
        json={"preg_texto_pregunta": "No", "preg_habilidad_id": 1, "preg_nivel_habilidad_id": 3},
    )
    assert r.status_code == 403


def test_cuest_view_consulta_cuestionarios(client, create_token, view_token):
    qid = _create_questionnaire(client, create_token)
    r = client.get(f"/cuestionarios/{qid}", headers=H(view_token))
    assert r.status_code == 200


def test_candidato_no_puede_usar_api_interna(client, candidate1_token, monkeypatch):
    # Este test solo necesita comprobar que una identidad de tipo candidato
    # es rechazada por require_permissions/get_current_user con HTTP 403.
    #
    # La carga ORM real de M3 usa selectinload de toda la ficha del candidato
    # (experiencias, estudios, cursos, habilidades, dirección, etc.). Replicar
    # todo M3 en el SQLite aislado de M4 no aporta valor a esta prueba puntual,
    # por lo que simulamos exclusivamente un candidato existente y activo.
    candidato_activo = SimpleNamespace(
        cand_id=1,
        estado=SimpleNamespace(esusr_nombre="Activo"),
    )

    monkeypatch.setattr(
        auth_dependencies,
        "_load_candidate",
        lambda db, candidate_id: candidato_activo if int(candidate_id) == 1 else None,
    )

    response = client.get("/preguntas", headers=H(candidate1_token))
    assert response.status_code == 403
    assert "usuario interno" in response.json()["detail"].lower()


def test_portal_candidato_sin_token_401(client):
    assert client.get("/cuestionarios/me").status_code == 401


def test_usuario_interno_no_puede_usar_portal_candidato(client, admin_token):
    assert client.get("/cuestionarios/me", headers=H(admin_token)).status_code == 403


# =============================================================================
# BANCO DE PREGUNTAS
# =============================================================================

def test_crud_pregunta(client, create_token):
    qid = _create_question(client, create_token)
    r = client.patch(
        f"/preguntas/{qid}",
        headers=H(create_token),
        json={"preg_texto_pregunta": "Pregunta editada", "preg_nivel_habilidad_id": 4},
    )
    assert r.status_code == 200
    assert r.json()["preg_texto_pregunta"] == "Pregunta editada"
    assert r.json()["puntaje_base"] == 30
    assert r.json()["duracion_minutos"] == 3
    assert client.delete(f"/preguntas/{qid}", headers=H(create_token)).status_code == 204
    assert client.get(f"/preguntas/{qid}", headers=H(create_token)).status_code == 404


def test_pregunta_habilidad_inexistente_422(client, create_token):
    r = client.post(
        "/preguntas",
        headers=H(create_token),
        json={"preg_texto_pregunta": "X", "preg_habilidad_id": 999, "preg_nivel_habilidad_id": 3},
    )
    assert r.status_code == 422


def test_pregunta_nivel_inexistente_422(client, create_token):
    r = client.post(
        "/preguntas",
        headers=H(create_token),
        json={"preg_texto_pregunta": "X", "preg_habilidad_id": 1, "preg_nivel_habilidad_id": 999},
    )
    assert r.status_code == 422


def test_filtros_preguntas(client, create_token):
    _create_question(client, create_token, level_id=5, text_value="Python Senior", habilidad_id=1)
    _create_question(client, create_token, level_id=3, text_value="PostgreSQL Junior", habilidad_id=2)
    r = client.get("/preguntas", headers=H(create_token), params={"habilidad_id": 2, "nivel_id": 3})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert "PostgreSQL" in r.json()[0]["preg_texto_pregunta"]


def test_opciones_crud_y_unica_correcta(client, create_token):
    qid = _create_question(client, create_token)
    wrong, correct = _add_simple_options(client, create_token, qid)
    r = client.post(
        f"/preguntas/{qid}/opciones",
        headers=H(create_token),
        json={"opcr_texto_opcion": "Otra correcta", "opcr_es_correcta": True},
    )
    assert r.status_code == 409

    r = client.patch(
        f"/preguntas/{qid}/opciones/{wrong}",
        headers=H(create_token),
        json={"opcr_texto_opcion": "Incorrecta editada"},
    )
    assert r.status_code == 200

    assert client.delete(
        f"/preguntas/{qid}/opciones/{wrong}", headers=H(create_token)
    ).status_code == 204


def test_no_agrega_pregunta_con_una_sola_opcion(client, create_token):
    qid = _create_question(client, create_token)
    client.post(
        f"/preguntas/{qid}/opciones",
        headers=H(create_token),
        json={"opcr_texto_opcion": "Una", "opcr_es_correcta": True},
    )
    cid = _create_questionnaire(client, create_token)
    r = client.post(f"/cuestionarios/{cid}/preguntas/{qid}", headers=H(create_token))
    assert r.status_code == 409


def test_no_agrega_pregunta_sin_correcta(client, create_token):
    qid = _create_question(client, create_token)
    for txt in ["A", "B"]:
        client.post(
            f"/preguntas/{qid}/opciones",
            headers=H(create_token),
            json={"opcr_texto_opcion": txt, "opcr_es_correcta": False},
        )
    cid = _create_questionnaire(client, create_token)
    r = client.post(f"/cuestionarios/{cid}/preguntas/{qid}", headers=H(create_token))
    assert r.status_code == 409


# =============================================================================
# CUESTIONARIOS / COMPOSICIÓN / MÉTRICAS
# =============================================================================

def test_cuestionario_solicitud_inexistente_422(client, create_token):
    r = client.post(
        "/cuestionarios",
        headers=H(create_token),
        json={
            "cues_nombre": "QA",
            "cues_descripcion": "QA",
            "cues_porcentaje_aprobacion": 70,
            "cues_solicitud_id": 999,
        },
    )
    assert r.status_code == 422


def test_metricas_calculadas_desde_nivel(client, create_token):
    data = _valid_questionnaire(client, create_token)
    r = client.get(f"/cuestionarios/{data['questionnaire_id']}", headers=H(create_token))
    assert r.status_code == 200
    body = r.json()
    assert body["cantidad_preguntas"] == 2
    assert body["puntaje_maximo"] == 80  # Senior 50 + Semi Senior 30
    assert body["duracion_minutos"] == 8  # Senior 5 + Semi Senior 3


def test_no_duplica_pregunta_en_cuestionario(client, create_token):
    qid = _create_question(client, create_token)
    _add_simple_options(client, create_token, qid)
    cid = _create_questionnaire(client, create_token)
    assert client.post(f"/cuestionarios/{cid}/preguntas/{qid}", headers=H(create_token)).status_code == 200
    assert client.post(f"/cuestionarios/{cid}/preguntas/{qid}", headers=H(create_token)).status_code == 409


def test_pregunta_usada_no_se_elimina(client, create_token):
    data = _valid_questionnaire(client, create_token)
    r = client.delete(f"/preguntas/{data['q1']}", headers=H(create_token))
    assert r.status_code == 409


def test_quitar_pregunta_antes_de_asignar(client, create_token):
    data = _valid_questionnaire(client, create_token)
    r = client.delete(
        f"/cuestionarios/{data['questionnaire_id']}/preguntas/{data['q2']}",
        headers=H(create_token),
    )
    assert r.status_code == 204
    r = client.get(f"/cuestionarios/{data['questionnaire_id']}", headers=H(create_token))
    assert r.json()["cantidad_preguntas"] == 1


def test_filtros_cuestionarios(client, create_token, view_token):
    _create_questionnaire(client, create_token, solicitud_id=1, name="Uno")
    _create_questionnaire(client, create_token, solicitud_id=2, name="Dos")
    r = client.get("/cuestionarios", headers=H(view_token), params={"solicitud_id": 2})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["cues_nombre"] == "Dos"


def test_eliminar_cuestionario_sin_asignaciones(client, create_token):
    cid = _create_questionnaire(client, create_token)
    assert client.delete(f"/cuestionarios/{cid}", headers=H(create_token)).status_code == 204


# =============================================================================
# ASIGNACIÓN
# =============================================================================

def test_no_asigna_cuestionario_sin_preguntas(client, create_token, assign_token):
    cid = _create_questionnaire(client, create_token)
    expires = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = client.post(
        f"/cuestionarios/{cid}/asignar",
        headers=H(assign_token),
        json={"candidato_id": 1, "fecha_vencimiento": expires},
    )
    assert r.status_code == 409


def test_no_asigna_candidato_fuera_solicitud(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token, solicitud_id=2)
    # candidato 2 solo está asociado a solicitud 1
    expires = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar",
        headers=H(assign_token),
        json={"candidato_id": 2, "fecha_vencimiento": expires},
    )
    assert r.status_code == 409


def test_asignacion_correcta_estado_asignado(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    r = client.get(f"/asignaciones-cuestionario/{aid}", headers=H(_token(_user_id(VIEW_EMAIL), VIEW_EMAIL)))
    assert r.status_code == 200
    assert r.json()["estado_nombre"] == "Asignado"
    assert r.json()["cdcu_fecha_inicio"] is None
    assert r.json()["duracion_minutos"] == 8


def test_no_asigna_con_vencimiento_pasado(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    expires = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar",
        headers=H(assign_token),
        json={"candidato_id": 1, "fecha_vencimiento": expires},
    )
    assert r.status_code == 422


def test_no_duplica_asignacion(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"])
    expires = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar",
        headers=H(assign_token),
        json={"candidato_id": 1, "fecha_vencimiento": expires},
    )
    assert r.status_code == 409


def test_no_elimina_cuestionario_asignado(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"])
    r = client.delete(f"/cuestionarios/{data['questionnaire_id']}", headers=H(create_token))
    assert r.status_code == 409


def test_no_quita_preguntas_despues_asignacion(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"])
    r = client.delete(
        f"/cuestionarios/{data['questionnaire_id']}/preguntas/{data['q2']}",
        headers=H(create_token),
    )
    assert r.status_code == 409


def test_filtros_asignaciones(client, create_token, assign_token, view_token):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"], candidate_id=1)
    r = client.get(
        "/asignaciones-cuestionario",
        headers=H(view_token),
        params={"candidato_id": 1, "estado_id": 1},
    )
    assert r.status_code == 200
    assert len(r.json()) == 1


# =============================================================================
# PORTAL CANDIDATO / PRIVACIDAD
# =============================================================================

def test_candidato_lista_solo_sus_asignaciones(client, create_token, assign_token, candidate1_token, candidate2_token):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"], candidate_id=1)
    _assign(client, assign_token, data["questionnaire_id"], candidate_id=2)
    r1 = client.get("/cuestionarios/me", headers=H(candidate1_token))
    r2 = client.get("/cuestionarios/me", headers=H(candidate2_token))
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert len(r1.json()) == 1
    assert len(r2.json()) == 1
    assert r1.json()[0]["cdcu_id"] != r2.json()[0]["cdcu_id"]


def test_candidato_no_ve_asignacion_ajena(client, create_token, assign_token, candidate2_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"], candidate_id=1)
    r = client.get(f"/cuestionarios/me/{aid}", headers=H(candidate2_token))
    assert r.status_code == 404


def test_preguntas_no_disponibles_antes_iniciar(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    r = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token))
    assert r.status_code == 409


def test_iniciar_registra_fecha_y_estado(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    r = client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "En Progreso"
    assert r.json()["fecha_inicio"] is not None


def test_no_inicia_dos_veces(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    assert client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token)).status_code == 200
    assert client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token)).status_code == 409


def test_preguntas_candidato_no_exponen_respuesta_correcta(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    r = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token))
    assert r.status_code == 200
    raw = r.text
    assert "opcr_es_correcta" not in raw
    assert "es_correcta" not in raw


# =============================================================================
# RESPUESTAS / CORRECCIÓN
# =============================================================================

def test_guardado_progresivo_y_upsert(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    questions = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()
    prcu = questions[0]["prcu_id"]

    r = client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": prcu, "opcion_respuesta_id": data["wrong1"]},
    )
    assert r.status_code == 200
    first_id = r.json()["rspr_id"]

    r = client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": prcu, "opcion_respuesta_id": data["correct1"]},
    )
    assert r.status_code == 200
    assert r.json()["rspr_id"] == first_id

    db = TestingSessionLocal()
    try:
        count = db.scalar(
            select(m4_models.RespuestaPregunta).where(
                m4_models.RespuestaPregunta.rspr_candidato_cuestionario_id == aid
            ).with_only_columns(text("count(*)"))
        )
        assert int(count) == 1
    finally:
        db.close()


def test_rechaza_pregunta_ajena(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    r = client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": 999999, "opcion_respuesta_id": data["correct1"]},
    )
    assert r.status_code == 422


def test_rechaza_opcion_de_otra_pregunta(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    qs = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()
    r = client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[0]["prcu_id"], "opcion_respuesta_id": data["correct2"]},
    )
    assert r.status_code == 422


def test_finalizacion_calcula_puntaje_ponderado_y_aprueba(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token, percentage=60)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    qs = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()

    # Senior correcta = 50, Semi Senior incorrecta = 0, total 50/80 = 62.50%
    client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[0]["prcu_id"], "opcion_respuesta_id": data["correct1"]},
    )
    client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[1]["prcu_id"], "opcion_respuesta_id": data["wrong2"]},
    )
    r = client.post(f"/cuestionarios/me/{aid}/finalizar", headers=H(candidate1_token))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["puntaje_obtenido"] == 50
    assert body["puntaje_maximo"] == 80
    assert Decimal(str(body["porcentaje_obtenido"])) == Decimal("62.50")
    assert body["aprobado"] is True
    assert body["estado"] == "Finalizado"


def test_finalizacion_reprobada_no_habilita_reintento(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token, percentage=90)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    qs = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()
    client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[0]["prcu_id"], "opcion_respuesta_id": data["wrong1"]},
    )
    r = client.post(f"/cuestionarios/me/{aid}/finalizar", headers=H(candidate1_token))
    assert r.status_code == 200
    assert r.json()["aprobado"] is False

    r = client.post(
        f"/asignaciones-cuestionario/{aid}/habilitar-reintento",
        headers=H(assign_token),
        json={
            "fecha_vencimiento": (
                datetime.now(timezone.utc) + timedelta(days=2)
            ).isoformat()
        },
    )
    assert r.status_code == 409


def test_no_responde_despues_finalizado(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    qs = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()
    client.post(f"/cuestionarios/me/{aid}/finalizar", headers=H(candidate1_token))
    r = client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[0]["prcu_id"], "opcion_respuesta_id": data["correct1"]},
    )
    assert r.status_code == 409


def test_resultado_interno_detalla_correcta_y_seleccionada(client, create_token, assign_token, view_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    qs = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()
    client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[0]["prcu_id"], "opcion_respuesta_id": data["wrong1"]},
    )
    client.post(f"/cuestionarios/me/{aid}/finalizar", headers=H(candidate1_token))
    r = client.get(f"/asignaciones-cuestionario/{aid}/resultado", headers=H(view_token))
    assert r.status_code == 200
    assert len(r.json()["respuestas"]) == 1
    assert r.json()["respuestas"][0]["es_correcta"] is False
    assert r.json()["respuestas"][0]["opcion_correcta"] == "Correcta"


# =============================================================================
# VENCIMIENTO / CRONÓMETRO
# =============================================================================

def test_asignado_vencido_pasa_a_vencido(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    db = TestingSessionLocal()
    try:
        a = db.get(m4_models.CandidatoCuestionario, aid)
        a.cdcu_fecha_vencimiento = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()

    r = client.get(f"/cuestionarios/me/{aid}", headers=H(candidate1_token))
    assert r.status_code == 200
    assert r.json()["estado"] == "Vencido"


def test_no_inicia_vencido(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    db = TestingSessionLocal()
    try:
        a = db.get(m4_models.CandidatoCuestionario, aid)
        a.cdcu_fecha_vencimiento = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()
    r = client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    assert r.status_code == 409


def test_limite_tiempo_finaliza_automaticamente(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    assert client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token)).status_code == 200

    db = TestingSessionLocal()
    try:
        a = db.get(m4_models.CandidatoCuestionario, aid)
        # Duración total 8 min; forzamos 9 min transcurridos.
        a.cdcu_fecha_inicio = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=9)
        db.commit()
    finally:
        db.close()

    r = client.get(f"/cuestionarios/me/{aid}", headers=H(candidate1_token))
    assert r.status_code == 200
    assert r.json()["estado"] == "Finalizado"
    assert r.json()["tiempo_utilizado"] == 8


# =============================================================================
# CANCELACIÓN / ERROR TÉCNICO / REINTENTO
# =============================================================================

def test_cancelar_asignado(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    r = client.post(f"/asignaciones-cuestionario/{aid}/cancelar", headers=H(assign_token))
    assert r.status_code == 200
    assert r.json()["estado_nombre"] == "Cancelado"


def test_error_tecnico_en_progreso(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    r = client.post(f"/asignaciones-cuestionario/{aid}/error-tecnico", headers=H(assign_token))
    assert r.status_code == 200
    assert r.json()["estado_nombre"] == "Error Tecnico"
    assert r.json()["cdcu_permitir_reintento"] is False


def test_reintento_solo_desde_error_tecnico(client, create_token, assign_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    r = client.post(
        f"/asignaciones-cuestionario/{aid}/habilitar-reintento",
        headers=H(assign_token),
        json={"fecha_vencimiento": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()},
    )
    assert r.status_code == 409


def test_habilitar_reintento_limpia_respuestas_y_resultado(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    qs = client.get(f"/cuestionarios/me/{aid}/preguntas", headers=H(candidate1_token)).json()
    client.put(
        f"/cuestionarios/me/{aid}/respuesta",
        headers=H(candidate1_token),
        json={"pregunta_cuestionario_id": qs[0]["prcu_id"], "opcion_respuesta_id": data["correct1"]},
    )

    assert client.post(
        f"/asignaciones-cuestionario/{aid}/error-tecnico", headers=H(assign_token)
    ).status_code == 200
    r = client.post(
        f"/asignaciones-cuestionario/{aid}/habilitar-reintento",
        headers=H(assign_token),
        json={"fecha_vencimiento": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["estado_nombre"] == "Asignado"
    assert body["cdcu_fecha_inicio"] is None
    assert body["cdcu_fecha_resolucion"] is None
    assert body["cdcu_porcentaje_obtenido"] is None
    assert body["cdcu_aprobado"] is None
    assert body["cdcu_permitir_reintento"] is True

    db = TestingSessionLocal()
    try:
        count = db.scalar(
            select(m4_models.RespuestaPregunta).where(
                m4_models.RespuestaPregunta.rspr_candidato_cuestionario_id == aid
            ).with_only_columns(text("count(*)"))
        )
        assert int(count) == 0
    finally:
        db.close()

    assert client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token)).status_code == 200


def test_error_tecnico_no_se_declara_finalizado(client, create_token, assign_token, candidate1_token):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"])
    client.post(f"/cuestionarios/me/{aid}/iniciar", headers=H(candidate1_token))
    client.post(f"/cuestionarios/me/{aid}/finalizar", headers=H(candidate1_token))
    r = client.post(f"/asignaciones-cuestionario/{aid}/error-tecnico", headers=H(assign_token))
    assert r.status_code == 409


# =============================================================================
# VALIDACIONES SCHEMA / CAMPOS EXTRA
# =============================================================================

def test_extra_field_rechazado_pregunta(client, create_token):
    r = client.post(
        "/preguntas",
        headers=H(create_token),
        json={
            "preg_texto_pregunta": "QA",
            "preg_habilidad_id": 1,
            "preg_nivel_habilidad_id": 3,
            "campo_extra": True,
        },
    )
    assert r.status_code == 422


def test_porcentaje_aprobacion_fuera_rango_422(client, create_token):
    r = client.post(
        "/cuestionarios",
        headers=H(create_token),
        json={
            "cues_nombre": "QA",
            "cues_descripcion": "QA",
            "cues_porcentaje_aprobacion": 101,
            "cues_solicitud_id": 1,
        },
    )
    assert r.status_code == 422


def test_patch_vacio_422(client, create_token):
    qid = _create_question(client, create_token)
    assert client.patch(f"/preguntas/{qid}", headers=H(create_token), json={}).status_code == 422
# =============================================================================
# CANDIDATOS DISPONIBLES / ASIGNACION MASIVA
# =============================================================================

def test_candidatos_disponibles_requiere_token(client):
    r = client.get("/cuestionarios/1/candidatos-disponibles")
    assert r.status_code == 401


def test_candidatos_disponibles_requiere_view_o_assign(
    client, create_token, noperm_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.get(
        f"/cuestionarios/{data['questionnaire_id']}/candidatos-disponibles",
        headers=H(noperm_token),
    )
    assert r.status_code == 403


def test_candidatos_disponibles_permite_cuest_view(
    client, create_token, view_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.get(
        f"/cuestionarios/{data['questionnaire_id']}/candidatos-disponibles",
        headers=H(view_token),
    )
    assert r.status_code == 200, r.text


def test_candidatos_disponibles_permite_cuest_assign(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.get(
        f"/cuestionarios/{data['questionnaire_id']}/candidatos-disponibles",
        headers=H(assign_token),
    )
    assert r.status_code == 200, r.text


def test_candidatos_disponibles_solo_misma_solicitud(
    client, create_token, view_token
):
    data = _valid_questionnaire(client, create_token, solicitud_id=1)
    r = client.get(
        f"/cuestionarios/{data['questionnaire_id']}/candidatos-disponibles",
        headers=H(view_token),
    )
    assert r.status_code == 200, r.text
    ids = {item["cand_id"] for item in r.json()}
    # Solicitud 1 tiene candidatos 1 y 2. Candidato 3 no está asociado.
    assert ids == {1, 2}


def test_candidatos_disponibles_informa_asignacion_existente(
    client, create_token, assign_token, view_token
):
    data = _valid_questionnaire(client, create_token)
    aid = _assign(client, assign_token, data["questionnaire_id"], candidate_id=1)

    r = client.get(
        f"/cuestionarios/{data['questionnaire_id']}/candidatos-disponibles",
        headers=H(view_token),
    )
    assert r.status_code == 200, r.text
    by_id = {item["cand_id"]: item for item in r.json()}

    assert by_id[1]["cuestionario_asignado"] is True
    assert by_id[1]["asignacion_id"] == aid
    assert by_id[1]["estado_cuestionario"] == "Asignado"

    assert by_id[2]["cuestionario_asignado"] is False
    assert by_id[2]["asignacion_id"] is None
    assert by_id[2]["estado_cuestionario"] is None


def test_asignar_masivo_requiere_cuest_assign(
    client, create_token, view_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(view_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 403


def test_asignar_masivo_dos_candidatos_validos(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["cuestionario_id"] == data["questionnaire_id"]
    assert body["solicitud_id"] == 1
    assert body["total_candidatos_solicitud"] == 2
    assert body["total_solicitados"] == 2
    assert body["total_asignados"] == 2
    assert body["total_omitidos_ya_asignados"] == 0
    assert len(body["asignaciones"]) == 2
    assert {a["cdcu_candidato_id"] for a in body["asignaciones"]} == {1, 2}
    assert all(a["estado_nombre"] == "Asignado" for a in body["asignaciones"])
    assert _assignment_count_db(data["questionnaire_id"]) == 2


def test_asignar_masivo_rechaza_lista_vacia(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 422


def test_asignar_masivo_rechaza_ids_duplicados(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 1],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 422
    assert _assignment_count_db(data["questionnaire_id"]) == 0


def test_asignar_masivo_rechaza_vencimiento_pasado(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": (
                datetime.now(timezone.utc) - timedelta(minutes=1)
            ).isoformat(),
        },
    )
    assert r.status_code == 422
    assert _assignment_count_db(data["questionnaire_id"]) == 0


def test_asignar_masivo_rechaza_candidato_otra_solicitud_y_es_atomico(
    client, create_token, assign_token
):
    # Cuestionario de solicitud 2. Candidato 1 pertenece a solicitud 2,
    # candidato 2 no pertenece a solicitud 2.
    data = _valid_questionnaire(client, create_token, solicitud_id=2)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 409, r.text
    # Atomicidad: candidato 1 tampoco queda asignado.
    assert _assignment_count_db(data["questionnaire_id"]) == 0


def test_asignar_masivo_rechaza_candidato_inexistente_y_es_atomico(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 99999],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 409
    assert _assignment_count_db(data["questionnaire_id"]) == 0


def test_asignar_masivo_rechaza_si_un_candidato_ya_tiene_cuestionario_y_es_atomico(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"], candidate_id=1)
    assert _assignment_count_db(data["questionnaire_id"]) == 1

    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 409, r.text

    # No debe crear parcialmente la asignación del candidato 2.
    assert _assignment_count_db(data["questionnaire_id"]) == 1
    assert _assignment_count_db(
        data["questionnaire_id"], candidate_id=2
    ) == 0


def test_asignar_masivo_rechaza_cuestionario_sin_preguntas(
    client, create_token, assign_token
):
    cid = _create_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{cid}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 409
    assert _assignment_count_db(cid) == 0


def test_asignar_todos_requiere_cuest_assign(
    client, create_token, view_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(view_token),
        json={"fecha_vencimiento": _future_expiration()},
    )
    assert r.status_code == 403


def test_asignar_todos_asigna_todos_los_candidatos_de_solicitud(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token, solicitud_id=1)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(assign_token),
        json={"fecha_vencimiento": _future_expiration()},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["total_candidatos_solicitud"] == 2
    assert body["total_solicitados"] == 2
    assert body["total_asignados"] == 2
    assert body["total_omitidos_ya_asignados"] == 0
    assert {a["cdcu_candidato_id"] for a in body["asignaciones"]} == {1, 2}
    assert _assignment_count_db(data["questionnaire_id"]) == 2


def test_asignar_todos_omite_ya_asignados_sin_duplicar(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    _assign(client, assign_token, data["questionnaire_id"], candidate_id=1)

    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(assign_token),
        json={"fecha_vencimiento": _future_expiration()},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["total_candidatos_solicitud"] == 2
    assert body["total_asignados"] == 1
    assert body["total_omitidos_ya_asignados"] == 1
    assert len(body["asignaciones"]) == 1
    assert body["asignaciones"][0]["cdcu_candidato_id"] == 2
    assert _assignment_count_db(data["questionnaire_id"]) == 2


def test_asignar_todos_repetido_no_duplica_y_reporta_todos_omitidos(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    first = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(assign_token),
        json={"fecha_vencimiento": _future_expiration()},
    )
    assert first.status_code == 201
    assert _assignment_count_db(data["questionnaire_id"]) == 2

    second = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(assign_token),
        json={"fecha_vencimiento": _future_expiration(days=3)},
    )
    assert second.status_code == 201, second.text
    body = second.json()
    assert body["total_asignados"] == 0
    assert body["total_omitidos_ya_asignados"] == 2
    assert body["asignaciones"] == []
    assert _assignment_count_db(data["questionnaire_id"]) == 2


def test_asignar_todos_rechaza_solicitud_sin_candidatos(
    client, create_token, assign_token
):
    # Solicitud 3 no tiene filas en tbl_solicitud_candidato.
    data = _valid_questionnaire(client, create_token, solicitud_id=3)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(assign_token),
        json={"fecha_vencimiento": _future_expiration()},
    )
    assert r.status_code == 409
    assert _assignment_count_db(data["questionnaire_id"]) == 0


def test_asignar_todos_rechaza_vencimiento_pasado(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-todos",
        headers=H(assign_token),
        json={
            "fecha_vencimiento": (
                datetime.now(timezone.utc) - timedelta(minutes=1)
            ).isoformat()
        },
    )
    assert r.status_code == 422
    assert _assignment_count_db(data["questionnaire_id"]) == 0


def test_asignaciones_masivas_aparecen_en_portal_candidato(
    client, create_token, assign_token, candidate1_token, candidate2_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 201

    r1 = client.get("/cuestionarios/me", headers=H(candidate1_token))
    r2 = client.get("/cuestionarios/me", headers=H(candidate2_token))
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert any(
        item["cuestionario_id"] == data["questionnaire_id"]
        for item in r1.json()
    )
    assert any(
        item["cuestionario_id"] == data["questionnaire_id"]
        for item in r2.json()
    )


def test_asignar_masivo_no_acepta_candidato_id_cero(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [0, 1],
            "fecha_vencimiento": _future_expiration(),
        },
    )
    assert r.status_code == 422


def test_asignar_masivo_rechaza_campos_extra(
    client, create_token, assign_token
):
    data = _valid_questionnaire(client, create_token)
    r = client.post(
        f"/cuestionarios/{data['questionnaire_id']}/asignar-masivo",
        headers=H(assign_token),
        json={
            "candidato_ids": [1, 2],
            "fecha_vencimiento": _future_expiration(),
            "campo_extra": "no permitido",
        },
    )
    assert r.status_code == 422
