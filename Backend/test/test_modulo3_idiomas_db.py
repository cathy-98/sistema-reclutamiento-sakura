from sqlalchemy import inspect, text
from app.database import engine

def test_tabla_nivel_idioma_existe():
    insp = inspect(engine)
    assert "tbl_nivel_idioma" in insp.get_table_names()

def test_candidato_idioma_esta_normalizada():
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns("tbl_candidato_idioma")}
    assert "cdio_nivel_idioma_id" in cols
    assert "cdio_nivel" not in cols

def test_fk_nivel_idioma_existe():
    insp = inspect(engine)
    fks = insp.get_foreign_keys("tbl_candidato_idioma")
    assert any(
        fk.get("referred_table") == "tbl_nivel_idioma"
        and "cdio_nivel_idioma_id" in fk.get("constrained_columns", [])
        for fk in fks
    )

def test_seeds_nivel_idioma():
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT nvid_codigo FROM tbl_nivel_idioma WHERE nvid_activo = true"
        )).fetchall()
    codigos = {r[0] for r in rows}
    assert {"BAS","A1","A2","INT","B1","B2","AVA","C1","C2","NAT"} <= codigos
