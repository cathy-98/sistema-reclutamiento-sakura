
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import requests


API = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("QA_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("QA_ADMIN_PASSWORD")
CANDIDATE_EMAIL = os.getenv("QA_M4_CANDIDATE_EMAIL")
CANDIDATE_PASSWORD = os.getenv("QA_M4_CANDIDATE_PASSWORD")
SOLICITUD_ID = os.getenv("QA_M4_SOLICITUD_ID")

TIMEOUT = 20


class LiveFail(RuntimeError):
    pass


def check(name, condition, detail=""):
    if not condition:
        raise LiveFail(f"[FAIL] {name}: {detail}")
    print(f"[PASS] {name}")


def req(method, path, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(
        method,
        f"{API}{path}",
        headers=headers,
        timeout=TIMEOUT,
        **kwargs,
    )


def login(email, password):
    r = req("POST", "/auth/login", json={"email": email, "password": password})
    check(f"Login {email}", r.status_code == 200, r.text)
    return r.json()["access_token"], r.json()


def main():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise LiveFail("Defina QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD.")
    if not CANDIDATE_EMAIL or not CANDIDATE_PASSWORD:
        raise LiveFail(
            "Defina QA_M4_CANDIDATE_EMAIL y QA_M4_CANDIDATE_PASSWORD con un candidato "
            "activo ya asociado a una solicitud."
        )

    print("Sakura Módulo 4 LIVE QA")
    print(f"API={API}")

    r = req("GET", "/openapi.json")
    check("API/OpenAPI disponible", r.status_code == 200, r.text)

    admin_token, _ = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    candidate_token, candidate_login = login(CANDIDATE_EMAIL, CANDIDATE_PASSWORD)
    check(
        "Login candidato identifica principal_type",
        candidate_login.get("principal_type") == "candidato",
        str(candidate_login),
    )

    # Seguridad básica.
    check("Preguntas sin token -> 401", req("GET", "/preguntas").status_code == 401)
    check(
        "Portal candidato rechaza token admin",
        req("GET", "/cuestionarios/me", admin_token).status_code == 403,
    )

    # Reutilizamos una pregunta válida existente para no depender de IDs de habilidad/nivel.
    r = req("GET", "/preguntas", admin_token, params={"limit": 500})
    check("Banco de preguntas accesible", r.status_code == 200, r.text)
    valid = None
    for item in r.json():
        opts = item.get("opciones") or []
        if len(opts) >= 2 and sum(1 for o in opts if o.get("opcr_es_correcta")) == 1:
            valid = item
            break
    check("Existe pregunta válida para LIVE", valid is not None, "Cree al menos una pregunta con 2 opciones y 1 correcta")

    # Detectar solicitud a partir de variable o de postulaciones del candidato.
    if SOLICITUD_ID:
        solicitud_id = int(SOLICITUD_ID)
    else:
        r = req("GET", "/candidatos/me/solicitudes", candidate_token)
        check("Candidato tiene endpoint de solicitudes", r.status_code == 200, r.text)
        solicitudes = r.json()
        check("Candidato asociado a una solicitud", len(solicitudes) > 0)
        first = solicitudes[0]
        solicitud_id = (
            first.get("solicitud_id")
            or first.get("sol_id")
            or (first.get("solicitud") or {}).get("sol_id")
        )
        check("Solicitud ID detectable", bool(solicitud_id), str(first))
        solicitud_id = int(solicitud_id)

    run = datetime.now().strftime("%H%M%S")
    r = req(
        "POST",
        "/cuestionarios",
        admin_token,
        json={
            "cues_nombre": f"QA LIVE M4 {run}",
            "cues_descripcion": "Cuestionario LIVE automatizado",
            "cues_porcentaje_aprobacion": 50,
            "cues_solicitud_id": solicitud_id,
        },
    )
    check("Cuestionario POST -> 201", r.status_code == 201, r.text)
    questionnaire_id = r.json()["cues_id"]

    r = req(
        "POST",
        f"/cuestionarios/{questionnaire_id}/preguntas/{valid['preg_id']}",
        admin_token,
    )
    check("Agregar pregunta válida", r.status_code == 200, r.text)

    r = req("GET", f"/cuestionarios/{questionnaire_id}", admin_token)
    check(
        "Métricas automáticas",
        r.status_code == 200
        and r.json().get("cantidad_preguntas") == 1
        and r.json().get("puntaje_maximo", 0) > 0
        and r.json().get("duracion_minutos", 0) > 0,
        r.text,
    )

    # Obtener cand_id desde /candidatos/me.
    r = req("GET", "/candidatos/me", candidate_token)
    check("GET /candidatos/me", r.status_code == 200, r.text)
    candidate_id = r.json().get("cand_id")
    check("cand_id disponible", bool(candidate_id), r.text)

    expires = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    r = req(
        "POST",
        f"/cuestionarios/{questionnaire_id}/asignar",
        admin_token,
        json={"candidato_id": candidate_id, "fecha_vencimiento": expires},
    )
    check("Asignar cuestionario -> 201", r.status_code == 201, r.text)
    assignment_id = r.json()["cdcu_id"]
    check("Estado inicial Asignado", r.json().get("estado_nombre") == "Asignado", r.text)

    r = req("GET", "/cuestionarios/me", candidate_token)
    check(
        "Candidato ve su cuestionario",
        r.status_code == 200 and any(x.get("cdcu_id") == assignment_id for x in r.json()),
        r.text,
    )

    check(
        "Preguntas ocultas antes de iniciar",
        req("GET", f"/cuestionarios/me/{assignment_id}/preguntas", candidate_token).status_code == 409,
    )

    r = req("POST", f"/cuestionarios/me/{assignment_id}/iniciar", candidate_token)
    check(
        "Iniciar -> En Progreso",
        r.status_code == 200 and r.json().get("estado") == "En Progreso",
        r.text,
    )

    r = req("GET", f"/cuestionarios/me/{assignment_id}/preguntas", candidate_token)
    check("Preguntas disponibles", r.status_code == 200 and len(r.json()) == 1, r.text)
    check(
        "No expone respuesta correcta",
        "opcr_es_correcta" not in r.text and '"es_correcta"' not in r.text,
        r.text,
    )
    candidate_question = r.json()[0]
    prcu_id = candidate_question["prcu_id"]

    # Seleccionamos una opción cualquiera; LIVE valida persistencia y cálculo, no fuerza aprobar.
    option_id = candidate_question["opciones"][0]["opcr_id"]
    r = req(
        "PUT",
        f"/cuestionarios/me/{assignment_id}/respuesta",
        candidate_token,
        json={
            "pregunta_cuestionario_id": prcu_id,
            "opcion_respuesta_id": option_id,
        },
    )
    check("Guardar respuesta progresiva", r.status_code == 200, r.text)

    r = req("POST", f"/cuestionarios/me/{assignment_id}/finalizar", candidate_token)
    check(
        "Finalizar cuestionario",
        r.status_code == 200 and r.json().get("estado") == "Finalizado",
        r.text,
    )
    check(
        "Resultado calculado por backend",
        r.json().get("puntaje_maximo", 0) > 0
        and r.json().get("porcentaje_obtenido") is not None
        and r.json().get("aprobado") is not None,
        r.text,
    )

    check(
        "No puede habilitar reintento por simple finalización",
        req(
            "POST",
            f"/asignaciones-cuestionario/{assignment_id}/habilitar-reintento",
            admin_token,
        ).status_code == 409,
    )

    r = req("GET", f"/asignaciones-cuestionario/{assignment_id}/resultado", admin_token)
    check(
        "Resultado detallado visible a personal interno",
        r.status_code == 200 and len(r.json().get("respuestas", [])) == 1,
        r.text,
    )

    print("RESULTADO: PASSED")
    print(f"Cuestionario QA conservado: ID={questionnaire_id}")
    print(f"Asignación QA conservada: ID={assignment_id}, estado=Finalizado")
    print("La conservación es intencional para permitir inspección de trazabilidad en PostgreSQL.")


if __name__ == "__main__":
    try:
        main()
    except LiveFail as exc:
        print(str(exc))
        sys.exit(1)
