from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Iterator

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "qa-m5-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ACTIVE_USER_STATUS_NAME", "Activo")
os.environ.setdefault("ADMIN_ROLE_NAME", "Administrador")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import utils as auth_utils
from app.catalogos import models as catalog_models
from app.clientes import models as cliente_models  # registra FKs usadas por candidato/solicitud
from app.candidatos import models as candidato_models
from app.database import Base, get_db
from app.entrevistas import models as entrevista_models
from app.entrevistas import router as entrevistas_router
from app.solicitudes import models as solicitud_models
from app.usuarios import models as user_models


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(TEST_ENGINE, "connect")
def _fk_on(dbapi_connection, _record):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
app_test = FastAPI(title="QA M5 Entrevistas")
app_test.include_router(entrevistas_router)


def override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app_test.dependency_overrides[get_db] = override_get_db

PERMS = ["INT_CREATE", "INT_VIEW", "INT_UPDATE", "INT_EVALUATE"]


def utc_future(days: int = 10, hours: int = 0) -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=days, hours=hours)


def _token(user_id: int) -> str:
    return auth_utils.create_access_token({
        "sub": str(user_id),
        "email": "qa.m5@sakura.cl",
        "principal_type": "usuario",
    })


def _candidate_token(candidate_id: int) -> str:
    return auth_utils.create_access_token({
        "sub": str(candidate_id),
        "email": "candidate.m5@sakura.cl",
        "principal_type": "candidato",
    })


def H(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(user_id)}"}


def HC(candidate_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {_candidate_token(candidate_id)}"}


def _make_user(db: Session, role, state, area, seq: int, email: str):
    u = user_models.Usuario(
        usr_rol_id=role.rol_id,
        usr_estado_usuario_id=state.esusr_id,
        usr_area_id=area.area_id,
        usr_nombres=f"U{seq}",
        usr_apellido_paterno="Entrevista",
        usr_rut_sin_dv=f"30000{seq}",
        usr_dv=str(seq % 10),
        usr_email=email,
        usr_contrasena=auth_utils.hash_password("Password123!"),
    )
    db.add(u)
    db.flush()
    return u


def _seed():
    db = TestingSessionLocal()
    try:
        activo = user_models.EstadoUsuario(esusr_nombre="Activo", esusr_descripcion="Activo")
        inactivo = user_models.EstadoUsuario(esusr_nombre="Inactivo", esusr_descripcion="Inactivo")
        area = user_models.Area(area_nombre="QA M5", area_descripcion="QA")
        db.add_all([activo, inactivo, area]); db.flush()

        p = {name: user_models.Permiso(per_nombre=name, per_descripcion=name) for name in PERMS}
        db.add_all(p.values()); db.flush()

        def role(name: str, perms: list[str]):
            r = user_models.Rol(rol_nombre=name, rol_descripcion=name, permisos=[p[x] for x in perms])
            db.add(r); db.flush(); return r

        r_admin = role("Administrador", PERMS)
        r_creator = role("Creator", ["INT_CREATE"])
        r_view = role("Viewer", ["INT_VIEW"])
        r_update = role("Updater", ["INT_UPDATE"])
        r_eval = role("Evaluator", ["INT_EVALUATE"])
        r_interviewer = role("Interviewer", ["INT_VIEW", "INT_EVALUATE"])
        r_no = role("NoPerm", [])
        r_recruiter = role("Reclutador", ["INT_CREATE", "INT_VIEW", "INT_UPDATE", "INT_EVALUATE"])

        admin = _make_user(db, r_admin, activo, area, 1, "admin.m5@sakura.cl")
        creator = _make_user(db, r_creator, activo, area, 2, "creator.m5@sakura.cl")
        viewer = _make_user(db, r_view, activo, area, 3, "viewer.m5@sakura.cl")
        updater = _make_user(db, r_update, activo, area, 4, "updater.m5@sakura.cl")
        eval1 = _make_user(db, r_interviewer, activo, area, 5, "eval1.m5@sakura.cl")
        eval2 = _make_user(db, r_interviewer, activo, area, 6, "eval2.m5@sakura.cl")
        eval_only = _make_user(db, r_eval, activo, area, 7, "evalonly.m5@sakura.cl")
        noperm = _make_user(db, r_no, activo, area, 8, "noperm.m5@sakura.cl")
        inactive_eval = _make_user(db, r_interviewer, inactivo, area, 9, "inactive.m5@sakura.cl")
        recruiter = _make_user(db, r_recruiter, activo, area, 10, "recruiter.m5@sakura.cl")

        req_states = {}
        for n in ["Pendiente", "En Curso", "En Entrevistas", "Cancelado", "Cerrado", "Pausado"]:
            o = catalog_models.EstadoSolicitud(essl_nombre=n, essl_descripcion=n); db.add(o); db.flush(); req_states[n] = o.essl_id
        post_states = {}
        for n in ["En revision", "En entrevista", "Inhabilitado", "Seleccionado", "Descartado", "Contratado"]:
            o = catalog_models.EstadoSolicitudCandidato(essc_nombre=n, essc_descripcion=n); db.add(o); db.flush(); post_states[n] = o.essc_id
        int_states = {}
        for n in ["Pendiente", "Confirmada", "Realizada", "Reprogramada", "Cancelada", "No Asistio"]:
            o = catalog_models.EstadoEntrevista(esev_nombre=n, esev_descripcion=n); db.add(o); db.flush(); int_states[n] = o.esev_id
        types = {}
        for n in ["RRHH", "Tecnica", "Cliente", "Operaciones"]:
            o = catalog_models.TipoEntrevista(tpet_nombre=n, tpet_descripcion=n); db.add(o); db.flush(); types[n] = o.tpet_id
        results = {}
        for n in ["Aprobado", "Aprobado con Observaciones", "No Aprobado", "En Espera"]:
            o = catalog_models.NombreResultado(nore_nombre=n); db.add(o); db.flush(); results[n] = o.nore_id
        disp = catalog_models.Disponibilidad(disp_nombre="Inmediata"); db.add(disp); db.flush()

        c1 = candidato_models.Candidato(cand_email="cand1.m5@sakura.cl", cand_password=auth_utils.hash_password("Cand123!"), cand_nombres="Ana", cand_apellido_paterno="Uno", cand_disponibilidad_id=disp.disp_id, cand_estado_usuario_id=activo.esusr_id)
        c2 = candidato_models.Candidato(cand_email="cand2.m5@sakura.cl", cand_password=auth_utils.hash_password("Cand123!"), cand_nombres="Beto", cand_apellido_paterno="Dos", cand_disponibilidad_id=disp.disp_id, cand_estado_usuario_id=activo.esusr_id)
        c3 = candidato_models.Candidato(cand_email="cand3.m5@sakura.cl", cand_password=auth_utils.hash_password("Cand123!"), cand_nombres="Cata", cand_apellido_paterno="Tres", cand_disponibilidad_id=disp.disp_id, cand_estado_usuario_id=activo.esusr_id)
        db.add_all([c1,c2,c3]); db.flush()

        s1 = solicitud_models.Solicitud(sol_codigo="SOL-900001", sol_titulo="QA M5", sol_cantidad_vacantes=3, sol_estado_solicitud_id=req_states["En Entrevistas"], sol_usuario_creador_id=admin.usr_id, sol_usuario_asignado_id=recruiter.usr_id)
        s2 = solicitud_models.Solicitud(sol_codigo="SOL-900002", sol_titulo="QA M5 No Stage", sol_cantidad_vacantes=1, sol_estado_solicitud_id=req_states["En Curso"], sol_usuario_creador_id=admin.usr_id, sol_usuario_asignado_id=recruiter.usr_id)
        db.add_all([s1,s2]); db.flush()
        p1 = solicitud_models.SolicitudCandidato(slcd_candidato_id=c1.cand_id, slcd_solicitud_id=s1.sol_id, slcd_estado_solicitud_candidato_id=post_states["En entrevista"], slcd_fecha_postulacion=datetime.now())
        p2 = solicitud_models.SolicitudCandidato(slcd_candidato_id=c2.cand_id, slcd_solicitud_id=s1.sol_id, slcd_estado_solicitud_candidato_id=post_states["En entrevista"], slcd_fecha_postulacion=datetime.now())
        p3 = solicitud_models.SolicitudCandidato(slcd_candidato_id=c3.cand_id, slcd_solicitud_id=s1.sol_id, slcd_estado_solicitud_candidato_id=post_states["En revision"], slcd_fecha_postulacion=datetime.now())
        p4 = solicitud_models.SolicitudCandidato(slcd_candidato_id=c3.cand_id, slcd_solicitud_id=s2.sol_id, slcd_estado_solicitud_candidato_id=post_states["En entrevista"], slcd_fecha_postulacion=datetime.now())
        db.add_all([p1,p2,p3,p4]); db.commit()
        return {
            "admin":admin.usr_id,"creator":creator.usr_id,"viewer":viewer.usr_id,"updater":updater.usr_id,
            "eval1":eval1.usr_id,"eval2":eval2.usr_id,"eval_only":eval_only.usr_id,"noperm":noperm.usr_id,
            "inactive_eval":inactive_eval.usr_id,"recruiter":recruiter.usr_id,
            "c1":c1.cand_id,"c2":c2.cand_id,"c3":c3.cand_id,
            "p1":p1.slcd_id,"p2":p2.slcd_id,"p3":p3.slcd_id,"p4":p4.slcd_id,
            "s1":s1.sol_id,"s2":s2.sol_id,"req_states":req_states,"post_states":post_states,
            "int_states":int_states,"types":types,"results":results,
        }
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(TEST_ENGINE)
    Base.metadata.create_all(TEST_ENGINE)
    # Replica la UNIQUE física existente en PostgreSQL base_inicial.
    with TEST_ENGINE.begin() as conn:
        conn.execute(text("CREATE UNIQUE INDEX uq_m5_agenda_sqlite ON tbl_cita_entrevista(ctev_solicitud_candidato_id, ctev_tipo_entrevista_id, ctev_fecha_hora_inicio)"))
    app_test.state.seed = _seed()
    yield
    Base.metadata.drop_all(TEST_ENGINE)


@pytest.fixture
def seed(): return app_test.state.seed

@pytest.fixture
def client():
    with TestClient(app_test) as c: yield c


def payload(seed, *, post=None, start=None, end=None, tipos=None, title="Entrevista QA"):
    start = start or utc_future(10)
    end = end or (start + timedelta(hours=1))
    return {
        "solicitud_candidato_id": post or seed["p1"],
        "fecha_hora_inicio": start.isoformat(),
        "fecha_hora_fin": end.isoformat(),
        "titulo_evento": title,
        "enlace_reunion": "https://meet.example/qa",
        "comentarios_convocatoria": "Conectarse 5 minutos antes",
        "tipos": tipos or [
            {"tipo_entrevista_id": seed["types"]["Tecnica"], "usuarios_ids": [seed["eval1"], seed["eval2"]]},
            {"tipo_entrevista_id": seed["types"]["RRHH"], "usuarios_ids": [seed["recruiter"]]},
        ],
    }


def create_ok(client, seed, **kwargs):
    r = client.post("/entrevistas", json=payload(seed, **kwargs), headers=H(seed["creator"]))
    assert r.status_code == 201, r.text
    return r.json()


def realize(client, seed, iid):
    r = client.post(f"/entrevistas/{iid}/realizar", headers=H(seed["updater"]))
    assert r.status_code == 200, r.text
    return r.json()


# --- Seguridad/RBAC ---
def test_sin_token_401(client): assert client.get("/entrevistas").status_code == 401
def test_sin_int_view_403(client, seed): assert client.get("/entrevistas", headers=H(seed["noperm"])).status_code == 403
def test_crear_sin_int_create_403(client, seed): assert client.post("/entrevistas", json=payload(seed), headers=H(seed["viewer"])).status_code == 403
def test_actualizar_sin_int_update_403(client, seed):
    i=create_ok(client,seed); assert client.patch(f"/entrevistas/{i['entrevista_id']}",json={"titulo_evento":"X"},headers=H(seed["viewer"])).status_code==403
def test_evaluar_sin_int_evaluate_403(client, seed):
    i=create_ok(client,seed); realize(client,seed,i["entrevista_id"]); assert client.post(f"/entrevistas/{i['entrevista_id']}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed["viewer"])).status_code==403
def test_candidato_no_usa_api_interna_403(client, seed): assert client.get("/entrevistas",headers=HC(seed["c1"])).status_code==403
def test_usuario_interno_no_usa_agenda_candidato_403(client, seed): assert client.get("/candidatos/me/entrevistas",headers=H(seed["viewer"])).status_code==403

# --- Creación y validaciones ---
def test_creacion_multiple_tipos_y_entrevistadores(client, seed):
    b = create_ok(client, seed)

    assert b["estado_nombre"] == "Pendiente"
    assert b["usuario_creador_id"] == seed["creator"]
    assert len(b["tipos"]) == 2

    # No asumir orden de salida. La API puede ordenar los tipos por ID/nombre.
    tipos_por_id = {
        int(t["tipo_entrevista_id"]): t
        for t in b["tipos"]
    }

    tecnica_id = seed["types"]["Tecnica"]
    rrhh_id = seed["types"]["RRHH"]

    assert tecnica_id in tipos_por_id
    assert rrhh_id in tipos_por_id

    tecnica = tipos_por_id[tecnica_id]
    rrhh = tipos_por_id[rrhh_id]

    assert {x["usuario_id"] for x in tecnica["entrevistadores"]} == {
        seed["eval1"],
        seed["eval2"],
    }
    assert {x["usuario_id"] for x in rrhh["entrevistadores"]} == {
        seed["recruiter"],
    }
def test_creacion_guarda_primer_tipo_legado(client,seed):
    b=create_ok(client,seed)
    db=TestingSessionLocal(); obj=db.get(entrevista_models.CitaEntrevista,b["entrevista_id"]); assert obj.ctev_tipo_entrevista_id==seed["types"]["Tecnica"]; db.close()
def test_titulo_vacio_422(client,seed):
    p=payload(seed);p["titulo_evento"]="   ";assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_fechas_invertidas_422(client,seed):
    st=utc_future(); p=payload(seed,start=st,end=st-timedelta(minutes=1)); assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_fecha_pasada_422(client,seed):
    st=datetime.now()-timedelta(hours=2);p=payload(seed,start=st,end=st+timedelta(hours=1));assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_tipo_repetido_422(client,seed):
    tid=seed["types"]["Tecnica"];p=payload(seed,tipos=[{"tipo_entrevista_id":tid,"usuarios_ids":[seed['eval1']]},{"tipo_entrevista_id":tid,"usuarios_ids":[seed['eval2']]}]);assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_usuario_repetido_dentro_tipo_422(client,seed):
    tid=seed["types"]["Tecnica"];p=payload(seed,tipos=[{"tipo_entrevista_id":tid,"usuarios_ids":[seed['eval1'],seed['eval1']]}]);assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_sin_tipos_422(client,seed):
    p=payload(seed);p["tipos"]=[];assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_extra_field_422(client,seed):
    p=payload(seed);p["hack"]=1;assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_postulacion_inexistente_404(client,seed):
    assert client.post("/entrevistas",json=payload(seed,post=999999),headers=H(seed["creator"])).status_code==404
def test_postulacion_no_en_entrevista_409(client,seed): assert client.post("/entrevistas",json=payload(seed,post=seed["p3"]),headers=H(seed["creator"])).status_code==409
def test_solicitud_no_en_entrevistas_409(client,seed): assert client.post("/entrevistas",json=payload(seed,post=seed["p4"]),headers=H(seed["creator"])).status_code==409
def test_tipo_inexistente_422(client,seed):
    p=payload(seed,tipos=[{"tipo_entrevista_id":999999,"usuarios_ids":[seed['eval1']]}]);assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_usuario_entrevistador_inexistente_422(client,seed):
    p=payload(seed,tipos=[{"tipo_entrevista_id":seed['types']['Tecnica'],"usuarios_ids":[999999]}]);assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==422
def test_entrevistador_inactivo_409(client,seed):
    p=payload(seed,tipos=[{"tipo_entrevista_id":seed['types']['Tecnica'],"usuarios_ids":[seed['inactive_eval']]}]);assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==409
def test_entrevistador_sin_int_evaluate_409(client,seed):
    p=payload(seed,tipos=[{"tipo_entrevista_id":seed['types']['Tecnica'],"usuarios_ids":[seed['viewer']]}]);assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==409
def test_agenda_duplicada_409(client,seed):
    p=payload(seed); assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==201; assert client.post("/entrevistas",json=p,headers=H(seed["creator"])).status_code==409

# --- Masivo ---
def test_agendamiento_masivo_atomico_ok(client,seed):
    st=utc_future(12);p=payload(seed,start=st,end=st+timedelta(hours=1));p.pop("solicitud_candidato_id");p["solicitudes_candidatos_ids"]=[seed['p1'],seed['p2']]
    r=client.post("/entrevistas/agendar-masivo",json=p,headers=H(seed["creator"])); assert r.status_code==201,r.text; assert r.json()["total_creados"]==2
def test_masivo_ids_vacios_422(client,seed):
    p=payload(seed);p.pop("solicitud_candidato_id");p["solicitudes_candidatos_ids"]=[];assert client.post("/entrevistas/agendar-masivo",json=p,headers=H(seed["creator"])).status_code==422
def test_masivo_ids_duplicados_422(client,seed):
    p=payload(seed);p.pop("solicitud_candidato_id");p["solicitudes_candidatos_ids"]=[seed['p1'],seed['p1']];assert client.post("/entrevistas/agendar-masivo",json=p,headers=H(seed["creator"])).status_code==422
def test_masivo_invalido_no_crea_parcial(client,seed):
    st=utc_future(13);p=payload(seed,start=st,end=st+timedelta(hours=1));p.pop("solicitud_candidato_id");p["solicitudes_candidatos_ids"]=[seed['p1'],seed['p3']]
    r=client.post("/entrevistas/agendar-masivo",json=p,headers=H(seed["creator"]));assert r.status_code==409
    db=TestingSessionLocal(); n=db.scalar(select(__import__('sqlalchemy').func.count()).select_from(entrevista_models.CitaEntrevista)); db.close(); assert n==0

def test_masivo_conflicto_unique_hace_rollback_total(client,seed):
    st=utc_future(14); create_ok(client,seed,post=seed['p1'],start=st,end=st+timedelta(hours=1))
    p=payload(seed,start=st,end=st+timedelta(hours=1));p.pop("solicitud_candidato_id");p["solicitudes_candidatos_ids"]=[seed['p1'],seed['p2']]
    r=client.post("/entrevistas/agendar-masivo",json=p,headers=H(seed["creator"]));assert r.status_code==409
    db=TestingSessionLocal(); rows=list(db.scalars(select(entrevista_models.CitaEntrevista)));db.close();assert len(rows)==1

# --- Consultas/filtros ---
def test_get_y_listado(client,seed):
    i=create_ok(client,seed); assert client.get(f"/entrevistas/{i['entrevista_id']}",headers=H(seed['viewer'])).status_code==200; assert any(x['entrevista_id']==i['entrevista_id'] for x in client.get('/entrevistas',headers=H(seed['viewer'])).json())
def test_get_inexistente_404(client,seed): assert client.get('/entrevistas/999999',headers=H(seed['viewer'])).status_code==404
def test_filtros_principales(client,seed):
    i=create_ok(client,seed); iid=i['entrevista_id']; base=utc_future(10)
    filters=[{"solicitud_id":seed['s1']},{"candidato_id":seed['c1']},{"solicitud_candidato_id":seed['p1']},{"usuario_id":seed['eval1']},{"estado_id":seed['int_states']['Pendiente']},{"tipo_id":seed['types']['Tecnica']},{"fecha_desde":(base-timedelta(days=1)).isoformat()},{"fecha_hasta":(base+timedelta(days=1)).isoformat()}]
    for q in filters:
        r=client.get('/entrevistas',params=q,headers=H(seed['viewer']));assert r.status_code==200,(q,r.text);assert any(x['entrevista_id']==iid for x in r.json()),q
def test_paginacion(client,seed):
    create_ok(client,seed,start=utc_future(15),end=utc_future(15)+timedelta(hours=1));create_ok(client,seed,start=utc_future(16),end=utc_future(16)+timedelta(hours=1));r=client.get('/entrevistas',params={'limit':1},headers=H(seed['viewer']));assert len(r.json())==1
def test_consulta_por_solicitud_y_candidato(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];assert any(x['entrevista_id']==iid for x in client.get(f"/solicitudes/{seed['s1']}/entrevistas",headers=H(seed['viewer'])).json());assert any(x['entrevista_id']==iid for x in client.get(f"/candidatos/{seed['c1']}/entrevistas",headers=H(seed['viewer'])).json())

# --- Edición/participantes ---
def test_patch_datos_convocatoria(client,seed):
    i=create_ok(client,seed);r=client.patch(f"/entrevistas/{i['entrevista_id']}",json={"titulo_evento":"Nuevo","enlace_reunion":None},headers=H(seed['updater']));assert r.status_code==200;rj=r.json();assert rj['titulo_evento']=='Nuevo';assert rj['enlace_reunion'] is None
def test_patch_vacio_422(client,seed):
    i=create_ok(client,seed);assert client.patch(f"/entrevistas/{i['entrevista_id']}",json={},headers=H(seed['updater'])).status_code==422
def test_reemplazar_participantes(client,seed):
    i=create_ok(client,seed);body={"tipos":[{"tipo_entrevista_id":seed['types']['Cliente'],"usuarios_ids":[seed['eval2']]}]};r=client.put(f"/entrevistas/{i['entrevista_id']}/participantes",json=body,headers=H(seed['updater']));assert r.status_code==200;rj=r.json();assert len(rj['tipos'])==1;assert rj['tipos'][0]['nombre']=='Cliente'
def test_participantes_con_evaluacion_no_modificables(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id']
    db=TestingSessionLocal();ev=entrevista_models.EvaluacionEntrevista(even_nombre_resultado_id=seed['results']['Aprobado'],even_cita_entrevista_id=iid,even_usuario_id=seed['eval1'],even_tipo_entrevista_id=seed['types']['Tecnica'],even_fecha_creacion=datetime.now(),even_fecha_actualizacion=datetime.now());db.add(ev);db.commit();db.close()
    body={"tipos":[{"tipo_entrevista_id":seed['types']['Cliente'],"usuarios_ids":[seed['eval2']]}]};assert client.put(f"/entrevistas/{iid}/participantes",json=body,headers=H(seed['updater'])).status_code==409

# --- Estados ---
def test_confirmar_pendiente(client,seed):
    i=create_ok(client,seed);r=client.post(f"/entrevistas/{i['entrevista_id']}/confirmar",headers=H(seed['updater']));assert r.status_code==200;assert r.json()['estado_nombre']=='Confirmada'
def test_confirmar_dos_veces_409(client,seed):
    i=create_ok(client,seed);client.post(f"/entrevistas/{i['entrevista_id']}/confirmar",headers=H(seed['updater']));assert client.post(f"/entrevistas/{i['entrevista_id']}/confirmar",headers=H(seed['updater'])).status_code==409
def test_reprogramar(client,seed):
    i=create_ok(client,seed);st=utc_future(20);r=client.post(f"/entrevistas/{i['entrevista_id']}/reprogramar",json={"fecha_hora_inicio":st.isoformat(),"fecha_hora_fin":(st+timedelta(hours=2)).isoformat(),"motivo":"Cambio agenda"},headers=H(seed['updater']));assert r.status_code==200;assert r.json()['estado_nombre']=='Reprogramada';assert r.json()['motivo_estado']=='Cambio agenda'
def test_reprogramar_pasado_422(client,seed):
    i=create_ok(client,seed);st=datetime.now()-timedelta(days=1);r=client.post(f"/entrevistas/{i['entrevista_id']}/reprogramar",json={"fecha_hora_inicio":st.isoformat(),"fecha_hora_fin":(st+timedelta(hours=1)).isoformat(),"motivo":"X"},headers=H(seed['updater']));assert r.status_code==422
def test_cancelar_requiere_motivo_422(client,seed):
    i=create_ok(client,seed);assert client.post(f"/entrevistas/{i['entrevista_id']}/cancelar",json={"motivo":"   "},headers=H(seed['updater'])).status_code==422
def test_cancelar_terminal(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];r=client.post(f"/entrevistas/{iid}/cancelar",json={"motivo":"Cliente cancela"},headers=H(seed['updater']));assert r.status_code==200;assert r.json()['estado_nombre']=='Cancelada';assert client.post(f"/entrevistas/{iid}/confirmar",headers=H(seed['updater'])).status_code==409;assert client.patch(f"/entrevistas/{iid}",json={"titulo_evento":"No"},headers=H(seed['updater'])).status_code==409
def test_no_asistio_terminal(client,seed):
    i=create_ok(client,seed);r=client.post(f"/entrevistas/{i['entrevista_id']}/no-asistio",json={"motivo":"Candidato ausente"},headers=H(seed['updater']));assert r.status_code==200;assert r.json()['estado_nombre']=='No Asistio'
def test_realizar_terminal_para_edicion(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid);assert client.patch(f"/entrevistas/{iid}",json={"titulo_evento":"No"},headers=H(seed['updater'])).status_code==409
def test_si_postulacion_sale_de_en_entrevista_bloquea_transiciones(client,seed):
    i=create_ok(client,seed);db=TestingSessionLocal();p=db.get(solicitud_models.SolicitudCandidato,seed['p1']);p.slcd_estado_solicitud_candidato_id=seed['post_states']['Seleccionado'];db.commit();db.close();assert client.post(f"/entrevistas/{i['entrevista_id']}/confirmar",headers=H(seed['updater'])).status_code==409

# --- Evaluaciones múltiples/autoria ---
def test_no_evaluar_antes_de_realizada_409(client,seed):
    i=create_ok(client,seed);r=client.post(f"/entrevistas/{i['entrevista_id']}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval1']));assert r.status_code==409
def test_evaluacion_tipo_inexistente_404(client,seed):
    i=create_ok(client,seed);realize(client,seed,i['entrevista_id']);assert client.post(f"/entrevistas/{i['entrevista_id']}/tipos/999999/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval1'])).status_code==404
def test_evaluador_no_asignado_409(client,seed):
    i=create_ok(client,seed);realize(client,seed,i['entrevista_id']);assert client.post(f"/entrevistas/{i['entrevista_id']}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval_only'])).status_code==409
def test_resultado_inexistente_422(client,seed):
    i=create_ok(client,seed);realize(client,seed,i['entrevista_id']);assert client.post(f"/entrevistas/{i['entrevista_id']}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":999999},headers=H(seed['eval1'])).status_code==422
def test_dos_entrevistadores_mismo_tipo_dos_evaluaciones(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid)
    for uid,res in [(seed['eval1'],seed['results']['Aprobado']),(seed['eval2'],seed['results']['No Aprobado'])]:
        r=client.post(f"/entrevistas/{iid}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":res,"observacion":"QA"},headers=H(uid));assert r.status_code==201,r.text
    rows=client.get(f"/entrevistas/{iid}/evaluaciones",headers=H(seed['viewer'])).json();assert len(rows)==2;assert {x['usuario_id'] for x in rows}=={seed['eval1'],seed['eval2']}
def test_mismo_usuario_dos_tipos_dos_evaluaciones(client,seed):
    tipos=[{"tipo_entrevista_id":seed['types']['Tecnica'],"usuarios_ids":[seed['eval1']]},{"tipo_entrevista_id":seed['types']['RRHH'],"usuarios_ids":[seed['eval1']]}];i=create_ok(client,seed,tipos=tipos);iid=i['entrevista_id'];realize(client,seed,iid)
    for tid in [seed['types']['Tecnica'],seed['types']['RRHH']]: assert client.post(f"/entrevistas/{iid}/tipos/{tid}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval1'])).status_code==201
    assert len(client.get(f"/entrevistas/{iid}/evaluaciones",headers=H(seed['viewer'])).json())==2
def test_evaluacion_duplicada_mismo_usuario_tipo_409(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid);url=f"/entrevistas/{iid}/tipos/{seed['types']['Tecnica']}/evaluar";assert client.post(url,json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval1'])).status_code==201;assert client.post(url,json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval1'])).status_code==409
def test_editar_solo_mi_evaluacion(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid);tid=seed['types']['Tecnica'];client.post(f"/entrevistas/{iid}/tipos/{tid}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado'],"observacion":"Inicial"},headers=H(seed['eval1']))
    r=client.patch(f"/entrevistas/{iid}/tipos/{tid}/evaluacion",json={"nombre_resultado_id":seed['results']['Aprobado con Observaciones'],"observacion":"Editada"},headers=H(seed['eval1']));assert r.status_code==200;assert r.json()['observacion']=='Editada'
    other=client.patch(f"/entrevistas/{iid}/tipos/{tid}/evaluacion",json={"observacion":"Hack"},headers=H(seed['eval2']));assert other.status_code==404
def test_patch_evaluacion_vacio_422(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid);tid=seed['types']['Tecnica'];client.post(f"/entrevistas/{iid}/tipos/{tid}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval1']));assert client.patch(f"/entrevistas/{iid}/tipos/{tid}/evaluacion",json={},headers=H(seed['eval1'])).status_code==422
def test_listar_evaluaciones_con_int_evaluate_sin_view(client,seed):
    tipos=[{"tipo_entrevista_id":seed['types']['Tecnica'],"usuarios_ids":[seed['eval_only']]}];i=create_ok(client,seed,tipos=tipos);iid=i['entrevista_id'];realize(client,seed,iid);client.post(f"/entrevistas/{iid}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado']},headers=H(seed['eval_only']));assert client.get(f"/entrevistas/{iid}/evaluaciones",headers=H(seed['eval_only'])).status_code==200
def test_evaluacion_no_cambia_estado_postulacion(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid);client.post(f"/entrevistas/{iid}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":seed['results']['No Aprobado']},headers=H(seed['eval1']))
    db=TestingSessionLocal();p=db.get(solicitud_models.SolicitudCandidato,seed['p1']);state=p.slcd_estado_solicitud_candidato_id;db.close();assert state==seed['post_states']['En entrevista']

# --- Agenda entrevistador/candidato ---
def test_mis_entrevistas_solo_asignadas_y_tipos_propios(client,seed):
    i=create_ok(client,seed);rows=client.get('/entrevistas/me',headers=H(seed['eval1'])).json();assert [x['entrevista_id'] for x in rows]==[i['entrevista_id']];assert len(rows[0]['tipos_asignados'])==1;assert rows[0]['tipos_asignados'][0]['nombre']=='Tecnica';assert client.get('/entrevistas/me',headers=H(seed['viewer'])).json()==[]
def test_agenda_candidato_muestra_sin_resultados(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];realize(client,seed,iid);client.post(f"/entrevistas/{iid}/tipos/{seed['types']['Tecnica']}/evaluar",json={"nombre_resultado_id":seed['results']['Aprobado'],"observacion":"SECRETO"},headers=H(seed['eval1']))
    r=client.get('/candidatos/me/entrevistas',headers=HC(seed['c1']));assert r.status_code==200;item=next(x for x in r.json() if x['entrevista_id']==iid);assert item['estado']=='Realizada';assert 'evaluaciones' not in item;assert 'resultado' not in str(item).lower();assert 'SECRETO' not in str(item)
def test_detalle_candidato_solo_propietario(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];assert client.get(f"/candidatos/me/entrevistas/{iid}",headers=HC(seed['c1'])).status_code==200;assert client.get(f"/candidatos/me/entrevistas/{iid}",headers=HC(seed['c2'])).status_code==404
def test_agenda_candidato_conserva_canceladas(client,seed):
    i=create_ok(client,seed);iid=i['entrevista_id'];client.post(f"/entrevistas/{iid}/cancelar",json={"motivo":"QA"},headers=H(seed['updater']));rows=client.get('/candidatos/me/entrevistas',headers=HC(seed['c1'])).json();assert any(x['entrevista_id']==iid and x['estado']=='Cancelada' for x in rows)

