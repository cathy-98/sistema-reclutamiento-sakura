from __future__ import annotations

import os
import sys
import uuid
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

BASE_URL = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("QA_ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("QA_ADMIN_PASSWORD", "").strip()
SECOND_EMAIL = os.getenv("QA_M5_SECOND_INTERVIEWER_EMAIL", "").strip()
SECOND_PASSWORD = os.getenv("QA_M5_SECOND_INTERVIEWER_PASSWORD", "").strip()
CAND_EMAIL = os.getenv("QA_M5_CANDIDATE_EMAIL", "").strip()
CAND_PASSWORD = os.getenv("QA_M5_CANDIDATE_PASSWORD", "").strip()
POST_ID_RAW = os.getenv("QA_M5_SOLICITUD_CANDIDATO_ID", "").strip()
TIMEOUT = 20
RUN = uuid.uuid4().hex[:8]
PASSED = 0


class QAError(RuntimeError): pass


def call(method: str, path: str, expected: tuple[int, ...], token: str | None = None, **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    if token: headers["Authorization"] = f"Bearer {token}"
    r = requests.request(method, BASE_URL + path, headers=headers, timeout=TIMEOUT, **kwargs)
    if r.status_code not in expected:
        raise QAError(f"{method} {path}: esperado {expected}, recibido {r.status_code}. Body={r.text[:1600]}")
    return r


def ok(label: str):
    global PASSED
    PASSED += 1
    print(f"[PASS {PASSED:02d}] {label}")


def login(email: str, password: str) -> tuple[str, dict[str, Any]]:
    b = call("POST", "/auth/login", (200,), json={"email": email, "password": password}).json()
    token = b.get("access_token")
    if not token: raise QAError(f"Login {email} no retornó access_token")
    me = call("GET", "/auth/me", (200,), token=token).json()
    return token, me


def principal_id(token: str) -> int:
    """
    Obtiene el identificador del principal desde el claim `sub` del JWT.

    El backend Sakura usa `sub` como ID tanto para usuarios internos como
    para candidatos. Esto evita depender de la forma exacta de /auth/me,
    que puede ser distinta entre principal_type=usuario y candidato.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("JWT no tiene tres segmentos")

        payload_segment = parts[1]
        payload_segment += "=" * (-len(payload_segment) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode(payload_segment.encode("ascii")).decode("utf-8")
        )

        subject = payload.get("sub")
        if subject is None:
            raise ValueError("JWT no contiene claim sub")

        return int(subject)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise QAError(f"No fue posible obtener principal_id desde el JWT: {exc}") from exc


def catalog(path: str, idf: str, namef: str, token: str) -> dict[str, int]:
    rows = call("GET", f"/catalogos/{path}", (200,), token=token, params={"limit": 100}).json()
    if not rows: raise QAError(f"Catálogo {path} vacío")
    return {str(x[namef]).strip(): int(x[idf]) for x in rows}


def future(slot: int) -> tuple[str, str]:
    # días distintos para evitar colisiones con QA previa.
    start = datetime.now(timezone.utc) + timedelta(days=20 + slot, minutes=int(RUN[:2], 16) % 45)
    end = start + timedelta(hours=1)
    return start.isoformat(), end.isoformat()


def create_payload(post_id: int, t1: int, t2: int, u1: int, u2: int, slot: int, title: str):
    a,b = future(slot)
    return {
        "solicitud_candidato_id": post_id,
        "fecha_hora_inicio": a,
        "fecha_hora_fin": b,
        "titulo_evento": f"{title} {RUN}",
        "enlace_reunion": f"https://meet.example/{RUN}-{slot}",
        "comentarios_convocatoria": f"QA LIVE M5 {RUN}",
        "tipos": [
            {"tipo_entrevista_id": t1, "usuarios_ids": [u1, u2]},
            {"tipo_entrevista_id": t2, "usuarios_ids": [u1]},
        ],
    }


def run():
    print("Sakura Módulo 5 - QA LIVE COMPLETO")
    print("API=", BASE_URL, " RUN=", RUN)
    required = {
        "QA_ADMIN_EMAIL": ADMIN_EMAIL, "QA_ADMIN_PASSWORD": ADMIN_PASSWORD,
        "QA_M5_SECOND_INTERVIEWER_EMAIL": SECOND_EMAIL,
        "QA_M5_SECOND_INTERVIEWER_PASSWORD": SECOND_PASSWORD,
        "QA_M5_CANDIDATE_EMAIL": CAND_EMAIL,
        "QA_M5_CANDIDATE_PASSWORD": CAND_PASSWORD,
        "QA_M5_SOLICITUD_CANDIDATO_ID": POST_ID_RAW,
    }
    missing = [k for k,v in required.items() if not v]
    if missing: raise QAError("Faltan variables para LIVE completo: " + ", ".join(missing))
    try: post_id = int(POST_ID_RAW)
    except ValueError as exc: raise QAError("QA_M5_SOLICITUD_CANDIDATO_ID debe ser entero") from exc

    openapi = call("GET", "/openapi.json", (200,)).json()
    expected_routes = ["/entrevistas", "/entrevistas/agendar-masivo", "/entrevistas/me", "/candidatos/me/entrevistas"]
    for path in expected_routes:
        if path not in openapi.get("paths", {}): raise QAError(f"OpenAPI no contiene {path}")
    ok("OpenAPI registra M5")

    admin_token, admin_me = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    admin_id = principal_id(admin_token)
    ok("Login admin")

    second_token, second_me = login(SECOND_EMAIL, SECOND_PASSWORD)
    second_id = principal_id(second_token)
    ok("Login segundo entrevistador/reclutador")

    cand_token, cand_me = login(CAND_EMAIL, CAND_PASSWORD)
    cand_id = principal_id(cand_token)
    ok("Login candidato")

    # /auth/me puede variar en su estructura de detalle; solo validamos
    # principal_type cuando el campo está presente.
    if admin_me.get("principal_type") not in (None, "usuario"):
        raise QAError(f"Admin autenticado con principal_type inesperado: {admin_me.get('principal_type')}")
    if second_me.get("principal_type") not in (None, "usuario"):
        raise QAError(f"Segundo entrevistador autenticado con principal_type inesperado: {second_me.get('principal_type')}")
    if cand_me.get("principal_type") not in (None, "candidato"):
        raise QAError(f"Candidato autenticado con principal_type inesperado: {cand_me.get('principal_type')}")

    call("GET", "/entrevistas", (401,)); ok("API interna sin token -> 401")
    call("GET", "/entrevistas", (403,), token=cand_token); ok("Candidato no usa API interna -> 403")
    call("GET", "/candidatos/me/entrevistas", (403,), token=admin_token); ok("Usuario interno no usa agenda candidato -> 403")

    types = catalog("tipos-entrevista", "tpet_id", "tpet_nombre", admin_token)
    results = catalog("nombres-resultado", "nore_id", "nore_nombre", admin_token)
    states = catalog("estados-entrevista", "esev_id", "esev_nombre", admin_token)
    if len(types) < 2: raise QAError("Se requieren al menos dos tipos de entrevista")
    if not results: raise QAError("Se requiere al menos un resultado")
    t1,t2 = list(types.values())[:2]
    result_ids = list(results.values())
    r1 = result_ids[0]; r2 = result_ids[1] if len(result_ids)>1 else r1
    ok("Catálogos M5 disponibles")

    # Creación multi tipo/multi entrevistador.
    p = create_payload(post_id,t1,t2,admin_id,second_id,1,"QA CREATE")
    created = call("POST","/entrevistas",(201,),token=admin_token,json=p).json(); iid=int(created["entrevista_id"])
    if created["estado_nombre"] != "Pendiente": raise QAError("Nueva entrevista no quedó Pendiente")
    if int(created["usuario_creador_id"]) != admin_id: raise QAError("Creador no corresponde al JWT")
    if len(created["tipos"]) != 2: raise QAError("No se persistieron los dos tipos")
    ok("Creación: múltiples tipos, entrevistadores y creador JWT")

    call("POST","/entrevistas",(409,),token=admin_token,json=p); ok("Duplicado agenda -> 409")
    bad=dict(p); bad["titulo_evento"]="   "; call("POST","/entrevistas",(422,),token=admin_token,json=bad); ok("Título vacío -> 422")
    past=dict(p); s=datetime.now(timezone.utc)-timedelta(hours=2); past["fecha_hora_inicio"]=s.isoformat();past["fecha_hora_fin"]=(s+timedelta(hours=1)).isoformat();call("POST","/entrevistas",(422,),token=admin_token,json=past);ok("Fecha pasada -> 422")

    detail=call("GET",f"/entrevistas/{iid}",(200,),token=admin_token).json();
    if detail["entrevista_id"] != iid: raise QAError("GET detalle inconsistente")
    ok("Detalle entrevista")
    listing=call("GET","/entrevistas",(200,),token=admin_token,params={"solicitud_candidato_id":post_id,"usuario_id":second_id,"tipo_id":t1,"estado_id":states["Pendiente"]}).json()
    if not any(int(x["entrevista_id"])==iid for x in listing): raise QAError("Filtros no encontraron entrevista")
    ok("Listado/filtros solicitud-candidato, usuario, tipo, estado")

    patch=call("PATCH",f"/entrevistas/{iid}",(200,),token=admin_token,json={"titulo_evento":f"QA PATCH {RUN}"}).json()
    if patch["titulo_evento"] != f"QA PATCH {RUN}": raise QAError("PATCH no actualizó título")
    ok("PATCH convocatoria")

    # Participantes se pueden reemplazar antes de evaluar.
    repl={"tipos":[{"tipo_entrevista_id":t1,"usuarios_ids":[admin_id,second_id]},{"tipo_entrevista_id":t2,"usuarios_ids":[admin_id]}]}
    call("PUT",f"/entrevistas/{iid}/participantes",(200,),token=admin_token,json=repl); ok("Reemplazo participantes/tipos")

    mine=call("GET","/entrevistas/me",(200,),token=second_token).json()
    if not any(int(x["entrevista_id"])==iid for x in mine): raise QAError("Entrevista no aparece para segundo entrevistador")
    item=next(x for x in mine if int(x["entrevista_id"])==iid)
    if any(int(x["tipo_entrevista_id"])==t2 for x in item["tipos_asignados"]): raise QAError("/entrevistas/me filtró mal tipos asignados")
    ok("Agenda del entrevistador y tipos propios")

    # Candidato ve agenda, no evaluaciones.
    agenda=call("GET","/candidatos/me/entrevistas",(200,),token=cand_token).json()
    own=[x for x in agenda if int(x["entrevista_id"])==iid]
    if not own: raise QAError("La entrevista creada no aparece al candidato; confirme que POST_ID pertenece a QA_M5_CANDIDATE_EMAIL")
    if "evaluaciones" in own[0] or "resultado" in str(own[0]).lower(): raise QAError("Agenda candidato filtra información de evaluación incorrectamente")
    call("GET",f"/candidatos/me/entrevistas/{iid}",(200,),token=cand_token); ok("Agenda candidato sin resultados")

    # Estados confirmada / reprogramada.
    conf=call("POST",f"/entrevistas/{iid}/confirmar",(200,),token=admin_token).json()
    if conf["estado_nombre"]!="Confirmada": raise QAError("No quedó Confirmada")
    call("POST",f"/entrevistas/{iid}/confirmar",(409,),token=admin_token); ok("Confirmación + transición inválida")
    ns,ne=future(7)
    rep=call("POST",f"/entrevistas/{iid}/reprogramar",(200,),token=admin_token,json={"fecha_hora_inicio":ns,"fecha_hora_fin":ne,"motivo":"QA reprograma"}).json()
    if rep["estado_nombre"]!="Reprogramada" or rep["motivo_estado"]!="QA reprograma": raise QAError("Reprogramación inconsistente")
    ok("Reprogramación")

    # Contrato HTTP M5 relevante:
    # 404 -> recurso/tipo/evaluación propia inexistente.
    # 403 -> falta permiso RBAC.
    # 409 -> conflicto de negocio: estado inválido, duplicado o usuario no asignado al tipo.
    # Realizada y evaluaciones múltiples.
    realized=call("POST",f"/entrevistas/{iid}/realizar",(200,),token=admin_token).json()
    if realized["estado_nombre"]!="Realizada": raise QAError("No quedó Realizada")
    ok("Realizar entrevista")
    ev1=call("POST",f"/entrevistas/{iid}/tipos/{t1}/evaluar",(201,),token=admin_token,json={"nombre_resultado_id":r1,"observacion":"QA admin"}).json()
    ev2=call("POST",f"/entrevistas/{iid}/tipos/{t1}/evaluar",(201,),token=second_token,json={"nombre_resultado_id":r2,"observacion":"QA segundo"}).json()
    if ev1["usuario_id"]==ev2["usuario_id"]: raise QAError("Autoría de evaluaciones incorrecta")
    ok("Dos entrevistadores evalúan el mismo tipo")
    call("POST",f"/entrevistas/{iid}/tipos/{t1}/evaluar",(409,),token=admin_token,json={"nombre_resultado_id":r1}); ok("Evaluación duplicada usuario+tipo -> 409")
    ev_other=call("POST",f"/entrevistas/{iid}/tipos/{t2}/evaluar",(201,),token=admin_token,json={"nombre_resultado_id":r1,"observacion":"QA segundo tipo"}).json(); ok("Mismo usuario evalúa otro tipo")
    edited=call("PATCH",f"/entrevistas/{iid}/tipos/{t1}/evaluacion",(200,),token=admin_token,json={"observacion":"QA editada"}).json()
    if edited["observacion"]!="QA editada": raise QAError("PATCH evaluación no persistió")
    call(
        "PATCH",
        f"/entrevistas/{iid}/tipos/{t2}/evaluacion",
        (409,),
        token=second_token,
        json={"observacion": "No propia"},
    )
    ok("No asignado al tipo no puede editar evaluación ajena -> 409")
    evals=call("GET",f"/entrevistas/{iid}/evaluaciones",(200,),token=second_token).json()
    if len(evals)<3: raise QAError(f"Se esperaban >=3 evaluaciones; recibidas {len(evals)}")
    ok("Listado de evaluaciones")
    call("PUT",f"/entrevistas/{iid}/participantes",(409,),token=admin_token,json=repl); ok("Participantes inmutables tras evaluaciones/terminal")
    call("PATCH",f"/entrevistas/{iid}",(409,),token=admin_token,json={"titulo_evento":"No permitido"}); ok("Entrevista realizada no editable")

    # El candidato sigue sin ver evaluación después de existir.
    agenda_after=call("GET","/candidatos/me/entrevistas",(200,),token=cand_token).json()
    own_after=next(x for x in agenda_after if int(x["entrevista_id"])==iid)
    raw=str(own_after).lower()
    if "qa editada" in raw or "aprobado" in raw or "evaluacion" in raw: raise QAError("Se filtró resultado/observación al candidato")
    ok("Privacidad de evaluaciones para candidato")

    # Cancelada y No Asistió en citas nuevas.
    c2=call("POST","/entrevistas",(201,),token=admin_token,json=create_payload(post_id,t1,t2,admin_id,second_id,9,"QA CANCEL")).json();i2=int(c2["entrevista_id"])
    cancelled=call("POST",f"/entrevistas/{i2}/cancelar",(200,),token=admin_token,json={"motivo":"QA cancel"}).json()
    if cancelled["estado_nombre"]!="Cancelada": raise QAError("Cancelación inconsistente")
    call("POST",f"/entrevistas/{i2}/confirmar",(409,),token=admin_token); ok("Cancelada es terminal")
    c3=call("POST","/entrevistas",(201,),token=admin_token,json=create_payload(post_id,t1,t2,admin_id,second_id,10,"QA NOSHOW")).json();i3=int(c3["entrevista_id"])
    noshow=call("POST",f"/entrevistas/{i3}/no-asistio",(200,),token=admin_token,json={"motivo":"QA ausencia"}).json()
    if noshow["estado_nombre"]!="No Asistio": raise QAError("No Asistio inconsistente")
    ok("No Asistió")

    # Masivo: usa el mismo post solo no permite duplicado en array; necesitamos dos post IDs para éxito real.
    second_post_raw=os.getenv("QA_M5_SEGUNDA_SOLICITUD_CANDIDATO_ID","").strip()
    if not second_post_raw:
        raise QAError("Para cubrir agendamiento masivo sin SKIP defina QA_M5_SEGUNDA_SOLICITUD_CANDIDATO_ID con otra postulación en 'En entrevista' de solicitud 'En Entrevistas'.")
    second_post=int(second_post_raw)
    ms,me=future(12)
    mass={"solicitudes_candidatos_ids":[post_id,second_post],"fecha_hora_inicio":ms,"fecha_hora_fin":me,"titulo_evento":f"QA MASS {RUN}","enlace_reunion":None,"comentarios_convocatoria":"QA mass","tipos":[{"tipo_entrevista_id":t1,"usuarios_ids":[admin_id,second_id]}]}
    massr=call("POST","/entrevistas/agendar-masivo",(201,),token=admin_token,json=mass).json()
    if massr["total_solicitados"]!=2 or massr["total_creados"]!=2: raise QAError("Masivo no creó 2")
    ok("Agendamiento masivo atómico exitoso")
    call("POST","/entrevistas/agendar-masivo",(409,),token=admin_token,json=mass); ok("Masivo con conflicto -> rollback/409")

    print("\nRESULTADO: PASSED")
    print(f"PASSED: {PASSED}")
    print("FAILED: 0")
    print("SKIPPED: 0")
    print(f"Entrevistas QA conservadas para trazabilidad. Principal ID={iid}, RUN={RUN}, candidato_id={cand_id}")


if __name__ == "__main__":
    try: run()
    except (QAError, requests.RequestException) as exc:
        print("\nRESULTADO: FAILED")
        print(exc)
        sys.exit(1)