from app.candidatos.cv_parser import parse_core


def _cv(*lines: str) -> str:
    return "\n".join(lines)


def test_resumen_detecta_texto_posterior_a_perfil_profesional():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Perfil Profesional",
            "Diseñadora UX/UI con experiencia en productos digitales.",
        )
    )

    assert data["cand_resumen_profesional"] == "Diseñadora UX/UI con experiencia en productos digitales."


def test_resumen_detecta_encabezado_en_mayusculas():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "RESUMEN PROFESIONAL",
            "Analista de datos con experiencia en banca.",
        )
    )

    assert data["cand_resumen_profesional"] == "Analista de datos con experiencia en banca."


def test_resumen_detecta_professional_summary_en_ingles():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Professional Summary",
            "Software developer with experience building web applications.",
        )
    )

    assert data["cand_resumen_profesional"] == "Software developer with experience building web applications."


def test_resumen_detecta_sobre_mi():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Sobre mí",
            "Profesional enfocada en productos digitales y experiencia de usuario.",
        )
    )

    assert data["cand_resumen_profesional"] == "Profesional enfocada en productos digitales y experiencia de usuario."


def test_resumen_varias_lineas_se_une_y_se_detiene_en_experiencia_laboral():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Perfil Profesional",
            "Diseñadora UX/UI con experiencia en productos digitales.",
            "Especializada en investigación y diseño de interfaces.",
            "Experiencia Laboral",
            "Developer - Empresa X",
        )
    )

    assert data["cand_resumen_profesional"] == (
        "Diseñadora UX/UI con experiencia en productos digitales. "
        "Especializada en investigación y diseño de interfaces."
    )


def test_resumen_no_usa_descripcion_de_experiencia_laboral():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Experiencia Laboral",
            "Developer - Empresa X",
            "Responsable del desarrollo de aplicaciones empresariales para clientes corporativos.",
        )
    )

    assert data["cand_resumen_profesional"] is None


def test_resumen_no_usa_texto_largo_de_educacion():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Educación",
            "Ingeniería Informática en universidad con formación orientada a desarrollo de software.",
        )
    )

    assert data["cand_resumen_profesional"] is None


def test_resumen_none_si_no_existe_seccion_explicita():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Responsable del desarrollo de aplicaciones empresariales para clientes corporativos.",
        )
    )

    assert data["cand_resumen_profesional"] is None


def test_resumen_omite_email_y_url_dentro_del_bloque():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine@example.cl",
            "Perfil Profesional",
            "catherine.personal@example.cl",
            "https://www.linkedin.com/in/catherine",
            "Diseñadora UX/UI con experiencia en productos digitales.",
        )
    )

    assert data["cand_resumen_profesional"] == "Diseñadora UX/UI con experiencia en productos digitales."


def test_resumen_y_titulo_se_detectan_por_separado():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "UX/UI Designer",
            "catherine@example.cl",
            "Perfil Profesional",
            "Diseñadora enfocada en productos digitales y experiencia de usuario.",
        )
    )

    assert data["cand_titulo"] == "UX/UI Designer"
    assert data["cand_resumen_profesional"] == (
        "Diseñadora enfocada en productos digitales y experiencia de usuario."
    )


def test_resumen_no_regresa_nombre_email_telefono():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo",
            "catherine.rebolledo@example.cl",
            "+56 9 1234 5678",
            "Perfil Profesional",
            "Diseñadora UX/UI con experiencia en productos digitales.",
        )
    )

    assert data["cand_nombres"] == "Catherine"
    assert data["cand_apellido_paterno"] == "Rebolledo"
    assert data["cand_email"] == "catherine.rebolledo@example.cl"
    assert data["cand_telefono"] == "912345678"
    assert data["cand_resumen_profesional"] == "Diseñadora UX/UI con experiencia en productos digitales."


def test_resumen_catherine_se_recupera_despues_de_titulo_en_cabecera():
    data, _warnings = parse_core(
        _cv(
            "Catherine Rebolledo Santiago, RM, Chile",
            "Cathyrebopas@gmail.com",
            "UX/UI Designer con enfoque en Frontend",
            "Diseñadora UX/UI con experiencia en productos digitales y colaboración directa con",
            "desarrollo frontend. He participado en investigación, diseño y documentación de",
            "interfaces y apoyo en la comunicación con equipos técnicos.",
            "Actualmente me encuentro fortaleciendo mis habilidades en frontend.",
            "linkedin: /catherine-rebolledo",
            "+56957034447",
        )
    )

    assert data["cand_resumen_profesional"] == (
        "Diseñadora UX/UI con experiencia en productos digitales y colaboración directa con "
        "desarrollo frontend. He participado en investigación, diseño y documentación de "
        "interfaces y apoyo en la comunicación con equipos técnicos. "
        "Actualmente me encuentro fortaleciendo mis habilidades en frontend."
    )


def test_resumen_detecta_presentacion_y_se_detiene_en_antecedentes_personales():
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

    assert data["cand_resumen_profesional"] == (
        "Ingeniero de ejecución en informática egresado y Analista de sistemas titulado. "
        "Más de 10 años de experiencia liderando proyectos tecnológicos."
    )


def test_resumen_detecta_declaracion_profesional_con_anios_de_experiencia():
    data, _warnings = parse_core(
        _cv(
            "Francisco Muñoz Silva",
            "francisco.munoz@example.cl",
            "Técnicas: Microsoft Office, SQL Server, VMware ESX.",
            "Personales: Trabajo en equipo, proactividad y organización.",
            "Con más de 5 años de experiencia en área de servicios TI, cabe indicar",
            "que soy una persona comprometida, organizada, responsable, con buena",
            "actitud para trabajar en equipo.",
            "HABILIDADES",
            "SQL",
        )
    )

    assert data["cand_resumen_profesional"] == (
        "Con más de 5 años de experiencia en área de servicios TI, cabe indicar "
        "que soy una persona comprometida, organizada, responsable, con buena "
        "actitud para trabajar en equipo."
    )
