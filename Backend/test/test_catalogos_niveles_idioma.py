from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_openapi_expone_catalogos_idioma():
    schema = client.get("/openapi.json").json()
    assert "/catalogos/niveles-idioma" in schema["paths"]
    assert "/catalogos/idiomas" in schema["paths"]

def test_catalogo_niveles_idioma_lista():
    r = client.get("/catalogos/niveles-idioma")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    codigos = {x.get("nvid_codigo") for x in data}
    assert {"BAS","A1","A2","INT","B1","B2","AVA","C1","C2","NAT"} <= codigos

def test_catalogo_niveles_idioma_campos():
    r = client.get("/catalogos/niveles-idioma")
    assert r.status_code == 200
    assert r.json()
    item = r.json()[0]
    for campo in (
        "nvid_id","nvid_codigo","nvid_nombre","nvid_grupo",
        "nvid_es_generico","nvid_orden","nvid_activo"
    ):
        assert campo in item
