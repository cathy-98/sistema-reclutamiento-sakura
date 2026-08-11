from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass, field
from typing import Any

import requests


BASE_URL = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("QA_ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("QA_ADMIN_PASSWORD", "").strip()
TIMEOUT = float(os.getenv("QA_HTTP_TIMEOUT", "15"))
TOKEN = uuid.uuid4().hex[:6]


class TestFailure(RuntimeError):
    pass


@dataclass
class QAContext:
    admin_token: str = ""
    admin_id: int | None = None
    admin_role_id: int | None = None
    active_state_id: int | None = None
    deleted_state_id: int | None = None
    permission_ids: dict[str, int] = field(default_factory=dict)
    created_roles: list[int] = field(default_factory=list)
    created_permissions: list[int] = field(default_factory=list)
    created_areas: list[int] = field(default_factory=list)
    created_states: list[int] = field(default_factory=list)
    created_users: list[int] = field(default_factory=list)


CTX = QAContext()


def call(
    method: str,
    path: str,
    *,
    expected: tuple[int, ...],
    token: str | None = None,
    **kwargs: Any,
) -> requests.Response:
    headers = dict(kwargs.pop("headers", {}) or {})
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
        raise TestFailure(
            f"{method} {path}: esperado {expected}, recibido "
            f"{response.status_code}. Body={response.text}"
        )
    return response


def check(name: str, fn) -> None:
    try:
        fn()
        print(f"[PASS] {name}")
    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")
        raise


def login(email: str, password: str, *, expected: tuple[int, ...] = (200,)) -> requests.Response:
    return call(
        "POST",
        "/auth/login",
        expected=expected,
        json={"email": email, "password": password},
    )


def require_admin_credentials() -> None:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print(
            "ERROR: define QA_ADMIN_EMAIL y QA_ADMIN_PASSWORD antes de ejecutar.\n"
            "PowerShell ejemplo:\n"
            '$env:QA_ADMIN_EMAIL="admin@dominio.cl"\n'
            '$env:QA_ADMIN_PASSWORD="TuPassword"\n'
            'python live/test_modulo1_live.py'
        )
        sys.exit(2)


def bootstrap() -> None:
    # API disponible
    call("GET", "/openapi.json", expected=(200,))

    # Login admin
    response = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    CTX.admin_token = response.json()["access_token"]

    me = call("GET", "/auth/me", expected=(200,), token=CTX.admin_token).json()
    CTX.admin_id = me["usr_id"]
    CTX.admin_role_id = me.get("usr_rol_id")

    # Estados existentes
    estados = call("GET", "/usuarios/estados", expected=(200,), token=CTX.admin_token).json()
    for estado in estados:
        nombre = (estado.get("esusr_nombre") or "").casefold()
        if nombre == "activo".casefold():
            CTX.active_state_id = estado["esusr_id"]
        if nombre == "eliminado".casefold():
            CTX.deleted_state_id = estado["esusr_id"]

    if CTX.active_state_id is None:
        raise TestFailure("No existe estado 'Activo'.")
    if CTX.deleted_state_id is None:
        raise TestFailure("No existe estado 'Eliminado'.")

    # Permisos existentes
    permisos = call("GET", "/usuarios/permisos", expected=(200,), token=CTX.admin_token).json()
    CTX.permission_ids = {p["per_nombre"]: p["per_id"] for p in permisos}
    required = {"USR_CREATE", "USR_VIEW", "USR_UPDATE", "USR_DELETE"}
    missing = sorted(required - set(CTX.permission_ids))
    if missing:
        raise TestFailure(f"Faltan permisos semilla requeridos: {missing}")


def create_role(name: str, description: str = "QA Automation") -> int:
    response = call(
        "POST",
        "/usuarios/roles",
        expected=(201,),
        token=CTX.admin_token,
        json={"rol_nombre": name, "rol_descripcion": description},
    )
    role_id = response.json()["rol_id"]
    CTX.created_roles.append(role_id)
    return role_id


def create_area(name: str) -> int:
    response = call(
        "POST",
        "/usuarios/areas",
        expected=(201,),
        token=CTX.admin_token,
        json={"area_nombre": name, "area_descripcion": "QA Automation"},
    )
    area_id = response.json()["area_id"]
    CTX.created_areas.append(area_id)
    return area_id


def create_state(name: str) -> int:
    response = call(
        "POST",
        "/usuarios/estados",
        expected=(201,),
        token=CTX.admin_token,
        json={"esusr_nombre": name, "esusr_descripcion": "QA Automation"},
    )
    state_id = response.json()["esusr_id"]
    CTX.created_states.append(state_id)
    return state_id


def create_permission(name: str) -> int:
    response = call(
        "POST",
        "/usuarios/permisos",
        expected=(201,),
        token=CTX.admin_token,
        json={"per_nombre": name, "per_descripcion": "QA Automation"},
    )
    permission_id = response.json()["per_id"]
    CTX.created_permissions.append(permission_id)
    return permission_id


def user_payload(
    *,
    email: str,
    password: str,
    role_id: int | None,
    state_id: int,
    area_id: int | None,
    rut: str,
) -> dict[str, Any]:
    return {
        "usr_nombres": "QATest",
        "usr_apellido_paterno": "Auto",
        "usr_apellido_materno": None,
        "usr_rut_sin_dv": rut,
        "usr_dv": "K",
        "usr_telefono": "911111111",
        "usr_email": email,
        "usr_rol_id": role_id,
        "usr_estado_usuario_id": state_id,
        "usr_area_id": area_id,
        "usr_contrasena": password,
    }


def create_user(payload: dict[str, Any]) -> int:
    response = call(
        "POST",
        "/usuarios/",
        expected=(201,),
        token=CTX.admin_token,
        json=payload,
    )
    user_id = response.json()["usr_id"]
    CTX.created_users.append(user_id)
    return user_id


def run_tests() -> None:
    check("API/OpenAPI disponible", lambda: call("GET", "/openapi.json", expected=(200,)))

    check(
        "Login incorrecto -> 401",
        lambda: login(ADMIN_EMAIL, "PasswordIncorrectaQA!", expected=(401,)),
    )
    check(
        "Usuario inexistente -> 401",
        lambda: login(f"none-{TOKEN}@qa.cl", "Password123!", expected=(401,)),
    )
    check(
        "Sin token /auth/me -> 401",
        lambda: call("GET", "/auth/me", expected=(401,)),
    )
    check(
        "Token inválido /auth/me -> 401",
        lambda: call("GET", "/auth/me", expected=(401,), token="token.invalido.qa"),
    )
    check(
        "Token admin válido /auth/me -> 200",
        lambda: call("GET", "/auth/me", expected=(200,), token=CTX.admin_token),
    )

    # Recursos QA base
    area_id = create_area(f"QA-{TOKEN}")
    inactive_state_id = create_state(f"QAI{TOKEN}")
    viewer_role_id = create_role(f"QAV{TOKEN}")
    no_perm_role_id = create_role(f"QAN{TOKEN}")

    # Asignar USR_VIEW al rol viewer
    view_id = CTX.permission_ids["USR_VIEW"]
    check(
        "Asignar permiso USR_VIEW a rol",
        lambda: call(
            "PUT",
            f"/usuarios/roles/{viewer_role_id}/permisos",
            expected=(200,),
            token=CTX.admin_token,
            json={"permiso_ids": [view_id]},
        ),
    )

    # Usuario viewer
    viewer_email = f"qav{TOKEN}@qa.cl"
    viewer_password = "ViewerQA123!"
    viewer_id = create_user(
        user_payload(
            email=viewer_email,
            password=viewer_password,
            role_id=viewer_role_id,
            state_id=CTX.active_state_id,
            area_id=area_id,
            rut=f"61{TOKEN[:4]}01",
        )
    )
    viewer_token = login(viewer_email, viewer_password).json()["access_token"]

    check(
        "USR_VIEW puede listar usuarios",
        lambda: call("GET", "/usuarios/", expected=(200,), token=viewer_token),
    )
    check(
        "No administrador no puede crear roles -> 403",
        lambda: call(
            "POST",
            "/usuarios/roles",
            expected=(403,),
            token=viewer_token,
            json={"rol_nombre": f"X{TOKEN}", "rol_descripcion": "No crear"},
        ),
    )

    # Usuario sin permisos
    noperm_email = f"qan{TOKEN}@qa.cl"
    noperm_password = "NoPermQA123!"
    noperm_id = create_user(
        user_payload(
            email=noperm_email,
            password=noperm_password,
            role_id=no_perm_role_id,
            state_id=CTX.active_state_id,
            area_id=area_id,
            rut=f"62{TOKEN[:4]}02",
        )
    )
    noperm_token = login(noperm_email, noperm_password).json()["access_token"]
    check(
        "Usuario sin USR_VIEW -> 403",
        lambda: call("GET", "/usuarios/", expected=(403,), token=noperm_token),
    )

    # Usuario inactivo
    inactive_email = f"qai{TOKEN}@qa.cl"
    inactive_password = "InactiveQA123!"
    inactive_id = create_user(
        user_payload(
            email=inactive_email,
            password=inactive_password,
            role_id=viewer_role_id,
            state_id=inactive_state_id,
            area_id=area_id,
            rut=f"63{TOKEN[:4]}03",
        )
    )
    check(
        "Usuario no Activo -> login 403",
        lambda: login(inactive_email, inactive_password, expected=(403,)),
    )

    # CRUD usuario completo
    target_email = f"qat{TOKEN}@qa.cl"
    target_password = "TargetQA123!"
    target_id = create_user(
        user_payload(
            email=target_email,
            password=target_password,
            role_id=viewer_role_id,
            state_id=CTX.active_state_id,
            area_id=area_id,
            rut=f"64{TOKEN[:4]}04",
        )
    )
    check(
        "GET usuario por ID",
        lambda: call("GET", f"/usuarios/{target_id}", expected=(200,), token=CTX.admin_token),
    )
    check(
        "GET listado/búsqueda usuario",
        lambda: call(
            "GET",
            "/usuarios/",
            expected=(200,),
            token=CTX.admin_token,
            params={"q": target_email, "limit": 500},
        ),
    )
    check(
        "GET permisos usuario",
        lambda: call(
            "GET",
            f"/usuarios/{target_id}/permisos",
            expected=(200,),
            token=CTX.admin_token,
        ),
    )

    replacement_email = f"qau{TOKEN}@qa.cl"
    check(
        "PUT usuario",
        lambda: call(
            "PUT",
            f"/usuarios/{target_id}",
            expected=(200,),
            token=CTX.admin_token,
            json={
                "usr_nombres": "QAUpdated",
                "usr_apellido_paterno": "Auto",
                "usr_apellido_materno": None,
                "usr_rut_sin_dv": f"64{TOKEN[:4]}04",
                "usr_dv": "K",
                "usr_telefono": "922222222",
                "usr_email": replacement_email,
                "usr_rol_id": viewer_role_id,
                "usr_estado_usuario_id": CTX.active_state_id,
                "usr_area_id": area_id,
            },
        ),
    )
    check(
        "PATCH usuario",
        lambda: call(
            "PATCH",
            f"/usuarios/{target_id}",
            expected=(200,),
            token=CTX.admin_token,
            json={"usr_telefono": "933333333"},
        ),
    )
    check(
        "PATCH vacío -> 422",
        lambda: call(
            "PATCH",
            f"/usuarios/{target_id}",
            expected=(422,),
            token=CTX.admin_token,
            json={},
        ),
    )
    check(
        "FK rol inexistente -> 422",
        lambda: call(
            "PATCH",
            f"/usuarios/{target_id}",
            expected=(422,),
            token=CTX.admin_token,
            json={"usr_rol_id": 999999999},
        ),
    )
    check(
        "Email duplicado -> 409",
        lambda: call(
            "PATCH",
            f"/usuarios/{target_id}",
            expected=(409,),
            token=CTX.admin_token,
            json={"usr_email": ADMIN_EMAIL},
        ),
    )

    new_password = "ResetTarget123!"
    check(
        "Reset password administrador",
        lambda: call(
            "POST",
            f"/usuarios/{target_id}/reset-password",
            expected=(204,),
            token=CTX.admin_token,
            json={"nueva_contrasena": new_password},
        ),
    )
    check(
        "Login tras reset password",
        lambda: login(replacement_email, new_password, expected=(200,)),
    )

    # Auto baja admin
    check(
        "Administrador no puede autoeliminarse -> 409",
        lambda: call(
            "DELETE",
            f"/usuarios/{CTX.admin_id}",
            expected=(409,),
            token=CTX.admin_token,
        ),
    )

    # CRUD permiso temporal
    p_id = create_permission(f"QAP{TOKEN}")
    check(
        "GET permiso",
        lambda: call("GET", f"/usuarios/permisos/{p_id}", expected=(200,), token=CTX.admin_token),
    )
    check(
        "PUT permiso",
        lambda: call(
            "PUT",
            f"/usuarios/permisos/{p_id}",
            expected=(200,),
            token=CTX.admin_token,
            json={"per_nombre": f"QAX{TOKEN}", "per_descripcion": "PUT"},
        ),
    )
    check(
        "PATCH permiso",
        lambda: call(
            "PATCH",
            f"/usuarios/permisos/{p_id}",
            expected=(200,),
            token=CTX.admin_token,
            json={"per_descripcion": "PATCH"},
        ),
    )

    # CRUD rol temporal + RBAC add/remove
    r_id = create_role(f"QAR{TOKEN}")
    check(
        "PUT rol",
        lambda: call(
            "PUT",
            f"/usuarios/roles/{r_id}",
            expected=(200,),
            token=CTX.admin_token,
            json={"rol_nombre": f"QAU{TOKEN}", "rol_descripcion": "PUT"},
        ),
    )
    check(
        "PATCH rol",
        lambda: call(
            "PATCH",
            f"/usuarios/roles/{r_id}",
            expected=(200,),
            token=CTX.admin_token,
            json={"rol_descripcion": "PATCH"},
        ),
    )
    check(
        "Agregar permiso al rol",
        lambda: call(
            "POST",
            f"/usuarios/roles/{r_id}/permisos/{p_id}",
            expected=(200,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Consultar permisos del rol",
        lambda: call(
            "GET",
            f"/usuarios/roles/{r_id}/permisos",
            expected=(200,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Quitar permiso del rol",
        lambda: call(
            "DELETE",
            f"/usuarios/roles/{r_id}/permisos/{p_id}",
            expected=(200,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Quitar permiso no asignado -> 404",
        lambda: call(
            "DELETE",
            f"/usuarios/roles/{r_id}/permisos/{p_id}",
            expected=(404,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Permiso inexistente al reemplazar -> 422",
        lambda: call(
            "PUT",
            f"/usuarios/roles/{r_id}/permisos",
            expected=(422,),
            token=CTX.admin_token,
            json={"permiso_ids": [999999999]},
        ),
    )
    check(
        "permiso_ids duplicados -> 422",
        lambda: call(
            "PUT",
            f"/usuarios/roles/{r_id}/permisos",
            expected=(422,),
            token=CTX.admin_token,
            json={"permiso_ids": [view_id, view_id]},
        ),
    )

    # Estado/área en uso no eliminables
    check(
        "Área en uso -> DELETE 409",
        lambda: call(
            "DELETE",
            f"/usuarios/areas/{area_id}",
            expected=(409,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Rol en uso -> DELETE 409",
        lambda: call(
            "DELETE",
            f"/usuarios/roles/{viewer_role_id}",
            expected=(409,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Estado en uso -> DELETE 409",
        lambda: call(
            "DELETE",
            f"/usuarios/estados/{inactive_state_id}",
            expected=(409,),
            token=CTX.admin_token,
        ),
    )

    # Baja lógica target
    check(
        "DELETE usuario = baja lógica",
        lambda: call(
            "DELETE",
            f"/usuarios/{target_id}",
            expected=(204,),
            token=CTX.admin_token,
        ),
    )
    check(
        "Usuario eliminado no puede hacer login -> 403",
        lambda: login(replacement_email, new_password, expected=(403,)),
    )


def cleanup() -> None:
    if not CTX.admin_token:
        return

    print("\n--- CLEANUP QA ---")

    # Mover usuarios QA a estado Eliminado y liberar rol/área.
    for user_id in reversed(CTX.created_users):
        try:
            call(
                "PATCH",
                f"/usuarios/{user_id}",
                expected=(200, 404),
                token=CTX.admin_token,
                json={
                    "usr_rol_id": None,
                    "usr_area_id": None,
                    "usr_estado_usuario_id": CTX.deleted_state_id,
                },
            )
        except Exception as exc:
            print(f"[WARN] cleanup usuario {user_id}: {exc}")

    for role_id in reversed(CTX.created_roles):
        try:
            call("DELETE", f"/usuarios/roles/{role_id}", expected=(204, 404), token=CTX.admin_token)
        except Exception as exc:
            print(f"[WARN] cleanup rol {role_id}: {exc}")

    for permission_id in reversed(CTX.created_permissions):
        try:
            call("DELETE", f"/usuarios/permisos/{permission_id}", expected=(204, 404), token=CTX.admin_token)
        except Exception as exc:
            print(f"[WARN] cleanup permiso {permission_id}: {exc}")

    for area_id in reversed(CTX.created_areas):
        try:
            call("DELETE", f"/usuarios/areas/{area_id}", expected=(204, 404), token=CTX.admin_token)
        except Exception as exc:
            print(f"[WARN] cleanup área {area_id}: {exc}")

    for state_id in reversed(CTX.created_states):
        try:
            call("DELETE", f"/usuarios/estados/{state_id}", expected=(204, 404), token=CTX.admin_token)
        except Exception as exc:
            print(f"[WARN] cleanup estado {state_id}: {exc}")


def main() -> int:
    require_admin_credentials()
    print(f"Sakura Módulo 1 LIVE QA\nAPI={BASE_URL}\nRUN={TOKEN}\n")

    try:
        bootstrap()
        run_tests()
    except Exception as exc:
        print(f"\nRESULTADO: FAILED\n{exc}")
        return_code = 1
    else:
        print("\nRESULTADO: PASSED - Todos los casos live finalizaron correctamente.")
        return_code = 0
    finally:
        cleanup()

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
