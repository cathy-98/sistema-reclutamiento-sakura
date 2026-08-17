from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass
from typing import Any

import requests


BASE_URL = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("QA_ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("QA_ADMIN_PASSWORD", "").strip()
RECRUITER_ID_ENV = os.getenv("QA_RECRUITER_USER_ID", "").strip()
RUN = uuid.uuid4().hex[:8]
TIMEOUT = 15


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
    habilidad2_id: int | None
    nivel_id: int | None
    estado_ids: dict[str, int]
    cliente_id: int


def request(method: str, path: str, *, expected: tuple[int, ...], token: str | None = None, **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.request(
        method,
        f"{BASE_URL}{path}",
        headers=headers,
        timeout=TIMEOUT,
        **kwargs,
    )
    if response.status_code not in expected:
        body = response.text[:1500]
        raise LiveQAError(
            f"{method} {path}: esperado {expected}, recibido {response.status_code}. Body={body}"
        )
    return response


def pass_msg(label: str):
    print(f"[PASS] {label}")


def first_catalog(resource: str, id_field: str, token: str) -> dict[str, Any]:
    response = request(
        "GET",
        f"/catalogos/{resource}",
        expected=(200,),
        token=token,
        params={"skip": 0, "limit": 10},
    )
    rows = response.json()
    if not rows:
        raise LiveQAError(f"El catálogo {resource} está vacío; se requiere al menos un registro")
    if id_field not in rows[0]:
        raise LiveQAError(f"Catálogo {resource}: no se encontró campo {id_field}")
    return rows[0]


def state_catalog(token: str) -> dict[str, int]:
    response = request(
        "GET",
        "/catalogos/estados-solicitud",
        expected=(200,),
        token=token,
        params={"limit": 100},
    )
    result = {str(x.get("essl_nombre", "")).strip(): int(x["essl_id"]) for x in response.json()}
    required = {"Pendiente", "En Curso", "En Entrevistas", "Cancelado", "Cerrado", "Pausado"}
    missing = required - set(result)
    if missing:
        raise LiveQAError(f"Faltan estados de solicitud requeridos: {sorted(missing)}")
    return result


def find_recruiter(token: str) -> int:
    if RECRUITER_ID_ENV:
        try:
            return int(RECRUITER_ID_ENV)
        except ValueError as exc:
            raise LiveQAError("QA_RECRUITER_USER_ID debe ser entero") from exc

    response = request(
        "GET",
        "/usuarios/",
        expected=(200,),
        token=token,
        params={"limit": 500},
    )
    for user in response.json():
        role = user.get("rol") or {}
        state = user.get("estado") or {}
        if (
            str(role.get("rol_nombre", "")).casefold() == "reclutador"
            and str(state.get("esusr_nombre", "")).casefold() == "activo"
        ):
            return int(user["usr_id"])

    raise LiveQAError(
        "No se encontró un usuario Activo con rol Reclutador. "
        "Defina $env:QA_RECRUITER_USER_ID con el ID de un reclutador activo."
    )


def find_or_create_client(token: str) -> tuple[int, bool, int | None]:
    response = request(
        "GET",
        "/clientes",
        expected=(200,),
        token=token,
        params={"limit": 1},
    )
    rows = response.json()
    if rows:
        return int(rows[0]["cli_id"]), False, None

    company = request(
        "POST",
        "/clientes/empresas",
        expected=(201,),
        token=token,
        json={"emp_nombre": f"QA Live Empresa {RUN}", "emp_identificacion": f"QAL-{RUN}"},
    ).json()
    company_id = int(company["emp_id"])
    client = request(
        "POST",
        "/clientes",
        expected=(201,),
        token=token,
        json={
            "cli_nombre": f"QA Live Cliente {RUN}",
            "cli_empresa_id": company_id,
            "cli_email": f"cliente-{RUN}@qa.sakura.cl",
            "cli_telefono1": "912345678",
        },
    ).json()
    return int(client["cli_id"]), True, company_id


def build_context(token: str) -> Context:
    cargo = first_catalog("cargos", "crgo_id", token)
    prioridad = first_catalog("prioridades-solicitud", "prsol_id", token)
    modalidad = first_catalog("modalidades", "mdld_id", token)
    contrato = first_catalog("tipos-contrato", "tpct_id", token)
    habilidades = request(
        "GET", "/catalogos/habilidades", expected=(200,), token=token, params={"limit": 10}
    ).json()
    if not habilidades:
        raise LiveQAError("El catálogo habilidades está vacío")
    nivel_rows = request(
        "GET", "/catalogos/niveles-habilidad", expected=(200,), token=token, params={"limit": 10}
    ).json()

    cliente_id, created, company_id = find_or_create_client(token)
    if created:
        print(
            f"[INFO] No había clientes existentes. Se creó cliente QA {cliente_id} "
            f"y empresa QA {company_id}; si se crea una solicitud quedarán como trazabilidad QA."
        )

    return Context(
        token=token,
        recruiter_id=find_recruiter(token),
        cargo_id=int(cargo["crgo_id"]),
        prioridad_id=int(prioridad["prsol_id"]),
        modalidad_id=int(modalidad["mdld_id"]),
        contrato_id=int(contrato["tpct_id"]),
        habilidad_id=int(habilidades[0]["hab_id"]),
        habilidad2_id=int(habilidades[1]["hab_id"]) if len(habilidades) > 1 else None,
        nivel_id=int(nivel_rows[0]["nvhb_id"]) if nivel_rows else None,
        estado_ids=state_catalog(token),
        cliente_id=cliente_id,
    )


def solicitud_payload(ctx: Context, title: str) -> dict[str, Any]:
    skill: dict[str, Any] = {
        "solhb_habilidad_id": ctx.habilidad_id,
        "solhb_anios_experiencia_req": 1,
        "solhb_es_excluyente": True,
    }
    if ctx.nivel_id:
        skill["solhb_nivel_habilidad_id"] = ctx.nivel_id

    return {
        "sol_titulo": title,
        "sol_descripcion": "Solicitud generada por QA LIVE Módulo 2",
        "sol_observacion": f"QA LIVE RUN {RUN}",
        "sol_cantidad_vacantes": 1,
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
    print("Sakura Módulo 2 LIVE QA")
    print(f"API={BASE_URL}")
    print(f"RUN={RUN}")

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise LiveQAError(
            "Debe definir QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD antes de ejecutar el runner LIVE"
        )

    request("GET", "/openapi.json", expected=(200,))
    pass_msg("API/OpenAPI disponible")

    login = request(
        "POST",
        "/auth/login",
        expected=(200,),
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    ).json()
    token = login.get("access_token")
    if not token:
        raise LiveQAError("Login no retornó access_token")
    pass_msg("Login administrador")

    request("GET", "/solicitudes", expected=(401,))
    pass_msg("Solicitudes sin token -> 401")

    request("GET", "/clientes", expected=(401,))
    pass_msg("Clientes sin token -> 401")

    ctx = build_context(token)
    pass_msg("Catálogos, cliente y reclutador disponibles")

    # CRUD empresa/cliente descartable.
    company = request(
        "POST",
        "/clientes/empresas",
        expected=(201,),
        token=token,
        json={"emp_nombre": f"QA Empresa {RUN}", "emp_identificacion": f"QA-{RUN}"},
    ).json()
    company_id = int(company["emp_id"])
    pass_msg("Empresa POST -> 201")

    request("GET", f"/clientes/empresas/{company_id}", expected=(200,), token=token)
    request(
        "PATCH",
        f"/clientes/empresas/{company_id}",
        expected=(200,),
        token=token,
        json={"emp_nombre": f"QA Empresa PATCH {RUN}"},
    )
    pass_msg("Empresa GET/PATCH")

    qa_client = request(
        "POST",
        "/clientes",
        expected=(201,),
        token=token,
        json={
            "cli_nombre": f"QA Cliente {RUN}",
            "cli_empresa_id": company_id,
            "cli_email": f"qa-{RUN}@qa.sakura.cl",
            "cli_telefono1": "923456789",
        },
    ).json()
    qa_client_id = int(qa_client["cli_id"])
    pass_msg("Cliente POST -> 201")

    request("GET", f"/clientes/{qa_client_id}", expected=(200,), token=token)
    request(
        "PATCH", f"/clientes/{qa_client_id}", expected=(200,), token=token,
        json={"cli_nombre": f"QA Cliente PATCH {RUN}"},
    )
    filtered = request(
        "GET", "/clientes", expected=(200,), token=token,
        params={"empresa_id": company_id, "q": RUN, "limit": 100},
    ).json()
    if not any(int(x["cli_id"]) == qa_client_id for x in filtered):
        raise LiveQAError("Cliente QA no apareció en filtro/búsqueda")
    pass_msg("Cliente GET/PATCH/filtros")

    # La empresa no se elimina mientras tiene cliente.
    request("DELETE", f"/clientes/empresas/{company_id}", expected=(409,), token=token)
    pass_msg("Empresa en uso -> 409")
    request("DELETE", f"/clientes/{qa_client_id}", expected=(204,), token=token)
    request("DELETE", f"/clientes/empresas/{company_id}", expected=(204,), token=token)
    pass_msg("Cleanup empresa/cliente descartable")

    # Solicitud real QA.
    bad = solicitud_payload(ctx, f"QA Sin Excluyente {RUN}")
    bad["habilidades"][0]["solhb_es_excluyente"] = False
    request("POST", "/solicitudes", expected=(422,), token=token, json=bad)
    pass_msg("Solicitud sin habilidad excluyente -> 422")

    created = request(
        "POST",
        "/solicitudes",
        expected=(201,),
        token=token,
        json=solicitud_payload(ctx, f"QA LIVE {RUN}"),
    ).json()
    sol_id = int(created["sol_id"])
    code = str(created.get("sol_codigo", ""))
    if not code.startswith("SOL-") or len(code) != 10:
        raise LiveQAError(f"Código de solicitud inesperado: {code!r}")
    if int(created["sol_estado_solicitud_id"]) != ctx.estado_ids["Pendiente"]:
        raise LiveQAError("La nueva solicitud no quedó en estado Pendiente")
    if not created.get("sol_usuario_creador_id"):
        raise LiveQAError("La solicitud no registró sol_usuario_creador_id desde el JWT")
    pass_msg(f"Solicitud creada -> {code} y creador registrado")

    request("GET", f"/solicitudes/{sol_id}", expected=(200,), token=token)
    listing = request(
        "GET", "/solicitudes", expected=(200,), token=token,
        params={"q": RUN, "cliente_id": ctx.cliente_id, "limit": 100},
    ).json()
    if not any(int(x["sol_id"]) == sol_id for x in listing):
        raise LiveQAError("Solicitud QA no apareció en listado con filtros")
    pass_msg("Solicitud GET/listado/filtros")

    request(
        "PATCH", f"/solicitudes/{sol_id}", expected=(200,), token=token,
        json={"sol_titulo": f"QA LIVE PATCH {RUN}"},
    )
    pass_msg("Solicitud PATCH")

    skills = request(
        "GET", f"/solicitudes/{sol_id}/habilidades", expected=(200,), token=token
    ).json()
    if not skills:
        raise LiveQAError("La solicitud no retornó habilidades")
    request(
        "DELETE",
        f"/solicitudes/{sol_id}/habilidades/{ctx.habilidad_id}",
        expected=(409,),
        token=token,
    )
    pass_msg("Protección última habilidad excluyente -> 409")

    evaluation = request(
        "POST", f"/solicitudes/{sol_id}/evaluar-candidato", expected=(200,), token=token,
        json=[{"habilidad_id": ctx.habilidad_id, "anios_experiencia": 2}],
    ).json()
    if evaluation.get("cumple_excluyentes") is not True:
        raise LiveQAError(f"Evaluación excluyentes inesperada: {evaluation}")
    if evaluation.get("descartado_automaticamente") is not False:
        raise LiveQAError(f"La evaluación positiva no debe descartar automáticamente: {evaluation}")
    pass_msg("Evaluación excluyentes: cumple y no descarta automáticamente")

    insufficient = request(
        "POST", f"/solicitudes/{sol_id}/evaluar-candidato", expected=(200,), token=token,
        json=[{"habilidad_id": ctx.habilidad_id, "anios_experiencia": 0}],
    ).json()
    if insufficient.get("cumple_excluyentes") is not False:
        raise LiveQAError(f"Se esperaba incumplimiento por experiencia: {insufficient}")
    if insufficient.get("descartado_automaticamente") is not False:
        raise LiveQAError(
            "Regla vigente M2/M3 violada: incumplir excluyentes no debe descartar automáticamente"
        )
    if not insufficient.get("habilidades_faltantes"):
        raise LiveQAError(f"Faltó detalle de habilidad/experiencia insuficiente: {insufficient}")
    pass_msg("Evaluación excluyentes: experiencia insuficiente sin descarte automático")

    missing = request(
        "POST", f"/solicitudes/{sol_id}/evaluar-candidato", expected=(200,), token=token,
        json=[],
    ).json()
    if missing.get("cumple_excluyentes") is not False:
        raise LiveQAError(f"Se esperaba incumplimiento por habilidad faltante: {missing}")
    if missing.get("descartado_automaticamente") is not False:
        raise LiveQAError("Habilidad faltante no debe descartar automáticamente")
    if not missing.get("habilidades_faltantes"):
        raise LiveQAError(f"No se informó habilidad obligatoria faltante: {missing}")
    pass_msg("Evaluación excluyentes: habilidad faltante sin descarte automático")

    # Estados: Pendiente -> En Curso -> Pausado -> En Curso -> Cancelado.
    request(
        "PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token,
        json={"sol_estado_solicitud_id": ctx.estado_ids["En Curso"]},
    )
    pass_msg("Pendiente -> En Curso")

    request(
        "PATCH", f"/solicitudes/{sol_id}/estado", expected=(422,), token=token,
        json={"sol_estado_solicitud_id": ctx.estado_ids["Pausado"]},
    )
    pass_msg("Pausado sin observación -> 422")

    request(
        "PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token,
        json={"sol_estado_solicitud_id": ctx.estado_ids["Pausado"], "observacion": f"Pausa QA {RUN}"},
    )
    request(
        "PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token,
        json={"sol_estado_solicitud_id": ctx.estado_ids["En Curso"]},
    )
    pass_msg("En Curso -> Pausado -> En Curso")

    history = request(
        "GET", f"/solicitudes/{sol_id}/historial", expected=(200,), token=token
    ).json()
    if len(history) < 4:
        raise LiveQAError(f"Historial incompleto para solicitud {sol_id}: {len(history)} filas")
    pass_msg("Historial/auditoría")

    request(
        "PATCH", f"/solicitudes/{sol_id}/estado", expected=(200,), token=token,
        json={
            "sol_estado_solicitud_id": ctx.estado_ids["Cancelado"],
            "observacion": f"Cierre QA LIVE {RUN}",
        },
    )
    request(
        "PATCH", f"/solicitudes/{sol_id}/estado", expected=(409,), token=token,
        json={"sol_estado_solicitud_id": ctx.estado_ids["En Curso"]},
    )
    pass_msg("Cancelado terminal -> no permite reapertura")

    request("DELETE", f"/solicitudes/{sol_id}", expected=(405,), token=token)
    pass_msg("Sin DELETE físico de solicitudes -> 405")

    print("\nRESULTADO: PASSED")
    print(f"Solicitud QA conservada como Cancelada: ID={sol_id}, código={code}, RUN={RUN}")
    print("La permanencia del registro es intencional: M2 preserva trazabilidad y no expone DELETE físico.")


if __name__ == "__main__":
    try:
        run()
    except (LiveQAError, requests.RequestException) as exc:
        print("\nRESULTADO: FAILED")
        print(exc)
        sys.exit(1)
