from __future__ import annotations
import os
import pytest
from sqlalchemy import create_engine, text

URL=os.getenv('DATABASE_URL') or os.getenv('SAKURA_DATABASE_URL')
pytestmark=pytest.mark.skipif(not URL or URL.startswith('sqlite'), reason='Requiere PostgreSQL real mediante DATABASE_URL')

def q(sql,params=None):
    e=create_engine(URL,pool_pre_ping=True)
    try:
        with e.connect() as c: return c.execute(text(sql),params or {}).mappings().all()
    finally: e.dispose()

def scalar(sql,params=None):
    rows=q(sql,params); return next(iter(rows[0].values())) if rows else None

@pytest.mark.parametrize('table',["tbl_categoria_habilidad","tbl_idioma","tbl_candidato_idioma","tbl_documento_reporte_candidato","tbl_plantilla_notificacion","tbl_notificacion_reclutamiento"])
def test_tablas_m6_existen(table): assert scalar("SELECT to_regclass(:n) IS NOT NULL AS ok",{'n':f'public.{table}'}) is True

def test_columna_categoria_en_habilidad(): assert scalar("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='tbl_habilidad' AND column_name='hab_categoria_habilidad_id') AS ok") is True

def test_fk_habilidad_categoria(): assert scalar("SELECT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='fk_tbl_habilidad_categoria_habilidad') AS ok") is True

def test_categorias_seed():
    names={r['cthb_nombre'] for r in q('SELECT cthb_nombre FROM tbl_categoria_habilidad')}; assert {'Lenguajes','Frameworks / Librerías','Bases de Datos','Cloud / DevOps','Herramientas','Metodologías','Otros'}<=names

def test_idiomas_seed():
    names={r['idio_nombre'] for r in q('SELECT idio_nombre FROM tbl_idioma')}; assert {'Español','Inglés','Portugués','Francés','Alemán','Italiano','Otro'}<=names

def test_idioma_unique_candidato_idioma(): assert scalar("SELECT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='uq_tbl_candidato_idioma') AS ok") is True

def test_check_nivel_idioma(): assert scalar("SELECT EXISTS(SELECT 1 FROM pg_constraint WHERE conname='chk_tbl_candidato_idioma_nivel') AS ok") is True

def test_documento_checks():
    names={r['conname'] for r in q("SELECT conname FROM pg_constraint WHERE conrelid='tbl_documento_reporte_candidato'::regclass")}; assert {'chk_tbl_documento_reporte_tipo','chk_tbl_documento_reporte_hash'}<=names

def test_notificacion_checks():
    names={r['conname'] for r in q("SELECT conname FROM pg_constraint WHERE conrelid='tbl_notificacion_reclutamiento'::regclass")}; assert {'chk_tbl_notificacion_tipo','chk_tbl_notificacion_estado'}<=names

def test_plantillas_seed_activas():
    rows=q("SELECT plnt_tipo,plnt_activa FROM tbl_plantilla_notificacion"); mp={x['plnt_tipo']:x['plnt_activa'] for x in rows}; assert mp.get('RECHAZO') is True and mp.get('AGRADECIMIENTO') is True and mp.get('DIRECTIVOS') is True

def test_indices_documentos():
    names={r['indexname'] for r in q("SELECT indexname FROM pg_indexes WHERE schemaname='public' AND tablename='tbl_documento_reporte_candidato'")}; assert 'ix_tbl_documento_reporte_postulacion' in names and 'ix_tbl_documento_reporte_fecha' in names

def test_indices_notificaciones():
    names={r['indexname'] for r in q("SELECT indexname FROM pg_indexes WHERE schemaname='public' AND tablename='tbl_notificacion_reclutamiento'")}; assert {'ix_tbl_notificacion_postulacion','ix_tbl_notificacion_fecha','ix_tbl_notificacion_estado'}<=names

def test_rep_view_existe(): assert scalar("SELECT EXISTS(SELECT 1 FROM tbl_permiso WHERE per_nombre='REP_VIEW') AS ok") is True

def test_reclutador_con_rep_view():
    assert scalar("""SELECT EXISTS(SELECT 1 FROM tbl_rol r JOIN tbl_rol_permiso rp ON rp.rlpm_rol_id=r.rol_id JOIN tbl_permiso p ON p.per_id=rp.rlpm_permiso_id WHERE lower(r.rol_nombre)=lower('Reclutador') AND p.per_nombre='REP_VIEW') AS ok""") is True

def test_no_documentos_hash_invalido(): assert scalar("SELECT COUNT(*)=0 AS ok FROM tbl_documento_reporte_candidato WHERE length(drcp_hash_sha256)<>64") is True

def test_no_idiomas_duplicados(): assert scalar("SELECT COUNT(*)=0 AS ok FROM (SELECT cdio_candidato_id,cdio_idioma_id,COUNT(*) n FROM tbl_candidato_idioma GROUP BY 1,2 HAVING COUNT(*)>1)x") is True
