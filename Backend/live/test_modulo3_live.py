from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Any

import requests

BASE_URL = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("QA_ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("QA_ADMIN_PASSWORD", "").strip()
RECRUITER_ID_ENV = os.getenv("QA_RECRUITER_USER_ID", "").strip()
RUN = uuid.uuid4().hex[:8]
TIMEOUT = 20


class LiveQAError(RuntimeError):
    pass


@dataclass
class Context:
    token: str
    recruiter_id: int
    cargo_id: int
    prioridad_id: int
    modalidad_id: int
    contrato_id: int
    habilidad_id: int
    nivel_id: int | None
    disponibilidad_id: int | None
    cliente_id: int
    solicitud_estados: dict[str, int]
    candidato_estados: dict[str, int]
    motivo_rechazo_id: int | None


def req(method: str, path: str, *, expected: tuple[int, ...], token: str | None = None, **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
    if r.status_code not in expected:
        raise LiveQAError(f"{method} {path}: esperado {expected}, recibido {r.status_code}. Body={r.text[:1800]}")
    return r


def passed(label: str):
    print(f"[PASS] {label}")


def catalog(resource: str, token: str, limit=100) -> list[dict[str, Any]]:
    return req("GET", f"/catalogos/{resource}", expected=(200,), token=token, params={"limit": limit}).json()


def first_catalog(resource: str, field: str, token: str) -> dict[str, Any]:
    rows = catalog(resource, token, 20)
    if not rows:
        raise LiveQAError(f"Catálogo {resource} está vacío")
    if field not in rows[0]:
        raise LiveQAError(f"Catálogo {resource}: falta campo {field}")
    return rows[0]


def named_map(resource: str, id_field: str, name_field: str, token: str) -> dict[str, int]:
    return {str(x.get(name_field, "")).strip(): int(x[id_field]) for x in catalog(resource, token, 100)}


def find_recruiter(token: str) -> int:
    if RECRUITER_ID_ENV:
        try:
            return int(RECRUITER_ID_ENV)
        except ValueError as exc:
            raise LiveQAError("QA_RECRUITER_USER_ID debe ser entero") from exc
    users = req("GET", "/usuarios/", expected=(200,), token=token, params={"limit": 500}).json()
    for user in users:
        role = user.get("rol") or {}
        state = user.get("estado") or {}
        if str(role.get("rol_nombre", "")).casefold() == "reclutador" and str(state.get("esusr_nombre", "")).casefold() == "activo":
            return int(user["usr_id"])
    raise LiveQAError("No existe Reclutador Activo. Defina QA_RECRUITER_USER_ID.")


def find_client(token: str) -> int:
    rows = req("GET", "/clientes", expected=(200,), token=token, params={"limit": 1}).json()
    if not rows:
        raise LiveQAError("Se requiere al menos un cliente para crear la solicitud LIVE")
    return int(rows[0]["cli_id"])


def build_context(token: str) -> Context:
    cargo = first_catalog("cargos", "crgo_id", token)
    prioridad = first_catalog("prioridades-solicitud", "prsol_id", token)
    modalidad = first_catalog("modalidades", "mdld_id", token)
    contrato = first_catalog("tipos-contrato", "tpct_id", token)
    habilidad = first_catalog("habilidades", "hab_id", token)
    niveles = catalog("niveles-habilidad", token, 20)
    disponibilidades = catalog("disponibilidades", token, 20)
    motivos = catalog("motivos-rechazo", token, 20)
    sol_states = named_map("estados-solicitud", "essl_id", "essl_nombre", token)
    cand_states = named_map("estados-solicitud-candidato", "essc_id", "essc_nombre", token)

    required_sol = {"Pendiente", "En Publicacion", "En Entrevistas", "Cancelado", "Cerrado", "Pausado"}
    required_cand = {"En revision", "En entrevista", "Inhabilitado", "Seleccionado", "Descartado", "Contratado"}
    if missing := required_sol - set(sol_states):
        raise LiveQAError(f"Faltan estados solicitud: {sorted(missing)}")
    if missing := required_cand - set(cand_states):
        raise LiveQAError(f"Faltan estados candidato: {sorted(missing)}")

    return Context(
        token=token,
        recruiter_id=find_recruiter(token),
        cargo_id=int(cargo["crgo_id"]),
        prioridad_id=int(prioridad["prsol_id"]),
        modalidad_id=int(modalidad["mdld_id"]),
        contrato_id=int(contrato["tpct_id"]),
        habilidad_id=int(habilidad["hab_id"]),
        nivel_id=int(niveles[0]["nvhb_id"]) if niveles else None,
        disponibilidad_id=int(disponibilidades[0]["disp_id"]) if disponibilidades else None,
        cliente_id=find_client(token),
        solicitud_estados=sol_states,
        candidato_estados=cand_states,
        motivo_rechazo_id=int(motivos[0]["mtrc_id"]) if motivos else None,
    )


def candidate_payload(ctx: Context, email: str) -> dict[str, Any]:
    p: dict[str, Any] = {
        "cand_email": email,
        "cand_nombres": "QA",
        "cand_apellido_paterno": "ModuloTres",
        "cand_telefono": "912345678",
        "cand_resumen_profesional": f"Candidato generado por QA LIVE {RUN}",
        "cand_url_1": ["https://linkedin.com/in/qa-sakura", "https://github.com/qa-sakura", "https://github.com/qa-sakura"],
        "cand_cv_urls": [f"qa/{RUN}/cv1.pdf", f"qa/{RUN}/cv2.pdf", f"qa/{RUN}/cv1.pdf"],
        "cand_titulo": "QA Backend",
    }
    if ctx.disponibilidad_id:
        p["cand_disponibilidad_id"] = ctx.disponibilidad_id
    return p


def solicitud_payload(ctx: Context) -> dict[str, Any]:
    skill: dict[str, Any] = {
        "solhb_habilidad_id": ctx.habilidad_id,
        "solhb_anios_experiencia_req": 1,
        "solhb_es_excluyente": True,
    }
    if ctx.nivel_id:
        skill["solhb_nivel_habilidad_id"] = ctx.nivel_id
    return {
        "sol_titulo": f"QA M3 cierre parcial {RUN}",
        "sol_descripcion": "Solicitud creada por QA LIVE Módulo 3",
        "sol_observacion": f"RUN {RUN}",
        "sol_cantidad_vacantes": 2,
        "sol_salario_min": 1000,
        "sol_salario_max": 2000,
        "sol_cargo_id": ctx.cargo_id,
        "sol_prioridad_id": ctx.prioridad_id,
        "sol_cliente_id": ctx.cliente_id,
        "sol_usuario_asignado_id": ctx.recruiter_id,
        "sol_modalidad_id": ctx.modalidad_id,
        "sol_tipo_contrato_id": ctx.contrato_id,
        "habilidades": [skill],
    }


def run():
    print("Sakura Módulo 3 LIVE QA")
    print(f"API={BASE_URL}")
    print(f"RUN={RUN}")
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise LiveQAError("Defina QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD")

    req("GET", "/openapi.json", expected=(200,)); passed("API/OpenAPI disponible")
    login = req("POST", "/auth/login", expected=(200,), json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).json()
    token = login.get("access_token")
    if not token:
        raise LiveQAError("Login administrador no entregó access_token")
    passed("Login administrador")

    req("GET", "/candidatos", expected=(401,)); passed("Candidatos sin JWT -> 401")
    ctx = build_context(token); passed("Catálogos, cliente y reclutador disponibles")

    # Crear candidato manual con password automática.
    email = f"qa-m3-{RUN}@sakura.cl"
    created = req("POST", "/candidatos", expected=(201,), token=token, json=candidate_payload(ctx, email)).json()
    candidate = created["candidato"]
    cand_id = int(candidate["cand_id"])
    temp_password = created.get("password_temporal")
    if not temp_password:
        raise LiveQAError("Creación automática no retornó password_temporal")
    if "cand_password" in candidate:
        raise LiveQAError("La API expuso cand_password")
    if candidate.get("cand_url_1", "").count("github.com/qa-sakura") != 1:
        raise LiveQAError("No se deduplicaron URLs profesionales")
    if candidate.get("cand_cv_urls", "").count(f"qa/{RUN}/cv1.pdf") != 1:
        raise LiveQAError("No se deduplicaron URLs de CV")
    passed("Candidato POST + password temporal + URLs normalizadas")

    # Duplicado e identidad cruzada.
    req("POST", "/candidatos", expected=(409,), token=token, json=candidate_payload(ctx, email)); passed("Email candidato duplicado -> 409")
    req("POST", "/candidatos", expected=(409,), token=token, json=candidate_payload(ctx, ADMIN_EMAIL)); passed("Email usuario interno no puede crearse como candidato -> 409")

    # Login candidato en el mismo endpoint.
    cand_login = req("POST", "/auth/login", expected=(200,), json={"email": email, "password": temp_password}).json()
    if cand_login.get("principal_type") != "candidato":
        raise LiveQAError(f"principal_type inesperado: {cand_login.get('principal_type')}")
    cand_token = cand_login["access_token"]
    passed("Login candidato por /auth/login")

    me = req("GET", "/auth/me", expected=(200,), token=cand_token).json()
    if me.get("principal_type") != "candidato":
        raise LiveQAError("/auth/me no identificó candidato")
    req("GET", "/candidatos/me", expected=(200,), token=cand_token)
    req("GET", "/candidatos", expected=(403,), token=cand_token)
    passed("Identidad candidato /auth/me + /candidatos/me + aislamiento recursos internos")

    # Cambio password candidato.
    new_password = f"M3Nueva{RUN}!"
    req("POST", "/auth/change-password", expected=(204,), token=cand_token, json={"password_actual": temp_password, "password_nueva": new_password})
    req("POST", "/auth/login", expected=(401,), json={"email": email, "password": temp_password})
    cand_login2 = req("POST", "/auth/login", expected=(200,), json={"email": email, "password": new_password}).json()
    cand_token = cand_login2["access_token"]
    passed("Cambio password candidato invalida password anterior")

    # CRUD básico y habilidad para cumplir requisito excluyente.
    req("GET", f"/candidatos/{cand_id}", expected=(200,), token=token)
    req("PATCH", f"/candidatos/{cand_id}", expected=(200,), token=token, json={"cand_titulo": f"QA PATCH {RUN}"})
    filtered = req("GET", "/candidatos", expected=(200,), token=token, params={"q": email, "limit": 100}).json()
    if not any(int(x["cand_id"]) == cand_id for x in filtered):
        raise LiveQAError("Candidato no apareció en búsqueda")
    passed("Candidato GET/PATCH/búsqueda")

    skill_payload: dict[str, Any] = {"cdhb_habilidad_id": ctx.habilidad_id, "cdhb_anios_experiencia": 5}
    if ctx.nivel_id:
        skill_payload["cdhb_nivel_habilidad_id"] = ctx.nivel_id
    skill = req("POST", f"/candidatos/{cand_id}/habilidades", expected=(201,), token=token, json=skill_payload).json()
    req("POST", f"/candidatos/{cand_id}/habilidades", expected=(409,), token=token, json=skill_payload)
    req("PATCH", f"/candidatos/{cand_id}/habilidades/{skill['cdhb_id']}", expected=(200,), token=token, json={"cdhb_anios_experiencia": 6})
    passed("Habilidad candidato CRUD/duplicado")

    # Importación TXT sin correo real ni Gmail.
    cv_email = f"cv-m3-{RUN}@sakura.cl"
    text = f"QA Candidato\n{cv_email}\n+56 9 1234 5678\nPython 4 anos\nBackend QA\nProfesional con experiencia suficiente para validar la importacion automatizada de CV del modulo tres Sakura.\n"
    imported = req("POST", "/candidatos/importar-cv", expected=(200,), token=token, files={"file": (f"cv-{RUN}.txt", text.encode("utf-8"), "text/plain")}).json()
    if not imported.get("creado") or not imported.get("password_temporal"):
        raise LiveQAError("Importación CV no creó candidato/password temporal")
    imported_id = int(imported["candidato"]["cand_id"])
    imported_pwd = imported["password_temporal"]
    passed("Importación CV TXT crea perfil")

    imported2 = req("POST", "/candidatos/importar-cv", expected=(200,), token=token, files={"file": (f"cv2-{RUN}.txt", text.encode("utf-8"), "text/plain")}).json()
    if imported2.get("creado") or not imported2.get("actualizado") or imported2.get("password_temporal") is not None:
        raise LiveQAError("Segundo CV no reutilizó candidato correctamente")
    req("POST", "/auth/login", expected=(200,), json={"email": cv_email, "password": imported_pwd})
    passed("Reimportación reutiliza candidato y conserva password")

    req("POST", "/candidatos/importar-cv", expected=(422,), token=token, files={"file": ("sin-correo.txt", b"Persona Sin Correo", "text/plain")})
    req("POST", "/candidatos/importar-cv", expected=(422,), token=token, files={"file": ("cv.csv", b"a,b", "text/csv")})
    passed("Importación inválida -> 422")

    # Crear solicitud con 2 vacantes, llevar a En Entrevistas.
    sol = req("POST", "/solicitudes", expected=(201,), token=token, json=solicitud_payload(ctx)).json()
    sol_id = int(sol["sol_id"])
    req("PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token, json={"sol_estado_solicitud_id": ctx.solicitud_estados["En Publicacion"]})
    req("PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token, json={"sol_estado_solicitud_id": ctx.solicitud_estados["En Entrevistas"]})
    passed(f"Solicitud M3 creada y llevada a En Entrevistas -> {sol.get('sol_codigo')}")

    # Cerrar con 0 contratados está bloqueado.
    req("PATCH", f"/solicitudes/{sol_id}/estado", expected=(409,), token=token, json={"sol_estado_solicitud_id": ctx.solicitud_estados["Cerrado"]})
    passed("Cierre con 0 contratados -> 409")

    # Asociación candidato y evaluación de excluyentes.
    app_resp = req("POST", f"/solicitudes/{sol_id}/candidatos/{cand_id}", expected=(201,), token=token, json={"slcd_pretension_renta": 1500000, "slcd_observaciones": f"RUN {RUN}"}).json()
    app = app_resp["postulacion"]
    app_id = int(app["slcd_id"])
    if int(app["slcd_estado_solicitud_candidato_id"]) != ctx.candidato_estados["En revision"]:
        raise LiveQAError("Postulación no inició En revision")
    if app_resp["evaluacion"].get("cumple_excluyentes") is not True:
        raise LiveQAError(f"Candidato debía cumplir excluyentes: {app_resp['evaluacion']}")
    passed("Asociación + estado inicial + evaluación excluyentes")

    req("POST", f"/solicitudes/{sol_id}/candidatos/{cand_id}", expected=(409,), token=token, json={})
    req("GET", f"/solicitudes/{sol_id}/candidatos", expected=(200,), token=token)
    req("GET", f"/candidatos/{cand_id}/solicitudes", expected=(200,), token=token)
    req("PATCH", f"/postulaciones/{app_id}", expected=(200,), token=token, json={"slcd_puntaje_compatibilidad": 95, "slcd_observaciones": "QA PATCH"})
    passed("Postulación duplicada/listados/PATCH")

    # Flujo postulación.
    req("PATCH", f"/postulaciones/{app_id}/estado", expected=(409,), token=token, json={"estado_id": ctx.candidato_estados["Seleccionado"]})
    passed("Transición directa En revision -> Seleccionado bloqueada")
    for name in ["En entrevista", "Seleccionado", "Contratado"]:
        req("PATCH", f"/postulaciones/{app_id}/estado", expected=(200,), token=token, json={"estado_id": ctx.candidato_estados[name]})
    req("PATCH", f"/postulaciones/{app_id}/estado", expected=(409,), token=token, json={"estado_id": ctx.candidato_estados["En entrevista"]})
    passed("Flujo En revision -> En entrevista -> Seleccionado -> Contratado + terminal")

    # Una de dos vacantes cubierta: debe cerrar y advertir.
    closed = req("PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token, json={"sol_estado_solicitud_id": ctx.solicitud_estados["Cerrado"]})
    warning = closed.headers.get("X-Sakura-Warning", "")
    if "1 de 2" not in warning:
        raise LiveQAError(f"Se esperaba warning 1 de 2, recibido: {warning!r}")
    passed("Cierre parcial permitido con X-Sakura-Warning")

    # Baja lógica del importado no relacionado con la solicitud.
    req("DELETE", f"/candidatos/{imported_id}", expected=(204,), token=token)
    req("POST", "/auth/login", expected=(403,), json={"email": cv_email, "password": imported_pwd})
    passed("Baja lógica candidato importado bloquea login")

    print("RESULTADO: PASSED")
    print(f"Solicitud QA conservada Cerrada: ID={sol_id}, código={sol.get('sol_codigo')}, RUN={RUN}")
    print(f"Candidato contratado QA conservado: ID={cand_id}, email={email}")
    print("La permanencia de estos registros es intencional para trazabilidad LIVE.")


if __name__ == "__main__":
    try:
        run()
    except LiveQAError as exc:
        print(f"[FAIL] {exc}", flush=True)
        raise SystemExit(1)
