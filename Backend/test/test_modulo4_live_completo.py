from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

import requests


API = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")

ADMIN_EMAIL = os.getenv("QA_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("QA_ADMIN_PASSWORD")

CANDIDATE_EMAIL = os.getenv("QA_M4_CANDIDATE_EMAIL")
CANDIDATE_PASSWORD = os.getenv("QA_M4_CANDIDATE_PASSWORD")

# Solicitud real que tenga al menos un candidato. Para pruebas masivas completas,
# idealmente debe tener 2 o más candidatos.
SOLICITUD_ID = os.getenv("QA_M4_SOLICITUD_ID")

# Opcional: candidato que NO pertenezca a QA_M4_SOLICITUD_ID.
OUTSIDER_CANDIDATE_ID = os.getenv("QA_M4_OUTSIDER_CANDIDATE_ID")

TIMEOUT = int(os.getenv("QA_HTTP_TIMEOUT", "25"))

PASSED = 0
FAILED = 0
SKIPPED = 0


class LiveFail(RuntimeError):
    pass


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"[PASS] {name}")
        return
    FAILED += 1
    raise LiveFail(f"[FAIL] {name}: {detail}")


def skip(name: str, detail: str = "") -> None:
    global SKIPPED
    SKIPPED += 1
    suffix = f" - {detail}" if detail else ""
    print(f"[SKIP] {name}{suffix}")


def req(method: str, path: str, token: str | None = None, **kwargs) -> requests.Response:
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


def login(email: str, password: str) -> tuple[str, dict[str, Any]]:
    r = req("POST", "/auth/login", json={"email": email, "password": password})
    check(f"Login {email}", r.status_code == 200, r.text)
    body = r.json()
    token = body.get("access_token")
    check(f"Token recibido {email}", bool(token), str(body))
    return token, body


def future(days: int = 2) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def past(minutes: int = 1) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()


def get_valid_question(admin_token: str) -> dict[str, Any]:
    r = req("GET", "/preguntas", admin_token, params={"limit": 500})
    check("GET /preguntas", r.status_code == 200, r.text)

    for item in r.json():
        options = item.get("opciones") or []
        correct = [o for o in options if o.get("opcr_es_correcta") is True]
        if (
            len(options) >= 2
            and len(correct) == 1
            and int(item.get("puntaje_base") or 0) > 0
            and int(item.get("duracion_minutos") or 0) > 0
        ):
            return item

    raise LiveFail(
        "[FAIL] No existe en el banco una pregunta LIVE válida "
        "(>=2 opciones, exactamente 1 correcta, puntaje > 0 y duración > 0)."
    )


def create_questionnaire(
    admin_token: str,
    solicitud_id: int,
    valid_question: dict[str, Any],
    suffix: str,
    approval: int = 50,
) -> int:
    r = req(
        "POST",
        "/cuestionarios",
        admin_token,
        json={
            "cues_nombre": f"QA LIVE M4 {suffix}",
            "cues_descripcion": f"QA automatizado {suffix}",
            "cues_porcentaje_aprobacion": approval,
            "cues_solicitud_id": solicitud_id,
        },
    )
    check(f"Crear cuestionario {suffix}", r.status_code == 201, r.text)
    qid = int(r.json()["cues_id"])

    r = req(
        "POST",
        f"/cuestionarios/{qid}/preguntas/{valid_question['preg_id']}",
        admin_token,
    )
    check(f"Agregar pregunta a {suffix}", r.status_code == 200, r.text)

    r = req("GET", f"/cuestionarios/{qid}", admin_token)
    check(
        f"Métricas cuestionario {suffix}",
        r.status_code == 200
        and r.json().get("cantidad_preguntas") == 1
        and int(r.json().get("puntaje_maximo") or 0) > 0
        and int(r.json().get("duracion_minutos") or 0) > 0,
        r.text,
    )
    return qid


def get_candidate_me(candidate_token: str) -> dict[str, Any]:
    r = req("GET", "/candidatos/me", candidate_token)
    check("GET /candidatos/me", r.status_code == 200, r.text)
    body = r.json()

    # M3 actualmente devuelve:
    # {
    #   "principal_type": "candidato",
    #   "candidato": { "cand_id": ..., ... }
    # }
    # Se mantiene compatibilidad con una respuesta plana si existiera.
    candidate = body.get("candidato") if isinstance(body.get("candidato"), dict) else body

    check(
        "cand_id disponible",
        bool(candidate.get("cand_id")),
        str(body),
    )
    return candidate


def get_available_candidates(admin_token: str, questionnaire_id: int) -> list[dict[str, Any]]:
    r = req(
        "GET",
        f"/cuestionarios/{questionnaire_id}/candidatos-disponibles",
        admin_token,
    )
    check(
        f"GET candidatos-disponibles cuestionario {questionnaire_id}",
        r.status_code == 200,
        r.text,
    )
    return r.json()


def test_individual_flow(
    admin_token: str,
    candidate_token: str,
    candidate_id: int,
    solicitud_id: int,
    valid_question: dict[str, Any],
    run_id: str,
):
    print("\n=== FLUJO INDIVIDUAL + PORTAL CANDIDATO ===")

    qid = create_questionnaire(
        admin_token,
        solicitud_id,
        valid_question,
        f"IND-{run_id}",
        approval=50,
    )

    # Antes de asignar, el candidato debe aparecer como disponible si pertenece a la solicitud.
    candidates = get_available_candidates(admin_token, qid)
    by_id = {int(c["cand_id"]): c for c in candidates}
    check(
        "Candidato QA pertenece a la solicitud del cuestionario",
        candidate_id in by_id,
        f"cand_id={candidate_id}, disponibles={sorted(by_id)}",
    )
    check(
        "Candidato QA inicialmente no asignado",
        by_id[candidate_id]["cuestionario_asignado"] is False,
        str(by_id[candidate_id]),
    )

    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar",
        admin_token,
        json={
            "candidato_id": candidate_id,
            "fecha_vencimiento": future(),
        },
    )
    check("Asignación individual -> 201", r.status_code == 201, r.text)
    assignment_id = int(r.json()["cdcu_id"])
    check(
        "Asignación individual queda Asignado",
        r.json().get("estado_nombre") == "Asignado",
        r.text,
    )

    candidates = get_available_candidates(admin_token, qid)
    by_id = {int(c["cand_id"]): c for c in candidates}
    check(
        "candidatos-disponibles marca asignación existente",
        by_id[candidate_id]["cuestionario_asignado"] is True
        and int(by_id[candidate_id]["asignacion_id"]) == assignment_id,
        str(by_id[candidate_id]),
    )

    r = req("GET", "/cuestionarios/me", candidate_token)
    check(
        "Candidato ve asignación en /cuestionarios/me",
        r.status_code == 200
        and any(int(x["cdcu_id"]) == assignment_id for x in r.json()),
        r.text,
    )

    r = req(
        "GET",
        f"/cuestionarios/me/{assignment_id}/preguntas",
        candidate_token,
    )
    check("Preguntas ocultas antes de iniciar", r.status_code == 409, r.text)

    r = req(
        "POST",
        f"/cuestionarios/me/{assignment_id}/iniciar",
        candidate_token,
    )
    check(
        "Inicio -> En Progreso",
        r.status_code == 200
        and r.json().get("estado") == "En Progreso"
        and r.json().get("fecha_inicio") is not None,
        r.text,
    )

    r = req(
        "GET",
        f"/cuestionarios/me/{assignment_id}/preguntas",
        candidate_token,
    )
    check(
        "Preguntas visibles después de iniciar",
        r.status_code == 200 and len(r.json()) == 1,
        r.text,
    )
    check(
        "API candidato no expone opcr_es_correcta",
        "opcr_es_correcta" not in r.text and '"es_correcta"' not in r.text,
        r.text,
    )

    question = r.json()[0]
    prcu_id = int(question["prcu_id"])
    option_id = int(question["opciones"][0]["opcr_id"])

    r = req(
        "PUT",
        f"/cuestionarios/me/{assignment_id}/respuesta",
        candidate_token,
        json={
            "pregunta_cuestionario_id": prcu_id,
            "opcion_respuesta_id": option_id,
        },
    )
    check("Guardado progresivo de respuesta", r.status_code == 200, r.text)
    response_id = int(r.json()["rspr_id"])

    # Upsert: volver a enviar la misma respuesta mantiene la misma fila.
    r = req(
        "PUT",
        f"/cuestionarios/me/{assignment_id}/respuesta",
        candidate_token,
        json={
            "pregunta_cuestionario_id": prcu_id,
            "opcion_respuesta_id": option_id,
        },
    )
    check(
        "Upsert mantiene una sola respuesta",
        r.status_code == 200 and int(r.json()["rspr_id"]) == response_id,
        r.text,
    )

    r = req(
        "POST",
        f"/cuestionarios/me/{assignment_id}/finalizar",
        candidate_token,
    )
    check(
        "Finalizar -> Finalizado",
        r.status_code == 200 and r.json().get("estado") == "Finalizado",
        r.text,
    )
    check(
        "Backend calcula resultado",
        r.json().get("puntaje_maximo") is not None
        and r.json().get("puntaje_obtenido") is not None
        and r.json().get("porcentaje_obtenido") is not None
        and r.json().get("aprobado") is not None,
        r.text,
    )

    r = req(
        "GET",
        f"/asignaciones-cuestionario/{assignment_id}/resultado",
        admin_token,
    )
    check(
        "Resultado interno disponible",
        r.status_code == 200 and len(r.json().get("respuestas", [])) == 1,
        r.text,
    )

    # Reprobado o aprobado normalmente: jamás puede habilitar reintento directamente.
    r = req(
        "POST",
        f"/asignaciones-cuestionario/{assignment_id}/habilitar-reintento",
        admin_token,
        json={"fecha_vencimiento": future(days=3)},
    )
    check(
        "Finalizado no permite reintento sin Error Tecnico",
        r.status_code == 409,
        r.text,
    )

    return {
        "questionnaire_id": qid,
        "assignment_id": assignment_id,
    }


def test_mass_flow(
    admin_token: str,
    solicitud_id: int,
    valid_question: dict[str, Any],
    run_id: str,
):
    print("\n=== ASIGNACIÓN MASIVA SELECCIONADA ===")

    qid = create_questionnaire(
        admin_token,
        solicitud_id,
        valid_question,
        f"MASS-{run_id}",
    )
    available = get_available_candidates(admin_token, qid)
    candidate_ids = [int(x["cand_id"]) for x in available]

    check(
        "Solicitud tiene candidatos para prueba masiva",
        len(candidate_ids) >= 1,
        str(candidate_ids),
    )

    # Schema: lista vacía.
    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar-masivo",
        admin_token,
        json={"candidato_ids": [], "fecha_vencimiento": future()},
    )
    check("Masivo rechaza lista vacía -> 422", r.status_code == 422, r.text)

    # Schema: duplicados.
    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar-masivo",
        admin_token,
        json={
            "candidato_ids": [candidate_ids[0], candidate_ids[0]],
            "fecha_vencimiento": future(),
        },
    )
    check("Masivo rechaza IDs duplicados -> 422", r.status_code == 422, r.text)

    # Fecha vencida.
    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar-masivo",
        admin_token,
        json={
            "candidato_ids": [candidate_ids[0]],
            "fecha_vencimiento": past(),
        },
    )
    check("Masivo rechaza vencimiento pasado -> 422", r.status_code == 422, r.text)

    selected = candidate_ids[:2] if len(candidate_ids) >= 2 else candidate_ids[:1]
    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar-masivo",
        admin_token,
        json={
            "candidato_ids": selected,
            "fecha_vencimiento": future(),
        },
    )
    check("Asignación masiva válida -> 201", r.status_code == 201, r.text)
    body = r.json()
    check(
        "Masivo reporta total asignado correcto",
        int(body["total_asignados"]) == len(selected)
        and int(body["total_solicitados"]) == len(selected),
        str(body),
    )

    # Repetir con uno ya asignado debe fallar de forma atómica.
    if len(candidate_ids) >= 2:
        already = selected[0]
        other = candidate_ids[1] if candidate_ids[1] != already else None
        if other is not None:
            r = req(
                "POST",
                f"/cuestionarios/{qid}/asignar-masivo",
                admin_token,
                json={
                    "candidato_ids": [already, other],
                    "fecha_vencimiento": future(days=3),
                },
            )
            check(
                "Masivo con candidato ya asignado -> 409 atómico",
                r.status_code == 409,
                r.text,
            )
    else:
        skip(
            "Atomicidad por candidato ya asignado con segundo candidato",
            "la solicitud tiene solo 1 candidato",
        )

    # Outsider opcional.
    if OUTSIDER_CANDIDATE_ID:
        outsider = int(OUTSIDER_CANDIDATE_ID)
        r = req(
            "POST",
            f"/cuestionarios/{qid}/asignar-masivo",
            admin_token,
            json={
                "candidato_ids": [candidate_ids[0], outsider],
                "fecha_vencimiento": future(days=4),
            },
        )
        check(
            "Masivo rechaza candidato ajeno a solicitud -> 409",
            r.status_code == 409,
            r.text,
        )
    else:
        skip(
            "Candidato ajeno a la solicitud",
            "defina QA_M4_OUTSIDER_CANDIDATE_ID para habilitar este caso LIVE",
        )

    return {"questionnaire_id": qid, "available_count": len(candidate_ids)}


def test_assign_all_flow(
    admin_token: str,
    solicitud_id: int,
    valid_question: dict[str, Any],
    run_id: str,
):
    print("\n=== ASIGNAR TODOS ===")

    qid = create_questionnaire(
        admin_token,
        solicitud_id,
        valid_question,
        f"ALL-{run_id}",
    )
    available = get_available_candidates(admin_token, qid)
    ids = [int(x["cand_id"]) for x in available]

    check("Solicitud tiene al menos un candidato", len(ids) >= 1, str(ids))

    # Asignamos uno individualmente para validar que asignar-todos lo omita.
    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar",
        admin_token,
        json={
            "candidato_id": ids[0],
            "fecha_vencimiento": future(),
        },
    )
    check("Preasignación individual para asignar-todos", r.status_code == 201, r.text)

    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar-todos",
        admin_token,
        json={"fecha_vencimiento": future(days=3)},
    )
    check("asignar-todos -> 201", r.status_code == 201, r.text)
    body = r.json()

    check(
        "asignar-todos reporta universo de solicitud",
        int(body["total_candidatos_solicitud"]) == len(ids),
        str(body),
    )
    check(
        "asignar-todos omite preasignado",
        int(body["total_omitidos_ya_asignados"]) >= 1,
        str(body),
    )
    check(
        "asignar-todos crea exactamente pendientes",
        int(body["total_asignados"]) == max(0, len(ids) - 1),
        str(body),
    )

    # Segunda ejecución: no debe duplicar nada.
    r2 = req(
        "POST",
        f"/cuestionarios/{qid}/asignar-todos",
        admin_token,
        json={"fecha_vencimiento": future(days=4)},
    )
    check("asignar-todos repetido -> 201", r2.status_code == 201, r2.text)
    body2 = r2.json()
    check(
        "asignar-todos repetido no duplica",
        int(body2["total_asignados"]) == 0
        and int(body2["total_omitidos_ya_asignados"]) == len(ids),
        str(body2),
    )

    # Fecha pasada.
    qid2 = create_questionnaire(
        admin_token,
        solicitud_id,
        valid_question,
        f"ALL-PAST-{run_id}",
    )
    r = req(
        "POST",
        f"/cuestionarios/{qid2}/asignar-todos",
        admin_token,
        json={"fecha_vencimiento": past()},
    )
    check("asignar-todos rechaza vencimiento pasado -> 422", r.status_code == 422, r.text)

    return {"questionnaire_id": qid}


def test_technical_error_retry(
    admin_token: str,
    candidate_token: str,
    candidate_id: int,
    solicitud_id: int,
    valid_question: dict[str, Any],
    run_id: str,
):
    print("\n=== ERROR TÉCNICO + REINTENTO ===")

    qid = create_questionnaire(
        admin_token,
        solicitud_id,
        valid_question,
        f"TECH-{run_id}",
    )
    r = req(
        "POST",
        f"/cuestionarios/{qid}/asignar",
        admin_token,
        json={
            "candidato_id": candidate_id,
            "fecha_vencimiento": future(),
        },
    )
    check("Asignación para error técnico", r.status_code == 201, r.text)
    aid = int(r.json()["cdcu_id"])

    r = req(
        "POST",
        f"/cuestionarios/me/{aid}/iniciar",
        candidate_token,
    )
    check("Iniciar evaluación técnica", r.status_code == 200, r.text)

    r = req(
        "GET",
        f"/cuestionarios/me/{aid}/preguntas",
        candidate_token,
    )
    check("Obtener pregunta para intento técnico", r.status_code == 200, r.text)
    question = r.json()[0]

    r = req(
        "PUT",
        f"/cuestionarios/me/{aid}/respuesta",
        candidate_token,
        json={
            "pregunta_cuestionario_id": int(question["prcu_id"]),
            "opcion_respuesta_id": int(question["opciones"][0]["opcr_id"]),
        },
    )
    check("Guardar respuesta antes del error técnico", r.status_code == 200, r.text)

    r = req(
        "POST",
        f"/asignaciones-cuestionario/{aid}/error-tecnico",
        admin_token,
    )
    check(
        "Marcar Error Tecnico",
        r.status_code == 200
        and r.json().get("estado_nombre") == "Error Tecnico",
        r.text,
    )

    r = req(
        "POST",
        f"/asignaciones-cuestionario/{aid}/habilitar-reintento",
        admin_token,
        json={"fecha_vencimiento": future(days=5)},
    )
    check(
        "Habilitar reintento desde Error Tecnico",
        r.status_code == 200
        and r.json().get("estado_nombre") == "Asignado"
        and r.json().get("cdcu_fecha_inicio") is None
        and r.json().get("cdcu_fecha_resolucion") is None
        and r.json().get("cdcu_porcentaje_obtenido") is None
        and r.json().get("cdcu_aprobado") is None,
        r.text,
    )

    r = req(
        "POST",
        f"/cuestionarios/me/{aid}/iniciar",
        candidate_token,
    )
    check(
        "Candidato puede iniciar nuevamente después de Error Tecnico",
        r.status_code == 200 and r.json().get("estado") == "En Progreso",
        r.text,
    )

    return {"questionnaire_id": qid, "assignment_id": aid}


def main() -> None:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise LiveFail(
            "Defina QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD."
        )
    if not CANDIDATE_EMAIL or not CANDIDATE_PASSWORD:
        raise LiveFail(
            "Defina QA_M4_CANDIDATE_EMAIL y QA_M4_CANDIDATE_PASSWORD."
        )
    if not SOLICITUD_ID:
        raise LiveFail(
            "Defina QA_M4_SOLICITUD_ID con una solicitud real que tenga al menos "
            "el candidato de QA asociado. Idealmente use una solicitud con 2 o más candidatos."
        )

    solicitud_id = int(SOLICITUD_ID)

    print("=" * 78)
    print("SAKURA - QA LIVE COMPLETO MODULO 4")
    print("=" * 78)
    print(f"API: {API}")
    print(f"Solicitud QA: {solicitud_id}")
    print()

    r = req("GET", "/openapi.json")
    check("API /openapi.json disponible", r.status_code == 200, r.text)

    admin_token, admin_login = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    candidate_token, candidate_login = login(CANDIDATE_EMAIL, CANDIDATE_PASSWORD)

    check(
        "Login candidato usa principal_type=candidato",
        candidate_login.get("principal_type") == "candidato",
        str(candidate_login),
    )

    # Seguridad básica.
    check(
        "Endpoint interno sin token -> 401",
        req("GET", "/preguntas").status_code == 401,
    )
    check(
        "Portal candidato rechaza token interno -> 403",
        req("GET", "/cuestionarios/me", admin_token).status_code == 403,
    )

    candidate = get_candidate_me(candidate_token)
    candidate_id = int(candidate["cand_id"])

    valid_question = get_valid_question(admin_token)
    print(
        f"Pregunta reutilizada para QA: preg_id={valid_question['preg_id']}, "
        f"puntaje={valid_question['puntaje_base']}, "
        f"duracion={valid_question['duracion_minutos']} min"
    )

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    artifacts = []
    artifacts.append(
        test_individual_flow(
            admin_token,
            candidate_token,
            candidate_id,
            solicitud_id,
            valid_question,
            run_id,
        )
    )
    artifacts.append(
        test_mass_flow(
            admin_token,
            solicitud_id,
            valid_question,
            run_id,
        )
    )
    artifacts.append(
        test_assign_all_flow(
            admin_token,
            solicitud_id,
            valid_question,
            run_id,
        )
    )
    artifacts.append(
        test_technical_error_retry(
            admin_token,
            candidate_token,
            candidate_id,
            solicitud_id,
            valid_question,
            run_id,
        )
    )

    print("\n" + "=" * 78)
    print("RESUMEN QA LIVE M4")
    print("=" * 78)
    print(f"PASSED : {PASSED}")
    print(f"FAILED : {FAILED}")
    print(f"SKIPPED: {SKIPPED}")

    if FAILED:
        print("RESULTADO: FAILED")
        sys.exit(1)

    print("RESULTADO: PASSED")
    print()
    print("Registros QA conservados intencionalmente en PostgreSQL:")
    for item in artifacts:
        print(" -", item)
    print(
        "Puede eliminarlos posteriormente si lo desea; mantenerlos permite revisar "
        "trazabilidad, respuestas y estados directamente en PostgreSQL."
    )


if __name__ == "__main__":
    try:
        main()
    except LiveFail as exc:
        print(str(exc))
        print(f"\nPASSED={PASSED} FAILED={FAILED} SKIPPED={SKIPPED}")
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"[FAIL] Error HTTP/conectividad: {exc}")
        print(f"\nPASSED={PASSED} FAILED={FAILED + 1} SKIPPED={SKIPPED}")
        sys.exit(1)