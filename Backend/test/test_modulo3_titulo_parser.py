from app.candidatos.cv_parser import parse_core


def _cv(*lines: str) -> str:
    return "\n".join(lines)


def test_titulo_detecta_ux_ui_designer_en_bloque_superior():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "UX/UI Designer",
            "catherine.rebolledo@example.cl",
            "+56 9 1234 5678",
        )
    )

    assert data["cand_titulo"] == "UX/UI Designer"


def test_titulo_no_toma_linea_de_educacion():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
            "Educación",
            "Ingeniería Informática - Universidad X",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_no_toma_linea_de_experiencia_laboral():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
            "Experiencia Laboral",
            "Developer - Empresa X",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_no_toma_frase_de_resumen_profesional():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
            "Perfil Profesional",
            "Analista con experiencia en banca y retail",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_no_usa_email_o_contacto_con_keyword_profesional():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "developer.data@example.cl",
            "+56 9 1234 5678",
            "Contacto",
            "LinkedIn developer-data",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_none_si_no_hay_titulo_profesional_claro():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
            "+56 9 1234 5678",
            "Santiago Chile",
            "Disponibilidad inmediata",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_valido_antes_de_secciones_se_sigue_detectando():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "Product Designer",
            "catherine.rebolledo@example.cl",
            "Experiencia Laboral",
            "Developer - Empresa X",
        )
    )

    assert data["cand_titulo"] == "Product Designer"


def test_parse_core_mantiene_datos_basicos_al_detectar_titulo():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "UX/UI Designer",
            "catherine.rebolledo@example.cl",
            "+56 9 1234 5678",
            "12345678-5",
            "https://www.linkedin.com/in/catherine",
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


def test_titulo_no_toma_linea_academica_con_rango_en_educacion():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Educación",
            "2011-2015 Ingeniero en informática",
            "INACAP",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_no_toma_carrera_bajo_formacion_academica():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "FORMACIÓN ACADÉMICA",
            "2018 - 2022",
            "Ingeniería Civil Informática",
            "Universidad X",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_no_toma_estudio_con_rango_en_misma_linea():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "ESTUDIOS",
            "2019–2023 Diseño Gráfico",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_recupera_profesion_breve_en_cabecera_con_rango_francisco():
    data, _warnings = parse_core(
        _cv(
            "https://www.linkedin.com/in/francisco",
            "2011-2015 Ingeniero en informática",
            "Curicó-Chile Universidad Tecnológica INACAP",
            "Francisco Muñoz Silva",
            "francisco.munoz@example.cl",
            "EDUCACIÓN",
        )
    )

    assert data["cand_titulo"] == "Ingeniero en informática"


def test_titulo_mantiene_ux_ui_designer():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "UX/UI Designer",
            "catherine@example.cl",
        )
    )

    assert data["cand_titulo"] == "UX/UI Designer"


def test_titulo_mantiene_desarrollador_full_stack():
    data, _warnings = parse_core(
        _cv(
            "Pablo Palma",
            "Desarrollador Full Stack",
            "pablo@example.cl",
        )
    )

    assert data["cand_titulo"] == "Desarrollador Full Stack"


def test_titulo_mantiene_mba_ingeniero_civil_industrial():
    data, _warnings = parse_core(
        _cv(
            "Pablo Gorriateguy",
            "MBA Ingeniero Civil Industrial",
            "pablo@example.cl",
            "Education",
            "Ingeniería Civil Industrial",
        )
    )

    assert data["cand_titulo"] == "MBA Ingeniero Civil Industrial"


def test_titulo_valido_antes_de_educacion_se_mantiene():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "UX/UI Designer",
            "catherine@example.cl",
            "Educación",
            "Diseño y Comunicación Digital",
        )
    )

    assert data["cand_titulo"] == "UX/UI Designer"


def test_titulo_none_con_solo_nombre_y_educacion():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Educación",
            "Diseño y Comunicación Digital",
        )
    )

    assert data["cand_titulo"] is None


def test_titulo_catherine_acepta_perfil_con_enfoque_en_cabecera():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo Santiago, RM, Chile",
            "Cathyrebopas@gmail.com",
            "UX/UI Designer con enfoque en Frontend",
            "Diseñadora UX/UI con experiencia en productos digitales y colaboración directa con",
            "desarrollo frontend.",
            "+56957034447",
        )
    )

    assert data["cand_titulo"] == "UX/UI Designer con enfoque en Frontend"


def test_titulo_jaime_se_deriva_de_presentacion_explicita():
    data, _warnings = parse_core(
        _cv(
            "JAIME MAURICIO OLIVARES VALENZUELA",
            "jaime.olivares@example.cl",
            "PRESENTACION",
            "Ingeniero de ejecución en informática egresado y Analista de sistemas titulado.",
            "Más de 10 años de experiencia liderando proyectos tecnológicos.",
            "ANTECEDENTES PERSONALES",
            "Rut: 12345678-5",
        )
    )

    assert data["cand_titulo"] == "Ingeniero de ejecución en informática"


def test_titulo_daniel_se_deriva_de_resumen_explicito():
    data, _warnings = parse_core(
        _cv(
            "Daniel Rebolledo",
            "daniel.rebolledo@example.cl",
            "Resumen Profesional",
            "•Ingeniero Civil Industrial con mención en Energía y Medioambiente.",
            "Áreas de interés en gestión de proyectos y mejora continua.",
        )
    )

    assert data["cand_titulo"] == "Ingeniero Civil Industrial"
