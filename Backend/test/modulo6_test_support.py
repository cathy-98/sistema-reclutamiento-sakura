from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "qa-m6-secret-key-0123456789-abcdefghijklmnopqrstuvwxyz")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ACTIVE_USER_STATUS_NAME", "Activo")
os.environ.setdefault("ADMIN_ROLE_NAME", "Administrador")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import utils as auth_utils
from app.catalogos import models as catalog_models
from app.catalogos import router as catalogos_router
from app.clientes import models as cliente_models
from app.candidatos import models as candidato_models
from app.cuestionarios import models as cuestionario_models
from app.database import Base, get_db
from app.entrevistas import models as entrevista_models
from app.informes import models as informe_models
from app.informes import router as informes_router
from app.informes import services as informe_services
from app.solicitudes import models as solicitud_models
from app.usuarios import models as user_models

TEST_ENGINE = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

@event.listens_for(TEST_ENGINE, "connect")
def _fk_on(dbapi_connection, _record):
    cur = dbapi_connection.cursor(); cur.execute("PRAGMA foreign_keys=ON"); cur.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
app_test = FastAPI(title="QA M6")
app_test.include_router(catalogos_router.router)
app_test.include_router(informes_router.router)

def override_get_db() -> Iterator[Session]:
    db = TestingSessionLocal()
    try: yield db
    finally: db.close()
app_test.dependency_overrides[get_db] = override_get_db

PERMS = ["REP_VIEW", "CAT_ADMIN", "CAN_VIEW", "CAN_UPDATE"]

def _token(uid: int, principal_type: str = "usuario") -> str:
    return auth_utils.create_access_token({"sub": str(uid), "email": "qa.m6@sakura.cl", "principal_type": principal_type})
def H(uid: int): return {"Authorization": f"Bearer {_token(uid)}"}
def HC(cid: int): return {"Authorization": f"Bearer {_token(cid, 'candidato')}"}

def _make_user(db, role, state, area, seq, email):
    u=user_models.Usuario(usr_rol_id=role.rol_id,usr_estado_usuario_id=state.esusr_id,usr_area_id=area.area_id,usr_nombres=f"QA{seq}",usr_apellido_paterno="M6",usr_rut_sin_dv=f"70000{seq}",usr_dv=str(seq%10),usr_email=email,usr_contrasena="hash")
    db.add(u); db.flush(); return u

def _seed():
    db=TestingSessionLocal()
    try:
        activo=user_models.EstadoUsuario(esusr_nombre="Activo",esusr_descripcion="Activo")
        area=user_models.Area(area_nombre="QA M6",area_descripcion="QA")
        db.add_all([activo,area]); db.flush()
        po={n:user_models.Permiso(per_nombre=n,per_descripcion=n) for n in PERMS}; db.add_all(po.values()); db.flush()
        def role(name, perms):
            r=user_models.Rol(rol_nombre=name,rol_descripcion=name,permisos=[po[p] for p in perms]); db.add(r); db.flush(); return r
        ra=role("Administrador",PERMS); rr=role("Reclutador",["REP_VIEW","CAN_VIEW","CAN_UPDATE"]); rv=role("Report",["REP_VIEW"]); rc=role("Catalog",["CAT_ADMIN"]); rcv=role("CandidateView",["CAN_VIEW"]); rcu=role("CandidateUpdate",["CAN_UPDATE"]); rn=role("NoPerm",[])
        admin=_make_user(db,ra,activo,area,1,"admin.m6@sakura.cl"); recruiter=_make_user(db,rr,activo,area,2,"recruiter.m6@sakura.cl"); reporter=_make_user(db,rv,activo,area,3,"report.m6@sakura.cl"); catalog=_make_user(db,rc,activo,area,4,"catalog.m6@sakura.cl"); canview=_make_user(db,rcv,activo,area,5,"canview.m6@sakura.cl"); canupdate=_make_user(db,rcu,activo,area,6,"canupdate.m6@sakura.cl"); noperm=_make_user(db,rn,activo,area,7,"noperm.m6@sakura.cl")

        disp=catalog_models.Disponibilidad(disp_nombre="Inmediata"); cargo=catalog_models.Cargo(crgo_nombre="Backend Senior",crgo_descripcion="Backend"); cargo2=catalog_models.Cargo(crgo_nombre="Data Engineer",crgo_descripcion="Data")
        pais=catalog_models.Pais(pais_nombre="Chile"); db.add_all([disp,cargo,cargo2,pais]); db.flush()
        reg=catalog_models.Region(reg_pais_id=pais.pais_id,reg_nombre="Metropolitana"); db.add(reg); db.flush(); com=catalog_models.Comuna(com_region_id=reg.reg_id,com_nombre="Santiago"); db.add(com)
        tipo_inst=catalog_models.TipoInstitucion(tint_tipo_institucion="Universidad"); db.add(tipo_inst); db.flush(); inst=catalog_models.Institucion(inst_nombre="Universidad QA",inst_tipo_institucion_id=tipo_inst.tint_id); carrera=catalog_models.Carrera(crra_nombre="Ingeniería Informática"); nivel_edu=catalog_models.NivelEducacional(nved_nombre="Universitario"); db.add_all([inst,carrera,nivel_edu])
        niv=catalog_models.NivelHabilidad(nvhb_nombre="Avanzado",nvhb_descripcion="Avanzado",nvhb_puntaje_base=50,nvhb_duracion=5); skill=catalog_models.Habilidad(hab_nombre="Python",hab_descripcion="Python"); skill2=catalog_models.Habilidad(hab_nombre="PostgreSQL",hab_descripcion="PostgreSQL"); db.add_all([niv,skill,skill2]); db.flush()
        cat_lang=informe_models.CategoriaHabilidad(cthb_nombre="Lenguajes",cthb_descripcion="Lenguajes"); cat_db=informe_models.CategoriaHabilidad(cthb_nombre="Bases de Datos",cthb_descripcion="BD"); lang_es=informe_models.Idioma(idio_nombre="Español"); lang_en=informe_models.Idioma(idio_nombre="Inglés"); db.add_all([cat_lang,cat_db,lang_es,lang_en]); db.flush()
        db.execute(text("UPDATE tbl_habilidad SET hab_categoria_habilidad_id=:c WHERE hab_id=:h"),{"c":cat_lang.cthb_id,"h":skill.hab_id}); db.execute(text("UPDATE tbl_habilidad SET hab_categoria_habilidad_id=:c WHERE hab_id=:h"),{"c":cat_db.cthb_id,"h":skill2.hab_id})
        req_states={}; post_states={}; qstates={}; istates={}; types={}; results={}
        for n in ["Pendiente","En Curso","En Entrevistas","Cancelado","Cerrado","Pausado"]:
            o=catalog_models.EstadoSolicitud(essl_nombre=n,essl_descripcion=n); db.add(o); db.flush(); req_states[n]=o.essl_id
        for n in ["En revision","En entrevista","Inhabilitado","Seleccionado","Descartado","Contratado"]:
            o=catalog_models.EstadoSolicitudCandidato(essc_nombre=n,essc_descripcion=n); db.add(o); db.flush(); post_states[n]=o.essc_id
        for n in ["Asignado","En Progreso","Finalizado","Vencido","Cancelado","Error Tecnico"]:
            o=catalog_models.EstadoCuestionarioCandidato(escc_nombre=n); db.add(o); db.flush(); qstates[n]=o.escc_id
        for n in ["Pendiente","Confirmada","Realizada","Reprogramada","Cancelada","No Asistio"]:
            o=catalog_models.EstadoEntrevista(esev_nombre=n,esev_descripcion=n); db.add(o); db.flush(); istates[n]=o.esev_id
        for n in ["RRHH","Tecnica"]:
            o=catalog_models.TipoEntrevista(tpet_nombre=n,tpet_descripcion=n); db.add(o); db.flush(); types[n]=o.tpet_id
        for n in ["Aprobado","Aprobado con Observaciones","No Aprobado","En Espera","Requiere Segunda Entrevista"]:
            o=catalog_models.NombreResultado(nore_nombre=n); db.add(o); db.flush(); results[n]=o.nore_id

        company=cliente_models.Empresa(emp_nombre="ELITSOFT QA",emp_identificacion="M6-QA"); db.add(company); db.flush()
        s1=solicitud_models.Solicitud(sol_codigo="SOL-M60001",sol_titulo="Backend QA",sol_cantidad_vacantes=5,sol_estado_solicitud_id=req_states["En Entrevistas"],sol_usuario_creador_id=admin.usr_id,sol_usuario_asignado_id=recruiter.usr_id,sol_cargo_id=cargo.crgo_id)
        s2=solicitud_models.Solicitud(sol_codigo="SOL-M60002",sol_titulo="Data QA",sol_cantidad_vacantes=2,sol_estado_solicitud_id=req_states["En Entrevistas"],sol_usuario_creador_id=admin.usr_id,sol_usuario_asignado_id=recruiter.usr_id,sol_cargo_id=cargo2.crgo_id)
        db.add_all([s1,s2]); db.flush()

        def cand(i,name):
            c=candidato_models.Candidato(cand_email=f"cand{i}.m6@sakura.cl",cand_password="hash",cand_nombres=name,cand_apellido_paterno="QA",cand_telefono=f"9000000{i}",cand_disponibilidad_id=disp.disp_id,cand_resumen_profesional=f"Perfil profesional {name}",cand_titulo="Ingeniero de Software",cand_estado_usuario_id=activo.esusr_id); db.add(c); db.flush(); return c
        csel=cand(1,"Seleccionado"); ccon=cand(2,"Contratado"); cdes=cand(3,"Descartado"); cinh=cand(4,"Inhabilitado"); crev=cand(5,"Revision"); cpass=cand(6,"AprobadoSugerido"); cfailt=cand(7,"FallaTest"); cpendt=cand(8,"TestPendiente"); cfaili=cand(9,"FallaEntrevista"); cpendi=cand(10,"EntrevistaPendiente"); cnoinv=cand(11,"SinEntrevista"); csecond=cand(12,"SegundoCargo")
        candidates=[csel,ccon,cdes,cinh,crev,cpass,cfailt,cpendt,cfaili,cpendi,cnoinv,csecond]
        for c in candidates:
            db.add(candidato_models.CandidatoHabilidad(cdhb_candidato_id=c.cand_id,cdhb_habilidad_id=skill.hab_id,cdhb_nivel_habilidad_id=niv.nvhb_id,cdhb_anios_experiencia=4))
        db.add(candidato_models.CandidatoHabilidad(cdhb_candidato_id=csel.cand_id,cdhb_habilidad_id=skill2.hab_id,cdhb_nivel_habilidad_id=niv.nvhb_id,cdhb_anios_experiencia=3))
        db.add(candidato_models.DireccionCandidato(drcd_candidato_id=csel.cand_id,drcd_comuna_id=com.com_id,drcd_calle="QA",drcd_numero=1))
        db.add(candidato_models.EstudioCandidato(etcd_candidato_id=csel.cand_id,etcd_nivel_educacional_id=nivel_edu.nved_id,etcd_institucion_id=inst.inst_id,etcd_carrera_id=carrera.crra_id,etcd_fecha_inicio=date(2015,1,1),etcd_fecha_fin=date(2020,1,1)))
        db.add(candidato_models.ExperienciaLaboral(expl_candidato_id=csel.cand_id,expl_empresa_id=company.emp_id,expl_cargo_id=cargo.crgo_id,expl_descripcion_funciones="Desarrollo de APIs y arquitectura.",expl_fecha_inicio=date(2021,1,1),expl_fecha_fin=None))
        db.add(candidato_models.Curso(curs_candidato_id=csel.cand_id,curs_nombre_curso="AWS Cloud",curs_es_certificado=True,curs_anio_curso=2025))
        db.add(informe_models.CandidatoIdioma(cdio_candidato_id=csel.cand_id,cdio_idioma_id=lang_es.idio_id,cdio_nivel="Nativo"))

        def post(c,state,match=80,s=s1):
            p=solicitud_models.SolicitudCandidato(slcd_candidato_id=c.cand_id,slcd_solicitud_id=s.sol_id,slcd_estado_solicitud_candidato_id=post_states[state],slcd_fecha_postulacion=datetime.now(),slcd_puntaje_compatibilidad=match); db.add(p); db.flush(); return p
        psel=post(csel,"Seleccionado",95); pcon=post(ccon,"Contratado",93); pdes=post(cdes,"Descartado",40); pinh=post(cinh,"Inhabilitado",35); prev=post(crev,"En revision",70); ppass=post(cpass,"En entrevista",88); pfailt=post(cfailt,"En entrevista",55); ppendt=post(cpendt,"En entrevista",75); pfaili=post(cfaili,"En entrevista",65); ppendi=post(cpendi,"En entrevista",72); pnoinv=post(cnoinv,"En entrevista",81); psecond=post(csecond,"Seleccionado",91,s2)

        q=cuestionario_models.Cuestionario(cues_id=1,cues_nombre="Test Backend",cues_descripcion="QA",cues_porcentaje_aprobacion=60,cues_solicitud_id=s1.sol_id); db.add(q); db.flush()
        now=datetime.now()
        def assign(c,approved,pct,state="Finalizado"):
            a=cuestionario_models.CandidatoCuestionario(cdcu_id=None,cdcu_candidato_id=c.cand_id,cdcu_cuestionario_id=q.cues_id,cdcu_fecha_asignacion=now,cdcu_fecha_vencimiento=now+timedelta(days=2),cdcu_fecha_resolucion=now if approved is not None else None,cdcu_porcentaje_obtenido=pct,cdcu_estado_cuestionario_candidato_id=qstates[state],cdcu_permitir_reintento=False,cdcu_aprobado=approved); db.add(a)
        assign(cpass,True,90); assign(cfailt,False,40); assign(cpendt,None,None,"Asignado"); assign(cfaili,True,85); assign(cpendi,True,82); assign(cnoinv,True,86)

        def interview(p,c,result=None,state="Realizada"):
            ce=entrevista_models.CitaEntrevista(ctev_solicitud_candidato_id=p.slcd_id,ctev_tipo_entrevista_id=types["Tecnica"],ctev_estado_entrevista_id=istates[state],ctev_fecha_hora_inicio=now+timedelta(days=1),ctev_fecha_hora_fin=now+timedelta(days=1,hours=1),ctev_fecha_creacion=now,ctev_titulo_evento="Entrevista QA",ctev_usuario_creador_id=admin.usr_id); db.add(ce); db.flush(); db.add(entrevista_models.CitaTipoEntrevista(cten_tipo_entrevista_id=types["Tecnica"],cten_cita_entrevista_id=ce.ctev_id)); db.add(entrevista_models.UsuarioCitaEntrevista(usrce_cita_entrevista_id=ce.ctev_id,usrce_usuario_id=recruiter.usr_id,usrce_tipo_entrevista_id=types["Tecnica"]));
            if result:
                db.add(entrevista_models.EvaluacionEntrevista(even_nombre_resultado_id=results[result],even_observacion="QA",even_cita_entrevista_id=ce.ctev_id,even_usuario_id=recruiter.usr_id,even_tipo_entrevista_id=types["Tecnica"],even_fecha_creacion=now,even_fecha_actualizacion=now))
        interview(ppass,cpass,"Aprobado"); interview(pfaili,cfaili,"No Aprobado"); interview(ppendi,cpendi,"En Espera")

        for kind,name,subject,body in [
            ("RECHAZO","Rechazo","Cierre - {cargo}","Hola {nombre}, cierre {codigo_solicitud}."),
            ("AGRADECIMIENTO","Gracias","Gracias - {cargo}","Gracias {nombre} por {solicitud}."),
            ("DIRECTIVOS","Directivos","Aprobados - {cargo} - {codigo_solicitud}","Adjuntos candidatos para {solicitud}.")]:
            db.add(informe_models.PlantillaNotificacion(plnt_tipo=kind,plnt_nombre=name,plnt_asunto=subject,plnt_cuerpo=body,plnt_activa=True))
        db.commit()
        return dict(admin=admin.usr_id,recruiter=recruiter.usr_id,reporter=reporter.usr_id,catalog=catalog.usr_id,canview=canview.usr_id,canupdate=canupdate.usr_id,noperm=noperm.usr_id,
                    csel=csel.cand_id,cdes=cdes.cand_id,skill=skill.hab_id,skill2=skill2.hab_id,cat_lang=cat_lang.cthb_id,cat_db=cat_db.cthb_id,lang_es=lang_es.idio_id,lang_en=lang_en.idio_id,cargo=cargo.crgo_id,cargo2=cargo2.crgo_id,disp=disp.disp_id,s1=s1.sol_id,s2=s2.sol_id,post_states=post_states,
                    psel=psel.slcd_id,pcon=pcon.slcd_id,pdes=pdes.slcd_id,pinh=pinh.slcd_id,prev=prev.slcd_id,ppass=ppass.slcd_id,pfailt=pfailt.slcd_id,ppendt=ppendt.slcd_id,pfaili=pfaili.slcd_id,ppendi=ppendi.slcd_id,pnoinv=pnoinv.slcd_id,psecond=psecond.slcd_id)
    finally: db.close()

@pytest.fixture(autouse=True)
def reset_db(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_STORAGE_DIR", str(tmp_path / "informes"))
    # SQLite devuelve BOOLEAN de SQL textual como 0/1. PostgreSQL devuelve bool.
    # Este shim mantiene la semántica productiva de M6 en la suite aislada.
    _orig_tech = informe_services._technical_evaluations
    def _sqlite_bool_tech(db, candidate_id, solicitud_id):
        rows, configured = _orig_tech(db, candidate_id, solicitud_id)
        for row in rows:
            if row.get("aprobado") is not None:
                row["aprobado"] = bool(row["aprobado"])
        return rows, configured
    monkeypatch.setattr(informe_services, "_technical_evaluations", _sqlite_bool_tech)
    _orig_period = informe_services._period
    def _sqlite_period(start, end):
        from datetime import date as _date
        def cv(v):
            if isinstance(v, str):
                try: return _date.fromisoformat(v[:10])
                except ValueError: return v
            return v
        return _orig_period(cv(start), cv(end))
    monkeypatch.setattr(informe_services, "_period", _sqlite_period)
    Base.metadata.drop_all(TEST_ENGINE)
    Base.metadata.create_all(TEST_ENGINE)
    with TEST_ENGINE.begin() as conn:
        # La columna M6 se agrega por migración y no está en el ORM histórico de Habilidad.
        cols=[x[1] for x in conn.execute(text("PRAGMA table_info(tbl_habilidad)")).all()]
        if "hab_categoria_habilidad_id" not in cols:
            conn.execute(text("ALTER TABLE tbl_habilidad ADD COLUMN hab_categoria_habilidad_id INTEGER"))
    app_test.state.seed=_seed()
    yield
    Base.metadata.drop_all(TEST_ENGINE)

@pytest.fixture
def client():
    with TestClient(app_test) as c: yield c
@pytest.fixture
def seed(): return app_test.state.seed
