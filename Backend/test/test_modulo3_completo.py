from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Iterator

os.environ.setdefault("JWT_SECRET_KEY", "qa-modulo3-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz")
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

from app.auth import router as auth_router
from app.auth import utils as auth_utils
from app.catalogos import models as catalog_models
from app.clientes import models as cliente_models
from app.database import Base, get_db
from app.candidatos import models as candidate_models
from app.candidatos import router as candidate_router
from app.solicitudes import models as solicitud_models
from app.solicitudes import router as solicitud_router
from app.usuarios import models as user_models


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(TEST_ENGINE, "connect")
def _sqlite_fk(dbapi_connection, _record):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

app_test = FastAPI(title="QA Módulo 3")
app_test.include_router(auth_router.router)
app_test.include_router(candidate_router.router)
app_test.include_router(solicitud_router.router)


def override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app_test.dependency_overrides[get_db] = override_get_db

PERMISSIONS = ["CAN_VIEW", "CAN_UPDATE", "CAN_DELETE", "SOL_VIEW", "SOL_UPDATE", "SOL_DELETE"]
ADMIN_EMAIL = "admin.m3@sakura.cl"
ADMIN_PASSWORD = "AdminM3QA123!"
VIEW_EMAIL = "view.m3@sakura.cl"
UPDATE_EMAIL = "update.m3@sakura.cl"
NO_PERM_EMAIL = "noperm.m3@sakura.cl"
CANDIDATE_PASSWORD = "CandidateQA123!"


class SeedInfo(dict):
    pass


def _mk_user(db: Session, role, state, area, seq: int, email: str):
    obj = user_models.Usuario(
        usr_rol_id=role.rol_id,
        usr_estado_usuario_id=state.esusr_id,
        usr_area_id=area.area_id,
        usr_nombres=f"QA{seq}",
        usr_apellido_paterno="ModuloTres",
        usr_apellido_materno=None,
        usr_rut_sin_dv=f"3100000{seq}",
        usr_dv=str(seq % 10),
        usr_telefono=f"9111111{seq:02d}",
        usr_email=email,
        usr_contrasena=auth_utils.hash_password(ADMIN_PASSWORD),
    )
    db.add(obj)
    db.flush()
    return obj


def _seed_database() -> SeedInfo:
    db = TestingSessionLocal()
    try:
        activo = user_models.EstadoUsuario(esusr_nombre="Activo", esusr_descripcion="Activo")
        inactivo = user_models.EstadoUsuario(esusr_nombre="Inactivo", esusr_descripcion="Inactivo")
        eliminado = user_models.EstadoUsuario(esusr_nombre="Eliminado", esusr_descripcion="Eliminado")
        area = user_models.Area(area_nombre="QA M3", area_descripcion="QA")
        db.add_all([activo, inactivo, eliminado, area]); db.flush()

        perms = {p: user_models.Permiso(per_nombre=p, per_descripcion=f"QA {p}") for p in PERMISSIONS}
        db.add_all(perms.values()); db.flush()

        def role(name: str, names: list[str]):
            r = user_models.Rol(rol_nombre=name, rol_descripcion=f"QA {name}", permisos=[perms[n] for n in names])
            db.add(r); db.flush(); return r

        admin_role = role("Administrador", PERMISSIONS)
        view_role = role("M3View", ["CAN_VIEW"])
        update_role = role("M3Update", ["CAN_UPDATE"])
        no_perm_role = role("M3NoPerm", [])
        admin = _mk_user(db, admin_role, activo, area, 1, ADMIN_EMAIL)
        viewer = _mk_user(db, view_role, activo, area, 2, VIEW_EMAIL)
        updater = _mk_user(db, update_role, activo, area, 3, UPDATE_EMAIL)
        noperm = _mk_user(db, no_perm_role, activo, area, 4, NO_PERM_EMAIL)

        pais = catalog_models.Pais(pais_nombre="Chile")
        db.add(pais); db.flush()
        region = catalog_models.Region(reg_pais_id=pais.pais_id, reg_nombre="Metropolitana")
        db.add(region); db.flush()
        comuna = catalog_models.Comuna(com_region_id=region.reg_id, com_nombre="Santiago")
        db.add(comuna)

        tipo_inst = catalog_models.TipoInstitucion(tint_tipo_institucion="Universidad")
        db.add(tipo_inst); db.flush()
        institucion = catalog_models.Institucion(inst_nombre="Universidad QA", inst_tipo_institucion_id=tipo_inst.tint_id)
        carrera = catalog_models.Carrera(crra_nombre="Ingenieria QA")
        nivel_edu = catalog_models.NivelEducacional(nved_nombre="Profesional")
        idioma_ingles = catalog_models.Idioma(idio_nombre="Inglés")
        nivel_idioma_intermedio = catalog_models.NivelIdioma(
            nvid_codigo="INT", nvid_nombre="Intermedio", nvid_grupo="Intermedio", nvid_orden=1
        )
        nivel_idioma_avanzado = catalog_models.NivelIdioma(
            nvid_codigo="AVA", nvid_nombre="Avanzado", nvid_grupo="Avanzado", nvid_orden=2
        )
        h_python = catalog_models.Habilidad(hab_nombre="Python", hab_descripcion="Python")
        h_fastapi = catalog_models.Habilidad(hab_nombre="FastAPI", hab_descripcion="FastAPI")
        n_junior = catalog_models.NivelHabilidad(nvhb_nombre="Junior", nvhb_descripcion="J", nvhb_puntaje_base=10, nvhb_duracion=1)
        n_senior = catalog_models.NivelHabilidad(nvhb_nombre="Senior", nvhb_descripcion="S", nvhb_puntaje_base=30, nvhb_duracion=1)
        cargo = catalog_models.Cargo(crgo_nombre="Backend QA", crgo_descripcion="Backend")
        modalidad = catalog_models.Modalidad(mdld_nombre="Remoto", mdld_descripcion="Remoto")
        contrato = catalog_models.TipoContrato(tpct_nombre="Indefinido", tpct_descripcion="Indef")
        disp = catalog_models.Disponibilidad(disp_nombre="Inmediata")
        prioridad = catalog_models.PrioridadSolicitud(prsol_nombre="Alta", prsol_descripcion="Alta")
        db.add_all([institucion, carrera, nivel_edu, idioma_ingles, nivel_idioma_intermedio, nivel_idioma_avanzado, h_python, h_fastapi, n_junior, n_senior, cargo, modalidad, contrato, disp, prioridad]); db.flush()

        sol_states = {}
        for name in ["Pendiente", "En Publicacion", "En Entrevistas", "Cancelado", "Cerrado", "Pausado"]:
            s = catalog_models.EstadoSolicitud(essl_nombre=name, essl_descripcion=name)
            db.add(s); db.flush(); sol_states[name] = s.essl_id

        cand_states = {}
        for name in ["En revision", "En entrevista", "Inhabilitado", "Seleccionado", "Descartado", "Contratado"]:
            s = catalog_models.EstadoSolicitudCandidato(essc_nombre=name, essc_descripcion=name)
            db.add(s); db.flush(); cand_states[name] = s.essc_id

        motivo = catalog_models.MotivoRechazo(mtrc_nombre="No cumple", mtrc_descripcion="QA")
        empresa = cliente_models.Empresa(emp_nombre="Empresa QA", emp_identificacion="M3-QA-001")
        db.add_all([motivo, empresa]); db.flush()
        cliente = cliente_models.Cliente(cli_nombre="Cliente QA", cli_empresa_id=empresa.emp_id, cli_email="cliente.m3@sakura.cl")
        db.add(cliente); db.flush()

        solicitud = solicitud_models.Solicitud(
            sol_codigo="SOL-900001",
            sol_titulo="Solicitud QA M3",
            sol_descripcion="QA",
            sol_cantidad_vacantes=2,
            sol_fecha_creacion=datetime.utcnow(),
            sol_cargo_id=cargo.crgo_id,
            sol_prioridad_id=prioridad.prsol_id,
            sol_cliente_id=cliente.cli_id,
            sol_usuario_creador_id=admin.usr_id,
            sol_usuario_asignado_id=admin.usr_id,
            sol_modalidad_id=modalidad.mdld_id,
            sol_estado_solicitud_id=sol_states["En Entrevistas"],
            sol_tipo_contrato_id=contrato.tpct_id,
        )
        solicitud.habilidades = [
            solicitud_models.SolicitudHabilidad(
                solhb_habilidad_id=h_python.hab_id,
                solhb_nivel_habilidad_id=n_senior.nvhb_id,
                solhb_anios_experiencia_req=3,
                solhb_es_excluyente=True,
            )
        ]
        db.add(solicitud); db.commit()

        return SeedInfo(
            activo_id=activo.esusr_id, inactivo_id=inactivo.esusr_id, eliminado_id=eliminado.esusr_id,
            admin_id=admin.usr_id, viewer_id=viewer.usr_id, updater_id=updater.usr_id, noperm_id=noperm.usr_id,
            comuna_id=comuna.com_id, institucion_id=institucion.inst_id, carrera_id=carrera.crra_id,
            nivel_edu_id=nivel_edu.nved_id, python_id=h_python.hab_id, fastapi_id=h_fastapi.hab_id,
            junior_id=n_junior.nvhb_id, senior_id=n_senior.nvhb_id, cargo_id=cargo.crgo_id,
            disponibilidad_id=disp.disp_id, empresa_id=empresa.emp_id, motivo_id=motivo.mtrc_id,
            solicitud_id=solicitud.sol_id, sol_states=sol_states, cand_states=cand_states,
        )
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_database(tmp_path, monkeypatch):
    monkeypatch.setenv("CANDIDATE_CV_STORAGE_DIR", str(tmp_path / "cv"))
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)
    app_test.state.seed = _seed_database()
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app_test) as c:
        yield c


@pytest.fixture
def seed() -> SeedInfo:
    return app_test.state.seed


def _headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def _login(client: TestClient, email: str, password: str) -> dict:
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture
def admin_token(client: TestClient):
    return _login(client, ADMIN_EMAIL, ADMIN_PASSWORD)["access_token"]


@pytest.fixture
def view_token(client: TestClient):
    return _login(client, VIEW_EMAIL, ADMIN_PASSWORD)["access_token"]


@pytest.fixture
def update_token(client: TestClient):
    return _login(client, UPDATE_EMAIL, ADMIN_PASSWORD)["access_token"]


@pytest.fixture
def no_perm_token(client: TestClient):
    return _login(client, NO_PERM_EMAIL, ADMIN_PASSWORD)["access_token"]


def _candidate_payload(seed: SeedInfo, email="candidate.qa@sakura.cl", *, password=None, include_nested=False):
    data = {
        "cand_email": email,
        "cand_nombres": "Carla",
        "cand_apellido_paterno": "QA",
        "cand_apellido_materno": "Sakura",
        "cand_telefono": "912345678",
        "cand_disponibilidad_id": seed["disponibilidad_id"],
        "cand_resumen_profesional": "Profesional QA para pruebas automatizadas del modulo tres.",
        "cand_url_1": ["https://linkedin.com/in/carla", "https://github.com/carla", "https://github.com/carla"],
        "cand_titulo": "Ingeniera QA",
        "cand_cv_urls": ["cv/a.pdf", "cv/b.pdf", "cv/a.pdf"],
    }
    if password is not None:
        data["password_inicial"] = password
    if include_nested:
        data.update({
            "direccion": {"drcd_comuna_id": seed["comuna_id"], "drcd_calle": "Calle QA", "drcd_numero": 123},
            "habilidades": [{"cdhb_habilidad_id": seed["python_id"], "cdhb_nivel_habilidad_id": seed["senior_id"], "cdhb_anios_experiencia": 5}],
            "estudios": [{"etcd_nivel_educacional_id": seed["nivel_edu_id"], "etcd_institucion_id": seed["institucion_id"], "etcd_carrera_id": seed["carrera_id"]}],
            "experiencias": [{"expl_empresa_id": seed["empresa_id"], "expl_cargo_id": seed["cargo_id"], "expl_descripcion_funciones": "Backend QA", "habilidades_ids": [seed["python_id"]]}],
            "cursos": [{"curs_nombre_curso": "Curso QA", "curs_institucion_id": seed["institucion_id"], "curs_es_certificado": True, "curs_anio_curso": 2026}],
        })
    return data


def _create_candidate(client, token, seed, email="candidate.qa@sakura.cl", **kwargs):
    payload = _candidate_payload(seed, email=email, **kwargs)
    r = client.post("/candidatos", headers=_headers(token), json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def _associate(client, token, seed, cand_id, **payload):
    r = client.post(
        f"/solicitudes/{seed['solicitud_id']}/candidatos/{cand_id}",
        headers=_headers(token), json=payload,
    )
    assert r.status_code == 201, r.text
    return r.json()


# ---------------- RBAC / CRUD ----------------
def test_candidatos_sin_token_401(client):
    assert client.get("/candidatos").status_code == 401


def test_candidatos_sin_permiso_403(client, no_perm_token):
    assert client.get("/candidatos", headers=_headers(no_perm_token)).status_code == 403


def test_can_view_lista_pero_no_crea(client, view_token, seed):
    assert client.get("/candidatos", headers=_headers(view_token)).status_code == 200
    assert client.post("/candidatos", headers=_headers(view_token), json=_candidate_payload(seed)).status_code == 403


def test_can_update_crea_candidato(client, update_token, seed):
    body = _create_candidate(client, update_token, seed)
    assert body["candidato"]["cand_email"] == "candidate.qa@sakura.cl"
    assert body["password_temporal"]
    assert "cand_password" not in body["candidato"]


def test_create_password_explicita_no_retorna_temporal(client, update_token, seed):
    body = _create_candidate(client, update_token, seed, password=CANDIDATE_PASSWORD)
    assert body["password_temporal"] is None


def test_create_normaliza_dv_y_urls(client, update_token, seed):
    payload = _candidate_payload(seed)
    payload["cand_rut_sin_dv"] = 22000001
    payload["cand_dv"] = "K"
    r = client.post("/candidatos", headers=_headers(update_token), json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    c = body["candidato"]
    assert c["cand_dv"] == 10
    assert c["cand_url_1"] == "https://linkedin.com/in/carla;https://github.com/carla"
    assert c["cand_cv_urls"] == "cv/a.pdf;cv/b.pdf"


def test_create_con_nested_completo(client, update_token, seed):
    body = _create_candidate(client, update_token, seed, include_nested=True)
    c = body["candidato"]
    assert c["direccion"]["drcd_comuna_id"] == seed["comuna_id"]
    assert len(c["habilidades"]) == len(c["estudios"]) == len(c["experiencias"]) == len(c["cursos"]) == 1
    assert c["experiencias"][0]["habilidades_ids"] == [seed["python_id"]]


def test_email_usuario_interno_no_puede_ser_candidato(client, update_token, seed):
    r = client.post("/candidatos", headers=_headers(update_token), json=_candidate_payload(seed, email=ADMIN_EMAIL))
    assert r.status_code == 409


def test_email_candidato_duplicado_409(client, update_token, seed):
    _create_candidate(client, update_token, seed)
    r = client.post("/candidatos", headers=_headers(update_token), json=_candidate_payload(seed))
    assert r.status_code == 409


def test_rut_incompleto_422(client, update_token, seed):
    p = _candidate_payload(seed); p["cand_rut_sin_dv"] = 22000001
    assert client.post("/candidatos", headers=_headers(update_token), json=p).status_code == 422


def test_disponibilidad_inexistente_422(client, update_token, seed):
    p = _candidate_payload(seed); p["cand_disponibilidad_id"] = 999999
    assert client.post("/candidatos", headers=_headers(update_token), json=p).status_code == 422


def test_nested_fk_inexistente_422(client, update_token, seed):
    p = _candidate_payload(seed, include_nested=True); p["habilidades"][0]["cdhb_habilidad_id"] = 999999
    assert client.post("/candidatos", headers=_headers(update_token), json=p).status_code == 422


def test_get_patch_put_list_filtros(client, admin_token, seed):
    body = _create_candidate(client, admin_token, seed, include_nested=True)
    cid = body["candidato"]["cand_id"]
    assert client.get(f"/candidatos/{cid}", headers=_headers(admin_token)).status_code == 200
    r = client.patch(f"/candidatos/{cid}", headers=_headers(admin_token), json={"cand_titulo": "Arquitecta QA"})
    assert r.status_code == 200 and r.json()["cand_titulo"] == "Arquitecta QA"
    rep = _candidate_payload(seed, password=None); rep.pop("password_inicial", None); rep["cand_titulo"] = "Reemplazo QA"
    r = client.put(f"/candidatos/{cid}", headers=_headers(admin_token), json=rep)
    assert r.status_code == 200 and r.json()["cand_titulo"] == "Reemplazo QA"
    listing = client.get("/candidatos", headers=_headers(admin_token), params={"q": "candidate.qa", "habilidad_id": seed["python_id"], "limit": 100})
    assert listing.status_code == 200 and any(x["cand_id"] == cid for x in listing.json())


def test_patch_vacio_422(client, admin_token, seed):
    cid = _create_candidate(client, admin_token, seed)["candidato"]["cand_id"]
    assert client.patch(f"/candidatos/{cid}", headers=_headers(admin_token), json={}).status_code == 422


def test_delete_es_logico_y_login_queda_bloqueado(client, admin_token, seed):
    body = _create_candidate(client, admin_token, seed, password=CANDIDATE_PASSWORD)
    cid = body["candidato"]["cand_id"]
    assert client.delete(f"/candidatos/{cid}", headers=_headers(admin_token)).status_code == 204
    detail = client.get(f"/candidatos/{cid}", headers=_headers(admin_token))
    assert detail.status_code == 200 and detail.json()["cand_estado_usuario_id"] == seed["eliminado_id"]
    assert client.post("/auth/login", json={"email": "candidate.qa@sakura.cl", "password": CANDIDATE_PASSWORD}).status_code == 403


# ---------------- autenticación candidato ----------------
def test_login_candidato_y_auth_me(client, admin_token, seed):
    _create_candidate(client, admin_token, seed, password=CANDIDATE_PASSWORD)
    login = _login(client, "candidate.qa@sakura.cl", CANDIDATE_PASSWORD)
    assert login["principal_type"] == "candidato"
    r = client.get("/auth/me", headers=_headers(login["access_token"]))
    assert r.status_code == 200 and r.json()["principal_type"] == "candidato"


def test_candidato_me(client, admin_token, seed):
    _create_candidate(client, admin_token, seed, password=CANDIDATE_PASSWORD)
    token = _login(client, "candidate.qa@sakura.cl", CANDIDATE_PASSWORD)["access_token"]
    r = client.get("/candidatos/me", headers=_headers(token))
    assert r.status_code == 200 and r.json()["candidato"]["cand_email"] == "candidate.qa@sakura.cl"


def test_candidato_no_puede_usar_recursos_internos(client, admin_token, seed):
    _create_candidate(client, admin_token, seed, password=CANDIDATE_PASSWORD)
    token = _login(client, "candidate.qa@sakura.cl", CANDIDATE_PASSWORD)["access_token"]
    assert client.get("/candidatos", headers=_headers(token)).status_code == 403


def test_candidato_cambia_password(client, admin_token, seed):
    _create_candidate(client, admin_token, seed, password=CANDIDATE_PASSWORD)
    token = _login(client, "candidate.qa@sakura.cl", CANDIDATE_PASSWORD)["access_token"]
    new = "CandidateNueva123!"
    r = client.post("/auth/change-password", headers=_headers(token), json={"password_actual": CANDIDATE_PASSWORD, "password_nueva": new})
    assert r.status_code == 204
    assert client.post("/auth/login", json={"email": "candidate.qa@sakura.cl", "password": CANDIDATE_PASSWORD}).status_code == 401
    assert client.post("/auth/login", json={"email": "candidate.qa@sakura.cl", "password": new}).status_code == 200


def test_candidato_change_password_actual_incorrecta(client, admin_token, seed):
    _create_candidate(client, admin_token, seed, password=CANDIDATE_PASSWORD)
    token = _login(client, "candidate.qa@sakura.cl", CANDIDATE_PASSWORD)["access_token"]
    r = client.post("/auth/change-password", headers=_headers(token), json={"password_actual": "Incorrecta123!", "password_nueva": "NuevaCandidate123!"})
    assert r.status_code == 400


# ---------------- nested resources ----------------
def test_crud_habilidad(client, admin_token, seed):
    cid = _create_candidate(client, admin_token, seed)["candidato"]["cand_id"]
    r = client.post(f"/candidatos/{cid}/habilidades", headers=_headers(admin_token), json={"cdhb_habilidad_id": seed["fastapi_id"], "cdhb_nivel_habilidad_id": seed["junior_id"], "cdhb_anios_experiencia": 1})
    assert r.status_code == 201; hid = r.json()["cdhb_id"]
    assert client.post(f"/candidatos/{cid}/habilidades", headers=_headers(admin_token), json={"cdhb_habilidad_id": seed["fastapi_id"]}).status_code == 409
    r = client.patch(f"/candidatos/{cid}/habilidades/{hid}", headers=_headers(admin_token), json={"cdhb_anios_experiencia": 3})
    assert r.status_code == 200 and r.json()["cdhb_anios_experiencia"] == 3
    assert client.delete(f"/candidatos/{cid}/habilidades/{hid}", headers=_headers(admin_token)).status_code == 204


def test_crud_estudio(client, admin_token, seed):
    cid = _create_candidate(client, admin_token, seed)["candidato"]["cand_id"]
    p = {"etcd_nivel_educacional_id": seed["nivel_edu_id"], "etcd_institucion_id": seed["institucion_id"], "etcd_carrera_id": seed["carrera_id"], "etcd_fecha_inicio": "2020-01-01", "etcd_fecha_fin": "2024-01-01"}
    r = client.post(f"/candidatos/{cid}/estudios", headers=_headers(admin_token), json=p); assert r.status_code == 201; sid=r.json()["etcd_id"]
    assert client.patch(f"/candidatos/{cid}/estudios/{sid}", headers=_headers(admin_token), json={"etcd_fecha_fin": "2025-01-01"}).status_code == 200
    assert client.delete(f"/candidatos/{cid}/estudios/{sid}", headers=_headers(admin_token)).status_code == 204


def test_crud_curso(client, admin_token, seed):
    cid = _create_candidate(client, admin_token, seed)["candidato"]["cand_id"]
    r=client.post(f"/candidatos/{cid}/cursos",headers=_headers(admin_token),json={"curs_nombre_curso":"Curso M3","curs_institucion_id":seed["institucion_id"],"curs_es_certificado":True,"curs_anio_curso":2026}); assert r.status_code==201; iid=r.json()["curs_id"]
    assert client.patch(f"/candidatos/{cid}/cursos/{iid}",headers=_headers(admin_token),json={"curs_nombre_curso":"Curso M3 PATCH"}).status_code==200
    assert client.delete(f"/candidatos/{cid}/cursos/{iid}",headers=_headers(admin_token)).status_code==204


def test_crud_experiencia_con_habilidades(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    r=client.post(f"/candidatos/{cid}/experiencias",headers=_headers(admin_token),json={"expl_empresa_id":seed["empresa_id"],"expl_cargo_id":seed["cargo_id"],"expl_descripcion_funciones":"QA","habilidades_ids":[seed["python_id"],seed["fastapi_id"]]}); assert r.status_code==201; iid=r.json()["expl_id"]
    assert set(r.json()["habilidades_ids"])=={seed["python_id"],seed["fastapi_id"]}
    r=client.patch(f"/candidatos/{cid}/experiencias/{iid}",headers=_headers(admin_token),json={"habilidades_ids":[seed["python_id"]]}); assert r.status_code==200 and r.json()["habilidades_ids"]==[seed["python_id"]]
    assert client.delete(f"/candidatos/{cid}/experiencias/{iid}",headers=_headers(admin_token)).status_code==204


def test_descargar_cv_original_usa_la_ultima_ruta_registrada(client, admin_token, seed, monkeypatch, tmp_path):
    storage = tmp_path / "cv"
    storage.mkdir()
    anterior = storage / "anterior.pdf"
    ultimo = storage / "ultimo.pdf"
    anterior.write_bytes(b"PDF anterior")
    ultimo.write_bytes(b"PDF ultimo")
    monkeypatch.setenv("CANDIDATE_CV_STORAGE_DIR", str(storage))

    payload = _candidate_payload(seed, email="descarga-original@sakura.cl")
    payload["cand_cv_urls"] = [str(anterior), str(ultimo)]
    creado = client.post("/candidatos", headers=_headers(admin_token), json=payload)
    assert creado.status_code == 201, creado.text

    response = client.get(
        f"/candidatos/{creado.json()['candidato']['cand_id']}/cv-original",
        headers=_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.content == b"PDF ultimo"
    assert "ultimo.pdf" in response.headers["content-disposition"]
    assert response.headers["content-type"] == "application/pdf"


def test_descargar_cv_original_rechaza_sin_cv_y_archivo_inexistente(client, admin_token, seed, monkeypatch, tmp_path):
    storage = tmp_path / "cv"
    storage.mkdir()
    monkeypatch.setenv("CANDIDATE_CV_STORAGE_DIR", str(storage))

    sin_cv = _candidate_payload(seed, email="sin-cv-original@sakura.cl")
    sin_cv["cand_cv_urls"] = None
    creado = client.post("/candidatos", headers=_headers(admin_token), json=sin_cv)
    assert creado.status_code == 201, creado.text
    cid = creado.json()["candidato"]["cand_id"]

    assert client.get(f"/candidatos/{cid}/cv-original", headers=_headers(admin_token)).status_code == 404

    sin_archivo = _candidate_payload(seed, email="cv-original-ausente@sakura.cl")
    sin_archivo["cand_cv_urls"] = [str(storage / "ausente.pdf")]
    creado = client.post("/candidatos", headers=_headers(admin_token), json=sin_archivo)
    assert creado.status_code == 201, creado.text
    assert client.get(
        f"/candidatos/{creado.json()['candidato']['cand_id']}/cv-original",
        headers=_headers(admin_token),
    ).status_code == 404


def test_descargar_cv_original_rechaza_ruta_externa_y_permisos(client, admin_token, view_token, no_perm_token, seed, monkeypatch, tmp_path):
    storage = tmp_path / "cv"
    storage.mkdir()
    externo = tmp_path / "externo.pdf"
    externo.write_bytes(b"fuera")
    monkeypatch.setenv("CANDIDATE_CV_STORAGE_DIR", str(storage))

    payload = _candidate_payload(seed, email="cv-original-externo@sakura.cl")
    payload["cand_cv_urls"] = [str(externo)]
    creado = client.post("/candidatos", headers=_headers(admin_token), json=payload)
    assert creado.status_code == 201, creado.text
    cid = creado.json()["candidato"]["cand_id"]

    assert client.get(f"/candidatos/{cid}/cv-original").status_code == 401
    assert client.get(f"/candidatos/{cid}/cv-original", headers=_headers(no_perm_token)).status_code == 403
    assert client.get(f"/candidatos/{cid}/cv-original", headers=_headers(view_token)).status_code == 404
    assert client.get("/candidatos/999999/cv-original", headers=_headers(view_token)).status_code == 404


def test_descargar_cv_original_rechaza_symlink_fuera_del_storage(client, admin_token, seed, monkeypatch, tmp_path):
    storage = tmp_path / "cv"
    storage.mkdir()
    externo = tmp_path / "externo.pdf"
    externo.write_bytes(b"fuera")
    enlace = storage / "enlace.pdf"
    try:
        enlace.symlink_to(externo)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"el entorno no permite crear symlink: {exc}")
    monkeypatch.setenv("CANDIDATE_CV_STORAGE_DIR", str(storage))

    payload = _candidate_payload(seed, email="cv-original-symlink@sakura.cl")
    payload["cand_cv_urls"] = [str(enlace)]
    creado = client.post("/candidatos", headers=_headers(admin_token), json=payload)
    assert creado.status_code == 201, creado.text
    assert client.get(
        f"/candidatos/{creado.json()['candidato']['cand_id']}/cv-original",
        headers=_headers(admin_token),
    ).status_code == 404


def test_fechas_estudio_invalidas_422(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    r=client.post(f"/candidatos/{cid}/estudios",headers=_headers(admin_token),json={"etcd_fecha_inicio":"2025-01-01","etcd_fecha_fin":"2024-01-01"})
    assert r.status_code==422


def test_experiencia_habilidades_duplicadas_422(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    r=client.post(f"/candidatos/{cid}/experiencias",headers=_headers(admin_token),json={"habilidades_ids":[seed["python_id"],seed["python_id"]]})
    assert r.status_code==422


# ---------------- importación CV ----------------
def _cv_text(email: str) -> str:
    return f"""Carla Perez Soto\n{email}\n+56 9 1234 5678\nIngeniera QA Backend\nPython Senior 5 anos\nUniversidad QA Ingenieria QA Profesional\nEmpresa QA Backend QA\nCurso Python Universidad QA certificado 2026\nhttps://linkedin.com/in/carla\nhttps://github.com/carla\nProfesional con amplia experiencia en desarrollo backend, automatizacion de pruebas y plataformas de reclutamiento empresarial.\n"""


def test_importar_txt_crea_perfil_y_password(client, admin_token):
    r=client.post("/candidatos/importar-cv",headers=_headers(admin_token),files={"file":("cv.txt",_cv_text("cvnuevo@sakura.cl").encode(),"text/plain")})
    assert r.status_code==200,r.text; b=r.json(); assert b["creado"] is True and b["actualizado"] is False and b["password_temporal"]
    assert b["candidato"]["cand_cv_urls"] and b["cv_ruta_guardada"] in b["candidato"]["cand_cv_urls"]


def test_importar_mismo_email_reutiliza_y_no_cambia_password(client, admin_token):
    r1=client.post("/candidatos/importar-cv",headers=_headers(admin_token),files={"file":("cv1.txt",_cv_text("reuso@sakura.cl").encode(),"text/plain")}); assert r1.status_code==200
    pwd=r1.json()["password_temporal"]
    r2=client.post("/candidatos/importar-cv",headers=_headers(admin_token),files={"file":("cv2.txt",_cv_text("reuso@sakura.cl").encode(),"text/plain")}); assert r2.status_code==200
    b=r2.json(); assert b["creado"] is False and b["actualizado"] is True and b["password_temporal"] is None
    assert len((b["candidato"]["cand_cv_urls"] or "").split(";"))==2
    assert client.post("/auth/login",json={"email":"reuso@sakura.cl","password":pwd}).status_code==200


def _cv_experiencia_empresa_cargo(email: str, experiencia: str) -> str:
    return f"""Carla Perez Soto
{email}
+56 9 1234 5678
Ingeniera QA
Experiencia laboral
{experiencia}
"""


def _cv_habilidades_desconocidas(email: str, habilidades: str) -> str:
    return f"""Carla Perez Soto
{email}
+56 9 1234 5678
Ingeniera QA
Habilidades
{habilidades}
"""


def _cv_idiomas(email: str, idiomas: str) -> str:
    return f"""Carla Perez Soto
{email}
+56 9 1234 5678
Ingeniera QA
Idiomas
{idiomas}
"""


def test_importar_idioma_existente_y_nuevo_con_nivel_y_muestra_perfil(client, admin_token):
    response = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("idiomas.txt", _cv_idiomas("idiomas.nuevos@sakura.cl", "English - Intermedio | Klingon - Avanzado").encode(), "text/plain")},
    )
    assert response.status_code == 200, response.text
    candidate_id = response.json()["candidato"]["cand_id"]
    profile = client.get(f"/candidatos/{candidate_id}/perfil-completo", headers=_headers(admin_token))
    assert profile.status_code == 200, profile.text
    assert {(item["idioma"]["idio_nombre"], item["nivel_idioma"]["nvid_codigo"]) for item in profile.json()["idiomas"]} == {
        ("Inglés", "INT"), ("Klingon", "AVA")
    }
    db = TestingSessionLocal()
    try:
        language = db.query(catalog_models.Idioma).filter_by(idio_nombre="Klingon").one()
        assert language.idio_creado_automaticamente is True
        assert language.idio_origen == "CV"
        assert language.idio_origen_candidato_id == candidate_id
    finally:
        db.close()


def test_reimportar_idioma_reutiliza_normalizado_y_no_duplica(client, admin_token):
    for filename, line in (("idioma-1.txt", "Klingon - Avanzado"), ("idioma-2.txt", "KLINGON - AVANZADO")):
        response = client.post(
            "/candidatos/importar-cv",
            headers=_headers(admin_token),
            files={"file": (filename, _cv_idiomas("idioma.reuso@sakura.cl", line).encode(), "text/plain")},
        )
        assert response.status_code == 200, response.text
    db = TestingSessionLocal()
    try:
        assert db.query(catalog_models.Idioma).filter(catalog_models.Idioma.idio_nombre.ilike("klingon")).count() == 1
        candidate = db.query(candidate_models.Candidato).filter_by(cand_email="idioma.reuso@sakura.cl").one()
        assert db.query(candidate_models.CandidatoIdioma).filter_by(cdio_candidato_id=candidate.cand_id).count() == 1
    finally:
        db.close()


def test_idioma_sin_nivel_no_crea_catalogo_ni_asociacion(client, admin_token):
    response = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("idioma-sin-nivel.txt", _cv_idiomas("idioma.sin.nivel@sakura.cl", "Klingon").encode(), "text/plain")},
    )
    assert response.status_code == 200, response.text
    assert any("no se pudo resolver un nivel válido" in warning.lower() for warning in response.json()["advertencias"])
    db = TestingSessionLocal()
    try:
        assert db.query(catalog_models.Idioma).filter_by(idio_nombre="Klingon").count() == 0
        candidate = db.query(candidate_models.Candidato).filter_by(cand_email="idioma.sin.nivel@sakura.cl").one()
        assert candidate.idiomas == []
    finally:
        db.close()


def test_idioma_nivel_ambiguo_no_crea_asociacion(client, admin_token):
    response = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("idioma-ambiguo.txt", _cv_idiomas("idioma.ambiguo@sakura.cl", "Klingon - Intermedio Avanzado").encode(), "text/plain")},
    )
    assert response.status_code == 200, response.text
    db = TestingSessionLocal()
    try:
        assert db.query(catalog_models.Idioma).filter_by(idio_nombre="Klingon").count() == 0
        candidate = db.query(candidate_models.Candidato).filter_by(cand_email="idioma.ambiguo@sakura.cl").one()
        assert candidate.idiomas == []
    finally:
        db.close()


def _cv_estudio_catalogo(email: str, estudio: str) -> str:
    return f"""Carla Perez Soto
{email}
+56 9 1234 5678
Ingeniera QA
Educación
{estudio}
"""


def test_importar_cv_crea_catalogos_de_estudios_y_los_asocia(client, admin_token, seed):
    casos = [
        (
            "estudio.carrera.nueva@sakura.cl",
            "Carrera: Arquitectura de Datos | Institución: Universidad QA",
            "Universidad QA",
            "Arquitectura de Datos",
        ),
        (
            "estudio.institucion.nueva@sakura.cl",
            "Carrera: Ingenieria QA | Institución: Instituto Nuevo Horizonte",
            "Instituto Nuevo Horizonte",
            "Ingenieria QA",
        ),
        (
            "estudio.ambos.nuevos@sakura.cl",
            "Carrera: Bioinformatica Aplicada | Institución: Universidad Nueva Ciencia",
            "Universidad Nueva Ciencia",
            "Bioinformatica Aplicada",
        ),
    ]
    for email, line, institution_name, career_name in casos:
        response = client.post(
            "/candidatos/importar-cv",
            headers=_headers(admin_token),
            files={"file": (f"{email}.txt", _cv_estudio_catalogo(email, line).encode(), "text/plain")},
        )
        assert response.status_code == 200, response.text
        candidate_id = response.json()["candidato"]["cand_id"]
        profile = client.get(f"/candidatos/{candidate_id}/perfil-completo", headers=_headers(admin_token))
        assert profile.status_code == 200, profile.text
        assert profile.json()["estudios"]
        db = TestingSessionLocal()
        try:
            institution = db.query(catalog_models.Institucion).filter_by(inst_nombre=institution_name).one()
            career = db.query(catalog_models.Carrera).filter_by(crra_nombre=career_name).one()
            study = db.query(candidate_models.EstudioCandidato).filter_by(etcd_candidato_id=candidate_id).one()
            assert (study.etcd_institucion_id, study.etcd_carrera_id) == (institution.inst_id, career.crra_id)
            assert institution.inst_origen == "CV" if institution_name != "Universidad QA" else institution.inst_origen is None
            if institution_name != "Universidad QA":
                assert institution.inst_creado_automaticamente is True
                assert institution.inst_origen_candidato_id == candidate_id
            if career_name != "Ingenieria QA":
                assert career.crra_creado_automaticamente is True
                assert career.crra_origen == "CV"
                assert career.crra_origen_candidato_id == candidate_id
            assert study.etcd_nivel_educacional_id is None
        finally:
            db.close()


def test_reimportar_estudio_reutiliza_catalogos_normalizados_y_no_duplica(client, admin_token):
    for filename, line in (
        ("estudio-1.txt", "Carrera: Ciencia de Datos | Institución: Universidad Horizonte"),
        ("estudio-2.txt", "CARRERA: CIENCIA DE DATOS | INSTITUCIÓN: UNIVERSIDAD HORIZONTE"),
    ):
        response = client.post(
            "/candidatos/importar-cv",
            headers=_headers(admin_token),
            files={"file": (filename, _cv_estudio_catalogo("estudio.reuso@sakura.cl", line).encode(), "text/plain")},
        )
        assert response.status_code == 200, response.text

    db = TestingSessionLocal()
    try:
        institution = db.query(catalog_models.Institucion).filter_by(inst_nombre="Universidad Horizonte").one()
        career = db.query(catalog_models.Carrera).filter_by(crra_nombre="Ciencia de Datos").one()
        candidate = db.query(candidate_models.Candidato).filter_by(cand_email="estudio.reuso@sakura.cl").one()
        assert db.query(catalog_models.Institucion).filter_by(inst_nombre="Universidad Horizonte").count() == 1
        assert db.query(catalog_models.Carrera).filter_by(crra_nombre="Ciencia de Datos").count() == 1
        assert db.query(candidate_models.EstudioCandidato).filter_by(etcd_candidato_id=candidate.cand_id).count() == 1
        study = candidate.estudios[0]
        assert (study.etcd_institucion_id, study.etcd_carrera_id) == (institution.inst_id, career.crra_id)
    finally:
        db.close()


def test_importar_estudio_parcial_valido_y_rechaza_contexto_ambiguo(client, admin_token):
    partial = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("estudio-parcial.txt", _cv_estudio_catalogo("estudio.parcial@sakura.cl", "Institución: Instituto Parcial").encode(), "text/plain")},
    )
    assert partial.status_code == 200, partial.text
    ambiguous = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("estudio-ambiguo.txt", _cv_estudio_catalogo("estudio.ambiguo@sakura.cl", "Carrera: estudios y formación | Institución: Universidad").encode(), "text/plain")},
    )
    assert ambiguous.status_code == 200, ambiguous.text

    db = TestingSessionLocal()
    try:
        partial_candidate = db.query(candidate_models.Candidato).filter_by(cand_email="estudio.parcial@sakura.cl").one()
        partial_study = partial_candidate.estudios[0]
        assert partial_study.etcd_institucion_id is not None
        assert partial_study.etcd_carrera_id is None
        assert db.query(catalog_models.Institucion).filter_by(inst_nombre="Universidad").count() == 0
        assert db.query(catalog_models.Carrera).filter_by(crra_nombre="estudios y formación").count() == 0
    finally:
        db.close()


def test_importar_cv_crea_habilidades_desconocidas_y_las_asocia(client, admin_token):
    texto = _cv_habilidades_desconocidas(
        "habilidades.nuevas@sakura.cl",
        "Kotlin, Terraform | React Native",
    )
    response = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("cv-habilidades.txt", texto.encode(), "text/plain")},
    )
    assert response.status_code == 200, response.text
    candidate_id = response.json()["candidato"]["cand_id"]
    profile = client.get(f"/candidatos/{candidate_id}/perfil-completo", headers=_headers(admin_token))
    assert profile.status_code == 200, profile.text
    assert {item["cdhb_habilidad_id"] for item in profile.json()["habilidades"]}

    db = TestingSessionLocal()
    try:
        habilidades = db.query(catalog_models.Habilidad).filter(
            catalog_models.Habilidad.hab_nombre.in_(["Kotlin", "Terraform", "React Native"])
        ).all()
        assert {item.hab_nombre for item in habilidades} == {"Kotlin", "Terraform", "React Native"}
        assert all(item.hab_creado_automaticamente is True for item in habilidades)
        assert all(item.hab_origen == "CV" for item in habilidades)
        assert all(item.hab_origen_candidato_id == candidate_id for item in habilidades)
        associations = db.query(candidate_models.CandidatoHabilidad).filter_by(cdhb_candidato_id=candidate_id).all()
        assert {item.hab_id for item in habilidades}.issubset({item.cdhb_habilidad_id for item in associations})
        assert all(item.cdhb_anios_experiencia is None for item in associations)
    finally:
        db.close()


def test_reimportar_cv_reutiliza_habilidades_normalizadas_y_no_duplica(client, admin_token):
    for filename, text in (
        ("habilidades-1.txt", _cv_habilidades_desconocidas("habilidades.reuso@sakura.cl", "Kotlin, Terraform")),
        ("habilidades-2.txt", _cv_habilidades_desconocidas("habilidades.reuso@sakura.cl", "KOTLIN, terraform")),
    ):
        response = client.post(
            "/candidatos/importar-cv",
            headers=_headers(admin_token),
            files={"file": (filename, text.encode(), "text/plain")},
        )
        assert response.status_code == 200, response.text

    db = TestingSessionLocal()
    try:
        assert db.query(catalog_models.Habilidad).filter_by(hab_nombre="Kotlin").count() == 1
        assert db.query(catalog_models.Habilidad).filter_by(hab_nombre="Terraform").count() == 1
        candidate = db.query(candidate_models.Candidato).filter_by(cand_email="habilidades.reuso@sakura.cl").one()
        assert db.query(candidate_models.CandidatoHabilidad).filter_by(cdhb_candidato_id=candidate.cand_id).count() == 2
    finally:
        db.close()


def test_importar_cv_no_crea_habilidad_desde_frase_ambigua(client, admin_token):
    texto = _cv_habilidades_desconocidas(
        "habilidades.ambiguas@sakura.cl",
        "experiencia en desarrollo de sistemas, otros",
    )
    response = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("cv-ambiguo.txt", texto.encode(), "text/plain")},
    )
    assert response.status_code == 200, response.text

    db = TestingSessionLocal()
    try:
        assert db.query(catalog_models.Habilidad).filter_by(hab_nombre="experiencia en desarrollo de sistemas").count() == 0
        assert db.query(candidate_models.Candidato).filter_by(cand_email="habilidades.ambiguas@sakura.cl").one().habilidades == []
    finally:
        db.close()


def test_importar_cv_crea_empresa_y_cargo_nuevos_y_los_asocia(client, admin_token):
    texto = _cv_experiencia_empresa_cargo(
        "catalogos.nuevos@sakura.cl",
        "Nova Sistemas SpA - Arquitecto de Integraciones",
    )
    r = client.post(
        "/candidatos/importar-cv",
        headers=_headers(admin_token),
        files={"file": ("cv-nuevos.txt", texto.encode(), "text/plain")},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    candidate_id = body["candidato"]["cand_id"]
    assert len(body["candidato"]["experiencias"]) == 1

    db = TestingSessionLocal()
    try:
        empresa = db.query(cliente_models.Empresa).filter_by(emp_nombre="Nova Sistemas SpA").one()
        cargo = db.query(catalog_models.Cargo).filter_by(crgo_nombre="Arquitecto de Integraciones").one()
        experiencia = db.query(candidate_models.ExperienciaLaboral).filter_by(expl_candidato_id=candidate_id).one()
        assert experiencia.expl_empresa_id == empresa.emp_id
        assert experiencia.expl_cargo_id == cargo.crgo_id
        assert empresa.emp_creado_automaticamente is True
        assert cargo.crgo_creado_automaticamente is True
        assert empresa.emp_origen == cargo.crgo_origen == "CV"
        assert empresa.emp_origen_candidato_id == cargo.crgo_origen_candidato_id == candidate_id
    finally:
        db.close()


def test_reimportar_cv_reutiliza_catalogos_y_no_duplica_experiencia(client, admin_token):
    texto = _cv_experiencia_empresa_cargo(
        "catalogos.reuso@sakura.cl",
        "Nova Reuso SpA - Arquitecto de Datos",
    )
    for nombre in ("primera.txt", "segunda.txt"):
        contenido = texto
        if nombre == "segunda.txt":
            contenido = contenido.replace("Nova Reuso SpA", "NOVA REUSO SPA").replace(
                "Arquitecto de Datos", "ARQUITECTO DE DATOS"
            )
        r = client.post(
            "/candidatos/importar-cv",
            headers=_headers(admin_token),
            files={"file": (nombre, contenido.encode(), "text/plain")},
        )
        assert r.status_code == 200, r.text

    db = TestingSessionLocal()
    try:
        assert db.query(cliente_models.Empresa).filter_by(emp_nombre="Nova Reuso SpA").count() == 1
        assert db.query(catalog_models.Cargo).filter_by(crgo_nombre="Arquitecto de Datos").count() == 1
        candidate = db.query(candidate_models.Candidato).filter_by(cand_email="catalogos.reuso@sakura.cl").one()
        assert db.query(candidate_models.ExperienciaLaboral).filter_by(expl_candidato_id=candidate.cand_id).count() == 1
    finally:
        db.close()


def test_importar_cv_conserva_experiencia_con_un_catalogo_nuevo(client, admin_token):
    casos = [
        ("empresa_existente@sakura.cl", "Empresa QA - Jefa de Operaciones", "Empresa QA", "Jefa de Operaciones"),
        ("cargo_existente@sakura.cl", "Nova Cliente SpA - Backend QA", "Nova Cliente SpA", "Backend QA"),
    ]
    for email, linea, empresa_nombre, cargo_nombre in casos:
        r = client.post(
            "/candidatos/importar-cv",
            headers=_headers(admin_token),
            files={"file": (f"{email}.txt", _cv_experiencia_empresa_cargo(email, linea).encode(), "text/plain")},
        )
        assert r.status_code == 200, r.text
        candidate_id = r.json()["candidato"]["cand_id"]
        db = TestingSessionLocal()
        try:
            empresa = db.query(cliente_models.Empresa).filter_by(emp_nombre=empresa_nombre).one()
            cargo = db.query(catalog_models.Cargo).filter_by(crgo_nombre=cargo_nombre).one()
            experiencia = db.query(candidate_models.ExperienciaLaboral).filter_by(expl_candidato_id=candidate_id).one()
            assert (experiencia.expl_empresa_id, experiencia.expl_cargo_id) == (empresa.emp_id, cargo.crgo_id)
        finally:
            db.close()


def test_importar_cv_sin_email_422(client, admin_token):
    r=client.post("/candidatos/importar-cv",headers=_headers(admin_token),files={"file":("cv.txt",b"Carla Perez\nSin correo", "text/plain")})
    assert r.status_code==422


def test_importar_formato_no_soportado_422(client, admin_token):
    r=client.post("/candidatos/importar-cv",headers=_headers(admin_token),files={"file":("cv.csv",b"a,b", "text/csv")})
    assert r.status_code==422


def test_importar_varios_cvs(client, admin_token):
    files=[("files",("a.txt",_cv_text("multi1@sakura.cl").encode(),"text/plain")),("files",("b.txt",_cv_text("multi2@sakura.cl").encode(),"text/plain"))]
    r=client.post("/candidatos/importar-cvs",headers=_headers(admin_token),files=files)
    assert r.status_code==200 and len(r.json())==2 and all(x["creado"] for x in r.json())


def test_importar_varios_cvs_revierte_catalogos_si_un_archivo_falla(client, admin_token):
    files = [
        (
            "files",
            (
                "valido.txt",
                _cv_experiencia_empresa_cargo(
                    "lote.rollback@sakura.cl",
                    "Empresa Lote Rollback - Cargo Lote Rollback",
                ).replace(
                    "Empresa Lote Rollback - Cargo Lote Rollback",
                    "Empresa Lote Rollback - Cargo Lote Rollback\nTecnologias: Skill Lote Rollback\nEducación\nCarrera: Carrera Lote Rollback | Institución: Universidad Lote Rollback\nIdiomas\nKlingon - Avanzado",
                ).encode(),
                "text/plain",
            ),
        ),
        ("files", ("invalido.csv", b"no es un CV", "text/csv")),
    ]
    response = client.post("/candidatos/importar-cvs", headers=_headers(admin_token), files=files)
    assert response.status_code == 422

    db = TestingSessionLocal()
    try:
        assert db.query(candidate_models.Candidato).filter_by(cand_email="lote.rollback@sakura.cl").count() == 0
        assert db.query(cliente_models.Empresa).filter_by(emp_nombre="Empresa Lote Rollback").count() == 0
        assert db.query(catalog_models.Cargo).filter_by(crgo_nombre="Cargo Lote Rollback").count() == 0
        assert db.query(catalog_models.Habilidad).filter_by(hab_nombre="Skill Lote Rollback").count() == 0
        assert db.query(catalog_models.Institucion).filter_by(inst_nombre="Universidad Lote Rollback").count() == 0
        assert db.query(catalog_models.Carrera).filter_by(crra_nombre="Carrera Lote Rollback").count() == 0
        assert db.query(catalog_models.Idioma).filter_by(idio_nombre="Klingon").count() == 0
    finally:
        db.close()


# ---------------- postulaciones / exclusiones ----------------
def test_asociar_candidato_que_no_cumple_se_permite_con_advertencia(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    b=_associate(client,admin_token,seed,cid,slcd_pretension_renta=1500000)
    assert b["evaluacion"]["cumple_excluyentes"] is False
    assert b["evaluacion"]["advertencia"]
    assert b["postulacion"]["slcd_estado_solicitud_candidato_id"]==seed["cand_states"]["En revision"]


def test_asociar_candidato_que_cumple_excluyentes(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed,include_nested=True)["candidato"]["cand_id"]
    b=_associate(client,admin_token,seed,cid)
    assert b["evaluacion"]["cumple_excluyentes"] is True and b["evaluacion"]["habilidades_faltantes"]==[]


def test_postulacion_duplicada_409(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    _associate(client,admin_token,seed,cid)
    assert client.post(f"/solicitudes/{seed['solicitud_id']}/candidatos/{cid}",headers=_headers(admin_token),json={}).status_code==409


def test_listar_postulaciones_por_solicitud_y_candidato(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    _associate(client,admin_token,seed,cid)
    a=client.get(f"/solicitudes/{seed['solicitud_id']}/candidatos",headers=_headers(admin_token)); assert a.status_code==200 and len(a.json())==1
    b=client.get(f"/candidatos/{cid}/solicitudes",headers=_headers(admin_token)); assert b.status_code==200 and len(b.json())==1


def test_patch_postulacion(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    app=_associate(client,admin_token,seed,cid)["postulacion"]
    r=client.patch(f"/postulaciones/{app['slcd_id']}",headers=_headers(admin_token),json={"slcd_puntaje_compatibilidad":88.5,"slcd_observaciones":"QA"})
    assert r.status_code==200 and float(r.json()["slcd_puntaje_compatibilidad"])==88.5


def test_flujo_completo_en_revision_a_contratado(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    app=_associate(client,admin_token,seed,cid)["postulacion"]; aid=app["slcd_id"]
    for name in ["En entrevista","Seleccionado","Contratado"]:
        r=client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"][name]})
        assert r.status_code==200,r.text
        assert r.json()["slcd_estado_solicitud_candidato_id"]==seed["cand_states"][name]


def test_transicion_directa_revision_a_seleccionado_409(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    aid=_associate(client,admin_token,seed,cid)["postulacion"]["slcd_id"]
    r=client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"]["Seleccionado"]})
    assert r.status_code==409


@pytest.mark.parametrize("state_name",["Inhabilitado","Descartado"])
def test_rechazo_requiere_motivo(client, admin_token, seed, state_name):
    cid=_create_candidate(client,admin_token,seed,email=f"{state_name.lower()}@sakura.cl")["candidato"]["cand_id"]
    aid=_associate(client,admin_token,seed,cid)["postulacion"]["slcd_id"]
    r=client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"][state_name]})
    assert r.status_code==422


def test_inhabilitado_con_motivo_ok(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    aid=_associate(client,admin_token,seed,cid)["postulacion"]["slcd_id"]
    r=client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"]["Inhabilitado"],"motivo_rechazo_id":seed["motivo_id"],"observaciones":"No cumple"})
    assert r.status_code==200 and r.json()["slcd_motivo_rechazo_id"]==seed["motivo_id"]


def test_motivo_rechazo_no_permitido_en_entrevista(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    aid=_associate(client,admin_token,seed,cid)["postulacion"]["slcd_id"]
    r=client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"]["En entrevista"],"motivo_rechazo_id":seed["motivo_id"]})
    assert r.status_code==422


def test_estado_terminal_contratado_no_reabre(client, admin_token, seed):
    cid=_create_candidate(client,admin_token,seed)["candidato"]["cand_id"]
    aid=_associate(client,admin_token,seed,cid)["postulacion"]["slcd_id"]
    for name in ["En entrevista","Seleccionado","Contratado"]:
        assert client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"][name]}).status_code==200
    assert client.patch(f"/postulaciones/{aid}/estado",headers=_headers(admin_token),json={"estado_id":seed["cand_states"]["En entrevista"]}).status_code==409


# ---------------- integración cierre M2 <-> M3 ----------------
def _contract_candidate(client, token, seed, email):
    cid=_create_candidate(client,token,seed,email=email)["candidato"]["cand_id"]
    aid=_associate(client,token,seed,cid)["postulacion"]["slcd_id"]
    for name in ["En entrevista","Seleccionado","Contratado"]:
        r=client.patch(f"/postulaciones/{aid}/estado",headers=_headers(token),json={"estado_id":seed["cand_states"][name]}); assert r.status_code==200,r.text
    return cid


def test_no_cerrar_solicitud_con_cero_contratados(client, admin_token, seed):
    r=client.patch(f"/solicitudes/{seed['solicitud_id']}/estado",headers=_headers(admin_token),json={"sol_estado_solicitud_id":seed["sol_states"]["Cerrado"]})
    assert r.status_code==409
    assert "ningún candidato contratado" in r.text


def test_cierre_parcial_permitido_con_warning(client, admin_token, seed):
    _contract_candidate(client,admin_token,seed,"parcial@sakura.cl")
    r=client.patch(f"/solicitudes/{seed['solicitud_id']}/estado",headers=_headers(admin_token),json={"sol_estado_solicitud_id":seed["sol_states"]["Cerrado"]})
    assert r.status_code==200,r.text
    warning=r.headers.get("X-Sakura-Warning","")
    assert "1 de 2" in warning


def test_cierre_total_sin_warning(client, admin_token, seed):
    _contract_candidate(client,admin_token,seed,"uno@sakura.cl")
    _contract_candidate(client,admin_token,seed,"dos@sakura.cl")
    r=client.patch(f"/solicitudes/{seed['solicitud_id']}/estado",headers=_headers(admin_token),json={"sol_estado_solicitud_id":seed["sol_states"]["Cerrado"]})
    assert r.status_code==200,r.text
    assert not r.headers.get("X-Sakura-Warning")


# =============================================================================
# AUTOSERVICIO CANDIDATO - M3 EXTENDIDO
# =============================================================================

def _candidate_token(client: TestClient, admin_token: str, seed: SeedInfo, *, email: str = "candidate.qa@sakura.cl"):
    created = _create_candidate(client, admin_token, seed, email=email, password=CANDIDATE_PASSWORD)
    token = _login(client, email, CANDIDATE_PASSWORD)["access_token"]
    return created, token


def test_me_perfil_completo_devuelve_todo_el_cv(client, admin_token, seed):
    body, token = _candidate_token(client, admin_token, seed)
    cid = body["candidato"]["cand_id"]
    client.post(f"/candidatos/{cid}/habilidades", headers=_headers(admin_token), json={"cdhb_habilidad_id": seed["python_id"], "cdhb_nivel_habilidad_id": seed["junior_id"], "cdhb_anios_experiencia": 2})
    client.post(f"/candidatos/{cid}/estudios", headers=_headers(admin_token), json={"etcd_institucion_id": seed["institucion_id"], "etcd_carrera_id": seed["carrera_id"]})
    client.post(f"/candidatos/{cid}/cursos", headers=_headers(admin_token), json={"curs_nombre_curso":"Curso Self", "curs_institucion_id":seed["institucion_id"], "curs_anio_curso":2026})
    r = client.get("/candidatos/me/perfil-completo", headers=_headers(token))
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["cand_id"] == cid
    assert len(b["habilidades"]) == 1
    assert len(b["estudios"]) == 1
    assert len(b["cursos"]) == 1
    assert "cand_password" not in b


def test_me_sin_token_retorna_401(client):
    assert client.get("/candidatos/me/perfil-completo").status_code == 401


def test_usuario_interno_no_puede_usar_me_candidato(client, admin_token):
    assert client.get("/candidatos/me/perfil-completo", headers=_headers(admin_token)).status_code == 403


def test_candidato_no_puede_consultar_perfil_por_id(client, admin_token, seed):
    body, token = _candidate_token(client, admin_token, seed)
    cid = body["candidato"]["cand_id"]
    assert client.get(f"/candidatos/{cid}", headers=_headers(token)).status_code == 403


def test_candidato_no_puede_consultar_otro_candidato(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed, email="candidate1.qa@sakura.cl")
    other = _create_candidate(client, admin_token, seed, email="candidate2.qa@sakura.cl")["candidato"]
    assert client.get(f"/candidatos/{other['cand_id']}/perfil-completo", headers=_headers(token)).status_code == 403


def test_patch_me_permita_solo_campos_autoservicio(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    r = client.patch("/candidatos/me", headers=_headers(token), json={
        "cand_telefono":"988887777",
        "cand_disponibilidad_id":seed["disponibilidad_id"],
        "cand_resumen_profesional":"Perfil actualizado por el candidato",
        "cand_url_1":["https://linkedin.com/in/self", "https://linkedin.com/in/self", "https://github.com/self"],
        "cand_titulo":"Especialista Backend",
    })
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["cand_telefono"] == "988887777"
    assert b["cand_titulo"] == "Especialista Backend"
    assert b["cand_url_1"] == "https://linkedin.com/in/self;https://github.com/self"


@pytest.mark.parametrize("field,value", [
    ("cand_email", "hack@sakura.cl"),
    ("cand_nombres", "Hack"),
    ("cand_rut_sin_dv", 99999999),
    ("cand_dv", 1),
    ("cand_estado_usuario_id", 999),
    ("cand_cv_urls", "ruta/falsa.pdf"),
    ("cand_fecha_creacion", "2026-01-01T00:00:00"),
])
def test_patch_me_rechaza_campos_protegidos(client, admin_token, seed, field, value):
    _, token = _candidate_token(client, admin_token, seed)
    r = client.patch("/candidatos/me", headers=_headers(token), json={field:value})
    assert r.status_code == 422


def test_patch_me_vacio_422(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    assert client.patch("/candidatos/me", headers=_headers(token), json={}).status_code == 422


def test_me_habilidades_get_crud(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    r = client.post("/candidatos/me/habilidades", headers=_headers(token), json={"cdhb_habilidad_id":seed["python_id"],"cdhb_nivel_habilidad_id":seed["junior_id"],"cdhb_anios_experiencia":1})
    assert r.status_code == 201, r.text; item = r.json()
    rows = client.get("/candidatos/me/habilidades", headers=_headers(token)); assert rows.status_code == 200 and len(rows.json()) == 1
    r = client.patch(f"/candidatos/me/habilidades/{item['cdhb_id']}", headers=_headers(token), json={"cdhb_anios_experiencia":4}); assert r.status_code == 200 and r.json()["cdhb_anios_experiencia"] == 4
    assert client.delete(f"/candidatos/me/habilidades/{item['cdhb_id']}", headers=_headers(token)).status_code == 204
    assert client.get("/candidatos/me/habilidades", headers=_headers(token)).json() == []


def test_me_habilidad_duplicada_409(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    payload={"cdhb_habilidad_id":seed["python_id"],"cdhb_anios_experiencia":1}
    assert client.post("/candidatos/me/habilidades",headers=_headers(token),json=payload).status_code==201
    assert client.post("/candidatos/me/habilidades",headers=_headers(token),json=payload).status_code==409


def test_me_no_puede_modificar_habilidad_de_otro(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed, email="owner.qa@sakura.cl")
    other = _create_candidate(client, admin_token, seed, email="other.qa@sakura.cl")["candidato"]
    skill=client.post(f"/candidatos/{other['cand_id']}/habilidades",headers=_headers(admin_token),json={"cdhb_habilidad_id":seed["python_id"],"cdhb_anios_experiencia":1}).json()
    assert client.patch(f"/candidatos/me/habilidades/{skill['cdhb_id']}",headers=_headers(token),json={"cdhb_anios_experiencia":9}).status_code==404


def test_me_estudios_get_crud(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    p={"etcd_nivel_educacional_id":seed["nivel_edu_id"],"etcd_institucion_id":seed["institucion_id"],"etcd_carrera_id":seed["carrera_id"],"etcd_fecha_inicio":"2020-01-01","etcd_fecha_fin":"2024-01-01"}
    r=client.post("/candidatos/me/estudios",headers=_headers(token),json=p); assert r.status_code==201,r.text; item=r.json()
    assert len(client.get("/candidatos/me/estudios",headers=_headers(token)).json())==1
    assert client.patch(f"/candidatos/me/estudios/{item['etcd_id']}",headers=_headers(token),json={"etcd_fecha_fin":"2025-01-01"}).status_code==200
    assert client.delete(f"/candidatos/me/estudios/{item['etcd_id']}",headers=_headers(token)).status_code==204


def test_me_estudio_fechas_invalidas_422(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    r=client.post("/candidatos/me/estudios",headers=_headers(token),json={"etcd_fecha_inicio":"2025-01-01","etcd_fecha_fin":"2024-01-01"})
    assert r.status_code==422


def test_me_experiencias_get_crud(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    p={"expl_empresa_id":seed["empresa_id"],"expl_cargo_id":seed["cargo_id"],"expl_descripcion_funciones":"Autoservicio","habilidades_ids":[seed["python_id"],seed["fastapi_id"]]}
    r=client.post("/candidatos/me/experiencias",headers=_headers(token),json=p); assert r.status_code==201,r.text; item=r.json()
    assert set(item["habilidades_ids"])=={seed["python_id"],seed["fastapi_id"]}
    rows=client.get("/candidatos/me/experiencias",headers=_headers(token)); assert rows.status_code==200 and len(rows.json())==1
    r=client.patch(f"/candidatos/me/experiencias/{item['expl_id']}",headers=_headers(token),json={"habilidades_ids":[seed["python_id"]]}); assert r.status_code==200 and r.json()["habilidades_ids"]==[seed["python_id"]]
    assert client.delete(f"/candidatos/me/experiencias/{item['expl_id']}",headers=_headers(token)).status_code==204


def test_me_cursos_get_crud(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    r=client.post("/candidatos/me/cursos",headers=_headers(token),json={"curs_nombre_curso":"Curso Portal","curs_institucion_id":seed["institucion_id"],"curs_es_certificado":True,"curs_anio_curso":2026}); assert r.status_code==201,r.text; item=r.json()
    assert len(client.get("/candidatos/me/cursos",headers=_headers(token)).json())==1
    r=client.patch(f"/candidatos/me/cursos/{item['curs_id']}",headers=_headers(token),json={"curs_nombre_curso":"Curso Portal PATCH"}); assert r.status_code==200
    assert client.delete(f"/candidatos/me/cursos/{item['curs_id']}",headers=_headers(token)).status_code==204


def test_me_direccion_crear_actualizar_listar_eliminar(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    r=client.put("/candidatos/me/direccion",headers=_headers(token),json={"drcd_comuna_id":seed["comuna_id"],"drcd_calle":"Calle QA","drcd_numero":123,"drcd_dpto_oficina":"4B"}); assert r.status_code==200,r.text; did=r.json()["drcd_id"]
    rows=client.get("/candidatos/me/direcciones",headers=_headers(token)); assert rows.status_code==200 and len(rows.json())==1 and rows.json()[0]["drcd_id"]==did
    r=client.put("/candidatos/me/direccion",headers=_headers(token),json={"drcd_numero":456}); assert r.status_code==200 and r.json()["drcd_numero"]==456 and r.json()["drcd_id"]==did
    assert client.delete("/candidatos/me/direccion",headers=_headers(token)).status_code==204
    assert client.get("/candidatos/me/direcciones",headers=_headers(token)).json()==[]


def test_me_direccion_comuna_inexistente_422(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    assert client.put("/candidatos/me/direccion",headers=_headers(token),json={"drcd_comuna_id":999999}).status_code==422


def test_me_direccion_delete_sin_direccion_404(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    assert client.delete("/candidatos/me/direccion",headers=_headers(token)).status_code==404


def test_me_solicitudes_solo_propias_y_readonly(client, admin_token, seed):
    body, token = _candidate_token(client, admin_token, seed)
    cid=body["candidato"]["cand_id"]
    app=_associate(client,admin_token,seed,cid)["postulacion"]
    rows=client.get("/candidatos/me/solicitudes",headers=_headers(token)); assert rows.status_code==200 and len(rows.json())==1 and rows.json()[0]["slcd_id"]==app["slcd_id"]
    rows=client.get("/candidatos/me/solicitudes",headers=_headers(token),params={"estado_id":seed["cand_states"]["En revision"]}); assert len(rows.json())==1
    rows=client.get("/candidatos/me/solicitudes",headers=_headers(token),params={"estado_id":seed["cand_states"]["Contratado"]}); assert rows.json()==[]
    # El candidato no puede alterar postulación/estado porque siguen siendo recursos internos CAN_UPDATE.
    assert client.patch(f"/postulaciones/{app['slcd_id']}",headers=_headers(token),json={"slcd_observaciones":"hack"}).status_code==403
    assert client.patch(f"/postulaciones/{app['slcd_id']}/estado",headers=_headers(token),json={"estado_id":seed["cand_states"]["Contratado"]}).status_code==403


def test_me_endpoints_no_exponen_password(client, admin_token, seed):
    _, token = _candidate_token(client, admin_token, seed)
    for path in ["/candidatos/me", "/candidatos/me/perfil-completo"]:
        r=client.get(path,headers=_headers(token)); assert r.status_code==200
        assert "cand_password" not in r.text


def test_candidato_inactivo_no_puede_usar_autoservicio(client, admin_token, seed):
    body, token = _candidate_token(client, admin_token, seed)
    cid=body["candidato"]["cand_id"]
    db=TestingSessionLocal()
    try:
        c=db.get(candidate_models.Candidato,cid); c.cand_estado_usuario_id=seed["inactivo_id"]; db.commit()
    finally: db.close()
    assert client.get("/candidatos/me/perfil-completo",headers=_headers(token)).status_code==403
