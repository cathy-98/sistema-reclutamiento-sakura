import pytest

from app.candidatos import cv_parser
from app.candidatos.cv_parser import parse_core


def _cv(*lines: str) -> str:
    return "\n".join(lines)


def _ocr_cv(*lines: str) -> str:
    return cv_parser._ExtractedText("\n".join(lines), from_ocr=True)


def test_nombre_dos_palabras():
    data, _warnings = parse_core(_cv("Catherine Rebolledo", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_nombre_tres_palabras_documenta_regla_actual():
    data, _warnings = parse_core(_cv("Catherine Andrea Rebolledo", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Andrea"
    assert data["cand_apellido_materno"] == "Rebolledo"


def test_nombre_cuatro_palabras():
    data, _warnings = parse_core(_cv("Catherine Andrea Rebolledo Pastene", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine Andrea"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] == "Pastene"


def test_nombre_en_mayusculas_sigue_detectandose():
    data, _warnings = parse_core(_cv("CATHERINE REBOLLEDO", "catherine@example.cl"))

    assert data["cand_nombres"] == "CATHERINE"
    assert data["cand_apellido_paterno"] == "REBOLLEDO"


def test_nombre_soporta_tildes_y_enie():
    data, _warnings = parse_core(_cv("José Muñoz", "jose@example.cl"))

    assert data["cand_nombres"] == "José"
    assert data["cand_apellido_paterno"] == "Muñoz"


def test_nombre_ocr_con_icono_y_email_en_misma_linea():
    data, _warnings = parse_core(_ocr_cv("Catherine Rebolledo O catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_nombre_ocr_con_email_en_misma_linea_sin_icono():
    data, _warnings = parse_core(_ocr_cv("Catherine Rebolledo catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_email_ocr_sin_nombre_no_inventa_identidad():
    with pytest.raises(ValueError, match="No fue posible identificar nombres y apellido"):
        parse_core(_ocr_cv("catherine@example.cl"))


def test_cargo_ocr_con_email_no_se_confunde_como_nombre():
    with pytest.raises(ValueError, match="No fue posible identificar nombres y apellido"):
        parse_core(_ocr_cv("Product Designer catherine@example.cl"))


def test_institucion_ocr_con_email_no_se_confunde_como_nombre():
    with pytest.raises(ValueError, match="No fue posible identificar nombres y apellido"):
        parse_core(_ocr_cv("Universidad de Chile contacto@example.cl"))


def test_caso_real_catherine_ocr_nombre_y_email_deformado():
    data, _warnings = parse_core(_ocr_cv("Catherine Rebolledo O Cathyrehopas@gmalicom"))

    assert data["cand_email"] == "cathyrehopas@gmail.com"
    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_no_toma_curriculum_vitae_como_nombre_y_sigue_buscando():
    data, _warnings = parse_core(_cv("Curriculum Vitae", "Catherine Rebolledo", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"


def test_no_toma_hoja_de_vida_como_nombre_y_sigue_buscando():
    data, _warnings = parse_core(_cv("HOJA DE VIDA", "Catherine Rebolledo", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"


def test_no_toma_datos_personales_como_nombre_y_sigue_buscando():
    data, _warnings = parse_core(_cv("Datos Personales", "Catherine Rebolledo", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"


def test_no_toma_perfil_profesional_como_nombre_y_sigue_buscando():
    data, _warnings = parse_core(
        _cv("Perfil Profesional", "Developer", "Catherine Rebolledo", "catherine@example.cl")
    )

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"


def test_no_usa_lineas_email_linkedin_o_github_como_nombre():
    data, _warnings = parse_core(
        _cv(
            "LinkedIn Catherine Rebolledo",
            "GitHub Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
        )
    )

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert "Nombre inferido desde la parte local del correo" in _warnings[0]


def test_nombre_no_detectable_usa_fallback_actual_desde_email():
    data, warnings = parse_core(_cv("Contacto", "catherine.rebolledo@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None
    assert warnings == ["Nombre inferido desde la parte local del correo; revisar manualmente."]


def test_cv_sin_nombre_seguro_y_sin_fallback_valido_mantiene_error_actual():
    with pytest.raises(ValueError, match="No fue posible identificar nombres y apellido"):
        parse_core(_cv("Contacto", "info@example.cl"))


def test_parse_core_mantiene_titulo_y_datos_basicos():
    data, _warnings = parse_core(
        _cv(
            "Currículum Vitae",
            "Catherine Rebolledo",
            "UX/UI Designer",
            "catherine.rebolledo@example.cl",
            "+56 9 1234 5678",
            "12345678-5",
            "https://www.linkedin.com/in/catherine",
            "Perfil Profesional",
            "Profesional con amplia experiencia en diseño de productos digitales y colaboración con equipos técnicos.",
        )
    )

    assert data["cand_email"] == "catherine.rebolledo@example.cl"
    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_telefono"] == "912345678"
    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_dv"] == 5
    assert "linkedin" in (data["cand_url_1"] or "")
    assert data["cand_titulo"] == "UX/UI Designer"
    assert data["cand_resumen_profesional"] is not None


def test_nombre_dividido_en_dos_lineas_pablo():
    data, _warnings = parse_core(
        _cv(
            "Pablo Roberto Palma",
            "Parada",
            "Desarrollador Full Stack",
            "pablo@example.cl",
        )
    )

    assert data["cand_nombres"] == "Pablo Roberto"
    assert data["cand_apellido_paterno"] == "Palma"
    assert data["cand_apellido_materno"] == "Parada"


def test_nombre_dividido_en_dos_lineas_daniel():
    data, _warnings = parse_core(
        _cv(
            "DANIEL OSVALDO",
            "REBOLLEDO MUÑOZ",
            "drebolledo@example.cl",
        )
    )

    assert data["cand_nombres"] == "DANIEL OSVALDO"
    assert data["cand_apellido_paterno"] == "REBOLLEDO"
    assert data["cand_apellido_materno"] == "MUÑOZ"


def test_nombre_con_prefijo_nombre_dos_puntos():
    data, warnings = parse_core(_cv("Nombre: PATRICIO GAJARDO ROJAS", "patricio.henry@example.cl"))

    assert data["cand_nombres"] == "PATRICIO"
    assert data["cand_apellido_paterno"] == "GAJARDO"
    assert data["cand_apellido_materno"] == "ROJAS"
    assert warnings == []


def test_nombre_con_prefijo_nombre_espacio_dos_puntos():
    data, warnings = parse_core(_cv("Nombre : PATRICIO GAJARDO ROJAS", "patricio.henry@example.cl"))

    assert data["cand_nombres"] == "PATRICIO"
    assert data["cand_apellido_paterno"] == "GAJARDO"
    assert data["cand_apellido_materno"] == "ROJAS"
    assert warnings == []


def test_nombre_con_metadata_de_ubicacion_en_misma_linea():
    data, _warnings = parse_core(_cv("Catherine Rebolledo Santiago, RM, Chile", "cathyrebopas@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_no_toma_linea_academica_con_ubicacion_e_institucion_como_nombre():
    data, warnings = parse_core(
        _cv(
            "Curicó-Chile Universidad Tecnológica INACAP",
            "francisco.munoz@example.cl",
        )
    )

    assert data["cand_nombres"] == "Francisco"
    assert data["cand_apellido_paterno"] == "Munoz"
    assert warnings == ["Nombre inferido desde la parte local del correo; revisar manualmente."]


def test_no_toma_linea_academica_antes_del_nombre_real():
    data, warnings = parse_core(
        _cv(
            "https://www.linkedin.com/in/francisco",
            "2011-2015 Ingeniero en informática",
            "Curicó-Chile Universidad Tecnológica INACAP",
            "Santiago-Chile AIEP",
            "Español",
            "Inglés",
            "Francisco Muñoz Silva",
            "francisco.a.munoz.silva@example.cl",
        )
    )

    assert data["cand_nombres"] == "Francisco"
    assert data["cand_apellido_paterno"] == "Muñoz"
    assert data["cand_apellido_materno"] == "Silva"
    assert warnings == []


def test_nombre_valido_no_combina_cargo_debajo():
    data, _warnings = parse_core(_cv("Catherine Rebolledo", "UX/UI Designer", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_nombre_valido_no_combina_ciudad_debajo():
    data, _warnings = parse_core(_cv("Catherine Rebolledo", "Santiago, Chile", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_nombre_valido_no_combina_institucion_debajo():
    data, _warnings = parse_core(_cv("Catherine Rebolledo", "Universidad de Chile", "catherine@example.cl"))

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_apellido_materno"] is None


def test_regresion_nombres_simples_de_dos_tres_y_cuatro_palabras():
    data_2, _warnings = parse_core(_cv("Catherine Rebolledo", "catherine@example.cl"))
    data_3, _warnings = parse_core(_cv("Catherine Andrea Rebolledo", "catherine@example.cl"))
    data_4, _warnings = parse_core(_cv("Catherine Andrea Rebolledo Pastene", "catherine@example.cl"))

    assert (data_2["cand_nombres"], data_2["cand_apellido_paterno"], data_2["cand_apellido_materno"]) == (
        "Catherine",
        "Rebolledo",
        None,
    )
    assert (data_3["cand_nombres"], data_3["cand_apellido_paterno"], data_3["cand_apellido_materno"]) == (
        "Catherine",
        "Andrea",
        "Rebolledo",
    )
    assert (data_4["cand_nombres"], data_4["cand_apellido_paterno"], data_4["cand_apellido_materno"]) == (
        "Catherine Andrea",
        "Rebolledo",
        "Pastene",
    )
