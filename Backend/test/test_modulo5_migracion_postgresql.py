from __future__ import annotations

import pytest
from sqlalchemy import inspect, text

from app.database import engine

pytestmark = pytest.mark.skipif(
    engine.dialect.name != "postgresql",
    reason="Estas verificaciones corresponden a la migración 006 en PostgreSQL real",
)


def scalar(sql: str):
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar()


def rows(sql: str):
    with engine.connect() as conn:
        return conn.execute(text(sql)).mappings().all()


def test_m5_tablas_existen():
    names = set(inspect(engine).get_table_names())
    for table in ["tbl_cita_entrevista", "tbl_cita_tipo_entrevista", "tbl_usuario_cita_entrevista", "tbl_evaluacion_entrevista"]:
        assert table in names


def test_columnas_m5_cita_existen():
    cols = {x["name"] for x in inspect(engine).get_columns("tbl_cita_entrevista")}
    assert {"ctev_usuario_creador_id", "ctev_fecha_actualizacion", "ctev_motivo_estado"}.issubset(cols)


def test_columnas_m5_usuario_cita_existen():
    cols = {x["name"] for x in inspect(engine).get_columns("tbl_usuario_cita_entrevista")}
    assert "usrce_tipo_entrevista_id" in cols
    assert next(x for x in inspect(engine).get_columns("tbl_usuario_cita_entrevista") if x["name"] == "usrce_tipo_entrevista_id")["nullable"] is False


def test_pk_usuario_cita_incluye_tipo():
    pk = inspect(engine).get_pk_constraint("tbl_usuario_cita_entrevista")
    assert set(pk["constrained_columns"]) == {"usrce_cita_entrevista_id", "usrce_usuario_id", "usrce_tipo_entrevista_id"}


def test_columnas_m5_evaluacion_existen():
    cols = {x["name"] for x in inspect(engine).get_columns("tbl_evaluacion_entrevista")}
    assert {"even_usuario_id", "even_tipo_entrevista_id", "even_fecha_creacion", "even_fecha_actualizacion"}.issubset(cols)


def test_indice_unico_evaluacion_usuario_tipo():
    idx = {x["name"]: x for x in inspect(engine).get_indexes("tbl_evaluacion_entrevista")}
    assert "uq_m5_evaluacion_cita_usuario_tipo" in idx
    assert idx["uq_m5_evaluacion_cita_usuario_tipo"]["unique"] is True


def test_reclutador_tiene_int_evaluate():
    count = scalar("""
        SELECT COUNT(*)
        FROM tbl_rol r
        JOIN tbl_rol_permiso rp ON rp.rlpm_rol_id = r.rol_id
        JOIN tbl_permiso p ON p.per_id = rp.rlpm_permiso_id
        WHERE lower(r.rol_nombre) = lower('Reclutador')
          AND p.per_nombre = 'INT_EVALUATE'
    """)
    assert int(count or 0) >= 1


def test_estados_entrevista_requeridos():
    found = {r["esev_nombre"] for r in rows("SELECT esev_nombre FROM tbl_estado_entrevista")}
    assert {"Pendiente", "Confirmada", "Realizada", "Reprogramada", "Cancelada", "No Asistio"}.issubset(found)


def test_catalogos_tipo_y_resultado_no_vacios():
    assert int(scalar("SELECT COUNT(*) FROM tbl_tipo_entrevista") or 0) >= 2
    assert int(scalar("SELECT COUNT(*) FROM tbl_nombre_resultado") or 0) >= 1


def test_no_hay_asignaciones_m5_sin_tipo():
    assert int(scalar("SELECT COUNT(*) FROM tbl_usuario_cita_entrevista WHERE usrce_tipo_entrevista_id IS NULL") or 0) == 0


def test_evaluaciones_m5_no_duplicadas_usuario_tipo():
    duplicates = rows("""
        SELECT even_cita_entrevista_id, even_usuario_id, even_tipo_entrevista_id, COUNT(*) AS n
        FROM tbl_evaluacion_entrevista
        WHERE even_usuario_id IS NOT NULL AND even_tipo_entrevista_id IS NOT NULL
        GROUP BY even_cita_entrevista_id, even_usuario_id, even_tipo_entrevista_id
        HAVING COUNT(*) > 1
    """)
    assert duplicates == []
