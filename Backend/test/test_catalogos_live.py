from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass, field
from typing import Any

import requests


BASE_URL = os.getenv("SAKURA_API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = float(os.getenv("SAKURA_API_TIMEOUT", "10"))
RUN_TOKEN = uuid.uuid4().hex[:6]


@dataclass(frozen=True)
class Dependency:
    resource: str
    id_field: str
    export_as: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class CatalogCase:
    resource: str
    id_field: str
    create_payload: dict[str, Any]
    put_payload: dict[str, Any]
    patch_payload: dict[str, Any]
    dependencies: tuple[Dependency, ...] = field(default_factory=tuple)


def resolve(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str):
            value = value.replace("$token", RUN_TOKEN)
            if value.startswith("$"):
                value = context[value[1:]]
        result[key] = value
    return result


def http_request(method: str, path: str, *, expected: tuple[int, ...], **kwargs) -> requests.Response:
    url = f"{BASE_URL}{path}"
    response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
    if response.status_code not in expected:
        raise RuntimeError(
            f"{method} {url} -> esperado {expected}, recibido "
            f"{response.status_code}: {response.text}"
        )
    return response


def cleanup(created: list[tuple[str, int]]) -> None:
    for resource, item_id in reversed(created):
        try:
            http_request(
                "DELETE",
                f"/catalogos/{resource}/{item_id}",
                expected=(204, 404),
            )
        except Exception as exc:
            print(f"WARNING cleanup {resource}/{item_id}: {exc}")


def create_dependencies(
    dependencies: tuple[Dependency, ...],
    created: list[tuple[str, int]],
) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for dependency in dependencies:
        payload = resolve(dependency.payload, context)
        response = http_request(
            "POST",
            f"/catalogos/{dependency.resource}",
            expected=(201,),
            json=payload,
        )
        body = response.json()
        item_id = body[dependency.id_field]
        context[dependency.export_as] = item_id
        created.append((dependency.resource, item_id))
    return context


PAIS = Dependency(
    "paises", "pais_id", "pais_id", {"pais_nombre": "QA-P-$token"}
)
REGION = Dependency(
    "regiones",
    "reg_id",
    "region_id",
    {"reg_pais_id": "$pais_id", "reg_nombre": "QA-R-$token"},
)
TIPO_INST = Dependency(
    "tipos-institucion",
    "tint_id",
    "tipo_institucion_id",
    {"tint_tipo_institucion": "QA-TI-$token"},
)


CASES = [
    CatalogCase("paises", "pais_id", {"pais_nombre": "QA-P-$token"}, {"pais_nombre": "QA-PU-$token"}, {"pais_nombre": "QA-PP-$token"}),
    CatalogCase("regiones", "reg_id", {"reg_pais_id": "$pais_id", "reg_nombre": "QA-R-$token"}, {"reg_pais_id": "$pais_id", "reg_nombre": "QA-RU-$token"}, {"reg_nombre": "QA-RP-$token"}, (PAIS,)),
CatalogCase(
    "comunas",
    "com_id",
    {
        "com_region_id": "$region_id",
        "com_nombre": "QA-COM-$token",
    },
    {
        "com_region_id": "$region_id",
        "com_nombre": "QA-COMU-$token",
    },
    {
        "com_nombre": "QA-COMP-$token",
    },
    dependencies=(
        PAIS,
        REGION,
    ),
),
    CatalogCase("tipos-institucion", "tint_id", {"tint_tipo_institucion": "QA-TI-$token"}, {"tint_tipo_institucion": "QA-TIU-$token"}, {"tint_tipo_institucion": "QA-TIP-$token"}),
    CatalogCase("instituciones", "inst_id", {"inst_nombre": "QA-I-$token", "inst_tipo_institucion_id": "$tipo_institucion_id"}, {"inst_nombre": "QA-IU-$token", "inst_tipo_institucion_id": "$tipo_institucion_id"}, {"inst_nombre": "QA-IP-$token"}, (TIPO_INST,)),
    CatalogCase("carreras", "crra_id", {"crra_nombre": "QA Carrera $token"}, {"crra_nombre": "QA Carrera U $token"}, {"crra_nombre": "QA Carrera P $token"}),
    CatalogCase("niveles-educacionales", "nved_id", {"nved_nombre": "QA-N-$token"}, {"nved_nombre": "QA-NU-$token"}, {"nved_nombre": "QA-NP-$token"}),
    CatalogCase("habilidades", "hab_id", {"hab_nombre": "QA-H-$token", "hab_descripcion": "QA habilidad"}, {"hab_nombre": "QA-HU-$token", "hab_descripcion": "QA PUT"}, {"hab_descripcion": "QA PATCH"}),
    CatalogCase("niveles-habilidad", "nvhb_id", {"nvhb_nombre": "QA-$token", "nvhb_descripcion": "Nivel QA", "nvhb_puntaje_base": 10, "nvhb_duracion": 12}, {"nvhb_nombre": "QB-$token", "nvhb_descripcion": "Nivel PUT", "nvhb_puntaje_base": 50, "nvhb_duracion": 24}, {"nvhb_puntaje_base": 75}),
    CatalogCase("cargos", "crgo_id", {"crgo_nombre": "QA-CG-$token", "crgo_descripcion": "Cargo QA"}, {"crgo_nombre": "QA-CGU-$token", "crgo_descripcion": "Cargo PUT"}, {"crgo_descripcion": "Cargo PATCH"}),
    CatalogCase("modalidades", "mdld_id", {"mdld_nombre": "QA-$token", "mdld_descripcion": "Modalidad QA"}, {"mdld_nombre": "QB-$token", "mdld_descripcion": "Modalidad PUT"}, {"mdld_descripcion": "Modalidad PATCH"}),
    CatalogCase("tipos-contrato", "tpct_id", {"tpct_nombre": "QA-$token", "tpct_descripcion": "Contrato QA"}, {"tpct_nombre": "QB-$token", "tpct_descripcion": "Contrato PUT"}, {"tpct_descripcion": "Contrato PATCH"}),
    CatalogCase("disponibilidades", "disp_id", {"disp_nombre": "QA-D-$token"}, {"disp_nombre": "QA-DU-$token"}, {"disp_nombre": "QA-DP-$token"}),
    CatalogCase("estados-solicitud", "essl_id", {"essl_nombre": "QA-$token", "essl_descripcion": "Estado QA"}, {"essl_nombre": "QB-$token", "essl_descripcion": "Estado PUT"}, {"essl_descripcion": "Estado PATCH"}),
    CatalogCase("prioridades-solicitud", "prsol_id", {"prsol_nombre": "QA-$token", "prsol_descripcion": "Prioridad QA"}, {"prsol_nombre": "QB-$token", "prsol_descripcion": "Prioridad PUT"}, {"prsol_descripcion": "Prioridad PATCH"}),
    CatalogCase("estados-solicitud-candidato", "essc_id", {"essc_nombre": "QA-ESC-$token", "essc_descripcion": "Estado QA"}, {"essc_nombre": "QA-ESU-$token", "essc_descripcion": "Estado PUT"}, {"essc_descripcion": "Estado PATCH"}),
    CatalogCase("motivos-rechazo", "mtrc_id", {"mtrc_nombre": "QA-M-$token", "mtrc_descripcion": "Motivo QA"}, {"mtrc_nombre": "QA-MU-$token", "mtrc_descripcion": "Motivo PUT"}, {"mtrc_descripcion": "Motivo PATCH"}),
    CatalogCase("estados-cuestionario-candidato", "escc_id", {"escc_nombre": "QA-EC-$token"}, {"escc_nombre": "QA-ECU-$token"}, {"escc_nombre": "QA-ECP-$token"}),
    CatalogCase("estados-entrevista", "esev_id", {"esev_nombre": "QA-EE-$token", "esev_descripcion": "Estado entrevista"}, {"esev_nombre": "QA-EEU-$token", "esev_descripcion": "Estado PUT"}, {"esev_descripcion": "Estado PATCH"}),
    CatalogCase("tipos-entrevista", "tpet_id", {"tpet_nombre": "QA-TE-$token", "tpet_descripcion": "Tipo QA"}, {"tpet_nombre": "QA-TEU-$token", "tpet_descripcion": "Tipo PUT"}, {"tpet_descripcion": "Tipo PATCH"}),
    CatalogCase("nombres-resultado", "nore_id", {"nore_nombre": "QA-NR-$token"}, {"nore_nombre": "QA-NRU-$token"}, {"nore_nombre": "QA-NRP-$token"}),
]


def run_case(case: CatalogCase) -> None:
    print("\n" + "=" * 68)
    print(f"TEST: {case.resource}")
    print("=" * 68)
    created: list[tuple[str, int]] = []

    try:
        context = create_dependencies(case.dependencies, created)
        create_payload = resolve(case.create_payload, context)

        response = http_request(
            "POST",
            f"/catalogos/{case.resource}",
            expected=(201,),
            json=create_payload,
        )
        item_id = response.json()[case.id_field]
        created.append((case.resource, item_id))
        print(f"OK POST -> ID {item_id}")

        response = http_request("GET", f"/catalogos/{case.resource}", expected=(200,))
        if not any(item.get(case.id_field) == item_id for item in response.json()):
            raise AssertionError("Registro no encontrado en GET listado")
        print("OK GET LIST")

        response = http_request(
            "GET",
            f"/catalogos/{case.resource}/{item_id}",
            expected=(200,),
        )
        assert response.json()[case.id_field] == item_id
        print("OK GET ID")

        http_request(
            "PUT",
            f"/catalogos/{case.resource}/{item_id}",
            expected=(200,),
            json=resolve(case.put_payload, context),
        )
        print("OK PUT")

        http_request(
            "PATCH",
            f"/catalogos/{case.resource}/{item_id}",
            expected=(200,),
            json=resolve(case.patch_payload, context),
        )
        print("OK PATCH")

        http_request(
            "DELETE",
            f"/catalogos/{case.resource}/{item_id}",
            expected=(204,),
        )
        print("OK DELETE")

        http_request(
            "GET",
            f"/catalogos/{case.resource}/{item_id}",
            expected=(404,),
        )
        print("OK 404 POST DELETE")
        print(f"PASS {case.resource}")

    finally:
        cleanup(created)


def main() -> None:
    print("\nSakura Catalog API Test Runner")
    print(f"API: {BASE_URL}")
    print(f"RUN TOKEN: {RUN_TOKEN}\n")

    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=TIMEOUT)
        response.raise_for_status()
    except Exception as exc:
        print("ERROR: no fue posible conectar con FastAPI.")
        print(exc)
        sys.exit(1)

    failures: list[tuple[str, str]] = []
    for case in CASES:
        try:
            run_case(case)
        except Exception as exc:
            failures.append((case.resource, str(exc)))
            print(f"FAIL {case.resource}: {exc}")

    print("\n" + "=" * 68)
    print("RESUMEN")
    print("=" * 68)
    print(f"Total:   {len(CASES)}")
    print(f"PASSED:  {len(CASES) - len(failures)}")
    print(f"FAILED:  {len(failures)}")

    if failures:
        print("\nErrores:")
        for resource, error in failures:
            print(f" - {resource}: {error}")
        sys.exit(1)

    print("\nTODOS LOS CATÁLOGOS PASARON CORRECTAMENTE.")


if __name__ == "__main__":
    main()
