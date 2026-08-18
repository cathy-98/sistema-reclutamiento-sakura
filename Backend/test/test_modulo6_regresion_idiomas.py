import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ADMIN_TOKEN = os.getenv("QA_ADMIN_TOKEN")
APPROVED_SLCD_ID = os.getenv("QA_M6_APPROVED_SLCD_ID")

def auth():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}

@pytest.mark.skipif(not ADMIN_TOKEN, reason="Requiere QA_ADMIN_TOKEN")
def test_m6_listado_sigue_operativo():
    r = client.get("/informes/candidatos", headers=auth())
    assert r.status_code == 200

@pytest.mark.skipif(not ADMIN_TOKEN or not APPROVED_SLCD_ID, reason="Requiere QA_ADMIN_TOKEN y QA_M6_APPROVED_SLCD_ID")
def test_m6_cv_corporativo_sigue_generando():
    r = client.post(
        f"/informes/candidatos/{APPROVED_SLCD_ID}/cv-corporativo",
        headers=auth(),
        json={}
    )
    assert r.status_code in (200, 201)
