from app.candidatos.cv_parser import parse_core


def _cv(*lines: str) -> str:
    return "\n".join(lines)


def _base(*lines: str) -> str:
    return _cv("Catherine Rebolledo", "catherine@example.cl", *lines)


def test_rut_valido_con_puntos_y_guion():
    data, _warnings = parse_core(_base("RUT: 12.345.678-5"))

    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_dv"] == 5


def test_rut_valido_sin_puntos_y_con_guion():
    data, _warnings = parse_core(_base("Rut: 12345678-5"))

    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_dv"] == 5


def test_rut_valido_sin_puntos_ni_guion():
    data, _warnings = parse_core(_base("RUN: 123456785"))

    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_dv"] == 5


def test_rut_valido_con_k():
    data, _warnings = parse_core(_base("R.U.T.: 22.000.001-K"))

    assert data["cand_rut_sin_dv"] == 22000001
    assert data["cand_dv"] == 10


def test_rut_con_dv_incorrecto_no_se_detecta():
    data, _warnings = parse_core(_base("RUT: 12.345.678-K"))

    assert data["cand_rut_sin_dv"] is None
    assert data["cand_dv"] is None


def test_linea_telefonos_no_produce_rut():
    data, _warnings = parse_core(_base("Teléfonos : 22380440 - 89351800"))

    assert data["cand_rut_sin_dv"] is None
    assert data["cand_dv"] is None


def test_linea_celular_no_produce_rut():
    data, _warnings = parse_core(_base("Cel. (56 - 9) 78798322"))

    assert data["cand_rut_sin_dv"] is None
    assert data["cand_dv"] is None


def test_numero_aislado_con_largo_similar_y_dv_invalido_no_se_detecta():
    data, _warnings = parse_core(_base("123456789"))

    assert data["cand_rut_sin_dv"] is None
    assert data["cand_dv"] is None


def test_telefono_real_22380440_no_se_detecta_como_rut():
    data, _warnings = parse_core(_base("22380440"))

    assert data["cand_rut_sin_dv"] is None
    assert data["cand_dv"] is None


def test_rut_etiquetado_tiene_prioridad_sobre_telefono_posterior():
    data, _warnings = parse_core(
        _base(
            "RUT: 19.243.779-2",
            "Teléfono: +56 9 1234 5678",
        )
    )

    assert data["cand_rut_sin_dv"] == 19243779
    assert data["cand_dv"] == 2


def test_rut_etiquetado_se_detecta_aunque_aparezca_despues_del_telefono():
    data, _warnings = parse_core(
        _base(
            "Teléfono: +56 9 1234 5678",
            "RUT: 19.243.779-2",
        )
    )

    assert data["cand_rut_sin_dv"] == 19243779
    assert data["cand_dv"] == 2


def test_cv_sin_rut_mantiene_none():
    data, _warnings = parse_core(_base("+56 9 1234 5678"))

    assert data["cand_rut_sin_dv"] is None
    assert data["cand_dv"] is None


def test_rut_no_regresa_nombre_email_y_telefono():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
            "+56 9 1234 5678",
            "RUT: 12.345.678-5",
        )
    )

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_email"] == "catherine.rebolledo@example.cl"
    assert data["cand_telefono"] == "912345678"
    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_dv"] == 5
