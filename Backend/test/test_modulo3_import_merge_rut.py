from types import SimpleNamespace

from app.candidatos.router import _merge_imported_core_fields


def _candidate(**overrides):
    base = {
        "cand_email": "jaime.olivares1982@gmail.com",
        "cand_nombres": "Nombre Existente",
        "cand_apellido_paterno": "Apellido",
        "cand_apellido_materno": None,
        "cand_telefono": "telefono-existente",
        "cand_rut_sin_dv": None,
        "cand_dv": None,
        "cand_titulo": "Titulo Existente",
        "cand_resumen_profesional": "Resumen existente",
        "cand_url_1": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _core(**overrides):
    base = {
        "cand_email": "jaime.olivares1982@gmail.com",
        "cand_nombres": "JAIME MAURICIO",
        "cand_apellido_paterno": "OLIVARES",
        "cand_apellido_materno": "VALENZUELA",
        "cand_telefono": None,
        "cand_rut_sin_dv": 15467207,
        "cand_dv": 9,
        "cand_titulo": None,
        "cand_resumen_profesional": None,
        "cand_url_1": None,
    }
    base.update(overrides)
    return base


def test_merge_reemplaza_rut_existente_invalido_con_nuevo_valido():
    existing = _candidate(cand_rut_sin_dv=2238044, cand_dv=9)

    _merge_imported_core_fields(existing, _core(cand_rut_sin_dv=15467207, cand_dv=9))

    assert existing.cand_rut_sin_dv == 15467207
    assert existing.cand_dv == 9


def test_merge_conserva_rut_existente_valido_si_nuevo_valido_es_distinto():
    existing = _candidate(cand_rut_sin_dv=12345678, cand_dv=5)

    _merge_imported_core_fields(existing, _core(cand_rut_sin_dv=15467207, cand_dv=9))

    assert existing.cand_rut_sin_dv == 12345678
    assert existing.cand_dv == 5


def test_merge_completa_rut_vacio_con_nuevo_valido():
    existing = _candidate(cand_rut_sin_dv=None, cand_dv=None)

    _merge_imported_core_fields(existing, _core(cand_rut_sin_dv=15467207, cand_dv=9))

    assert existing.cand_rut_sin_dv == 15467207
    assert existing.cand_dv == 9


def test_merge_conserva_rut_existente_invalido_si_cv_no_trae_rut():
    existing = _candidate(cand_rut_sin_dv=2238044, cand_dv=9)

    _merge_imported_core_fields(existing, _core(cand_rut_sin_dv=None, cand_dv=None))

    assert existing.cand_rut_sin_dv == 2238044
    assert existing.cand_dv == 9


def test_merge_conserva_rut_existente_valido_si_cv_no_trae_rut():
    existing = _candidate(cand_rut_sin_dv=12345678, cand_dv=5)

    _merge_imported_core_fields(existing, _core(cand_rut_sin_dv=None, cand_dv=None))

    assert existing.cand_rut_sin_dv == 12345678
    assert existing.cand_dv == 5


def test_merge_no_sobrescribe_otros_campos_existentes():
    existing = _candidate(
        cand_rut_sin_dv=2238044,
        cand_dv=9,
        cand_nombres="Nombre Existente",
        cand_apellido_paterno="Apellido Existente",
        cand_telefono="999999999",
        cand_titulo="Titulo Existente",
        cand_resumen_profesional="Resumen existente",
    )

    _merge_imported_core_fields(
        existing,
        _core(
            cand_rut_sin_dv=15467207,
            cand_dv=9,
            cand_nombres="JAIME MAURICIO",
            cand_apellido_paterno="OLIVARES",
            cand_telefono="912345678",
            cand_titulo="Titulo Nuevo",
            cand_resumen_profesional="Resumen nuevo",
        ),
    )

    assert existing.cand_rut_sin_dv == 15467207
    assert existing.cand_dv == 9
    assert existing.cand_nombres == "Nombre Existente"
    assert existing.cand_apellido_paterno == "Apellido Existente"
    assert existing.cand_telefono == "999999999"
    assert existing.cand_titulo == "Titulo Existente"
    assert existing.cand_resumen_profesional == "Resumen existente"


def test_merge_caso_jaime_corrige_rut_invalido_previo():
    existing = _candidate(
        cand_email="jaime.olivares1982@gmail.com",
        cand_rut_sin_dv=2238044,
        cand_dv=9,
    )
    parsed_core = _core(
        cand_email="jaime.olivares1982@gmail.com",
        cand_rut_sin_dv=15467207,
        cand_dv=9,
    )

    _merge_imported_core_fields(existing, parsed_core)

    assert existing.cand_rut_sin_dv == 15467207
    assert existing.cand_dv == 9


def test_merge_completa_titulo_y_resumen_vacios_con_valores_detectados():
    existing = _candidate(cand_titulo=None, cand_resumen_profesional=None)

    _merge_imported_core_fields(
        existing,
        _core(
            cand_titulo="UX/UI Designer con enfoque en Frontend",
            cand_resumen_profesional="Diseñadora UX/UI con experiencia en productos digitales.",
        ),
    )

    assert existing.cand_titulo == "UX/UI Designer con enfoque en Frontend"
    assert existing.cand_resumen_profesional == "Diseñadora UX/UI con experiencia en productos digitales."


def test_merge_conserva_titulo_y_resumen_existentes_si_cv_trae_otros():
    existing = _candidate(
        cand_titulo="Título validado manualmente",
        cand_resumen_profesional="Resumen validado manualmente",
    )

    _merge_imported_core_fields(
        existing,
        _core(
            cand_titulo="Título nuevo desde CV",
            cand_resumen_profesional="Resumen nuevo desde CV",
        ),
    )

    assert existing.cand_titulo == "Título validado manualmente"
    assert existing.cand_resumen_profesional == "Resumen validado manualmente"


def test_merge_no_borra_titulo_ni_resumen_si_parser_devuelve_none():
    existing = _candidate(
        cand_titulo="Título existente",
        cand_resumen_profesional="Resumen existente",
    )

    _merge_imported_core_fields(
        existing,
        _core(cand_titulo=None, cand_resumen_profesional=None),
    )

    assert existing.cand_titulo == "Título existente"
    assert existing.cand_resumen_profesional == "Resumen existente"
