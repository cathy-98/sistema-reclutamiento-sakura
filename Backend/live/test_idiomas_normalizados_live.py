import os
import sys
import requests

API = os.getenv("QA_API_URL", "http://127.0.0.1:8000").rstrip("/")
EMAIL = os.getenv("QA_ADMIN_EMAIL")
PASSWORD = os.getenv("QA_ADMIN_PASSWORD")
CANDIDATE_ID = os.getenv("QA_CANDIDATE_ID")
APPROVED_SLCD_ID = os.getenv("QA_M6_APPROVED_SLCD_ID")

def fail(msg):
    print("[FAIL]", msg)
    sys.exit(1)

if not EMAIL or not PASSWORD:
    fail("Configure QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD")

s = requests.Session()
r = s.post(f"{API}/auth/login", data={"username": EMAIL, "password": PASSWORD})
if r.status_code != 200:
    r = s.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD})
if r.status_code != 200:
    fail(f"Login admin: {r.status_code} {r.text}")

data = r.json()
token = data.get("access_token") or data.get("token")
if not token:
    fail("Login no devolvió token")

headers = {"Authorization": f"Bearer {token}"}
count = 0

def check(name, ok, detail=""):
    global count
    if not ok:
        fail(f"{name}: {detail}")
    count += 1
    print(f"[PASS {count:02d}] {name}")

r = s.get(f"{API}/openapi.json")
check("OpenAPI disponible", r.status_code == 200, r.text)
paths = r.json().get("paths", {})

for p in (
    "/catalogos/niveles-idioma",
    "/catalogos/idiomas",
    "/candidatos/{candidate_id}/idiomas",
    "/candidatos/me/idiomas",
    "/informes/candidatos",
):
    check(f"OpenAPI registra {p}", p in paths)

r = s.get(f"{API}/catalogos/niveles-idioma", headers=headers)
check("Listado niveles idioma", r.status_code == 200, r.text)
codigos = {x.get("nvid_codigo") for x in r.json()}
check(
    "Seeds niveles idioma completos",
    {"BAS","A1","A2","INT","B1","B2","AVA","C1","C2","NAT"} <= codigos,
    str(codigos)
)

if CANDIDATE_ID:
    r = s.get(f"{API}/candidatos/{CANDIDATE_ID}/idiomas", headers=headers)
    check("Idiomas candidato por admin", r.status_code == 200, r.text)
    if r.json():
        item = r.json()[0]
        check(
            "Idioma candidato usa FK nivel normalizado",
            "cdio_nivel_idioma_id" in item and "nivel_idioma" in item,
            str(item)
        )

if APPROVED_SLCD_ID:
    r = s.post(
        f"{API}/informes/candidatos/{APPROVED_SLCD_ID}/cv-corporativo",
        headers=headers,
        json={}
    )
    check("M6 CV corporativo después de 008", r.status_code in (200, 201), r.text[:400])

print(f"\nRESULTADO: PASSED ({count} casos LIVE)")
