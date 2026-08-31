import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ADMIN_TOKEN = os.getenv("QA_ADMIN_TOKEN")
CANDIDATE_TOKEN = os.getenv("QA_CANDIDATE_TOKEN")
CANDIDATE_ID = os.getenv("QA_CANDIDATE_ID")

def auth(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.skipif(not ADMIN_TOKEN or not CANDIDATE_ID, reason="Requiere QA_ADMIN_TOKEN y QA_CANDIDATE_ID")
def test_admin_lista_idiomas_candidato():
    r = client.get(f"/candidatos/{CANDIDATE_ID}/idiomas", headers=auth(ADMIN_TOKEN))
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.skipif(not CANDIDATE_TOKEN, reason="Requiere QA_CANDIDATE_TOKEN")
def test_candidato_lista_sus_idiomas():
    r = client.get("/candidatos/me/idiomas", headers=auth(CANDIDATE_TOKEN))
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.skipif(not CANDIDATE_TOKEN, reason="Requiere QA_CANDIDATE_TOKEN")
def test_perfil_completo_incluye_idiomas():
    r = client.get("/candidatos/me/perfil-completo", headers=auth(CANDIDATE_TOKEN))
    assert r.status_code == 200
    assert "idiomas" in r.json()
