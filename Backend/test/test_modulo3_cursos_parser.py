from app.candidatos import services
from app.catalogos.models import (
    Carrera,
    Cargo,
    Habilidad,
    Idioma,
    Institucion,
    NivelEducacional,
    NivelHabilidad,
    NivelIdioma,
)
from app.clientes.models import Empresa


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values

    def __iter__(self):
        return iter(self._values)


class _FakeDb:
    def __init__(self):
        self._values_by_model = {
            Empresa: [],
            Cargo: [],
            NivelHabilidad: [],
            Habilidad: [],
            Institucion: [],
            Carrera: [],
            NivelEducacional: [],
            NivelIdioma: [],
            Idioma: [],
        }

    def scalars(self, statement):
        model = statement.column_descriptions[0]["entity"]
        return _ScalarResult(self._values_by_model.get(model, []))


def _derive_cursos(texto: str):
    nested, _warnings = services.derive_nested_from_cv(_FakeDb(), texto)
    return nested["cursos"]


def _nombres(texto: str):
    return [item["curs_nombre_curso"] for item in _derive_cursos(texto)]


def test_cursos_ignora_headings():
    texto = "\n".join([
        "Cursos",
        "CURSOS",
        "Certificaciones",
        "Diplomados",
        "Certificación:",
    ])

    assert _derive_cursos(texto) == []


def test_cursos_ignora_descripciones_laborales_con_certificacion():
    texto = "\n".join([
        "empresarial de software , certificación de aplicaciones sobre distintas arquitecturas",
        "Certificación de aplicaciones internas y externas, validando funcionalidad",
        "Mejoras a sistemas, Certificaciones funcionales y de comunicación QA",
        "Software de Emisión de los Certificados de Saldos para plataforma Web",
        "ejecutaba utilizando recursos transaccionales en COM",
    ])

    assert _derive_cursos(texto) == []


def test_cursos_detecta_diplomados_reales_con_anio():
    nombres = _nombres(
        "\n".join([
            "2017-2017 Diplomado Gestión de Datacenter",
            "2018-2018 Diplomado Gestión de Datacenter",
            "2021 Diplomado en Gestion Publica",
        ])
    )

    assert nombres == [
        "2017-2017 Diplomado Gestión de Datacente",
        "2018-2018 Diplomado Gestión de Datacente",
        "2021 Diplomado en Gestion Publica",
    ]


def test_cursos_detecta_cursos_reales():
    nombres = _nombres(
        "\n".join([
            "1999 : Curso Unix, Universidad de Santiago, 30 horas",
            "Curso de 20 hrs. por Ágil Chile - Certificado por Certiprof",
            "Curso Python Universidad QA certificado 2026",
            "Curso de Arquitectura Cloud 2024",
            "2023 Curso de Python",
        ])
    )

    assert nombres == [
        "1999 : Curso Unix, Universidad de Santia",
        "Curso de 20 hrs. por Ágil Chile - Certif",
        "Curso Python Universidad QA certificado",
        "Curso de Arquitectura Cloud 2024",
        "2023 Curso de Python",
    ]


def test_cursos_detecta_certificacion_claramente_nombrada():
    nombres = _nombres(
        "\n".join([
            "Certificación AWS Solutions Architect 2024",
            "Licencias y certificaciones: Cisco IT",
            "2020 Certificado Scrum Master",
        ])
    )

    assert nombres == [
        "Certificación AWS Solutions Architect 20",
        "Licencias y certificaciones: Cisco IT",
        "2020 Certificado Scrum Master",
    ]


def test_cursos_no_detecta_recursos_como_curso():
    assert _derive_cursos("Administraba recursos técnicos del proyecto") == []


def test_cursos_ignora_cursos_dictados_o_impartidos_por_el_candidato():
    texto = "\n".join([
        "Curso de Angular - dictado por el candidato",
        "Curso de Python que impartió como docente",
        "Curso de JavaScript que enseñó como instructor",
        "Curso de Arquitectura Cloud, escribió y dictó curso de 20 horas",
    ])

    assert _derive_cursos(texto) == []


def test_cursos_conserva_formacion_obtenida_por_el_candidato():
    nombres = _nombres(
        "\n".join([
            "Curso de Angular Avanzado",
            "2023 Curso de Python",
            "Diplomado Gestión de Proyectos",
            "Certificación Azure Fundamentals 2024",
        ])
    )

    assert nombres == [
        "Curso de Angular Avanzado",
        "2023 Curso de Python",
        "Diplomado Gestión de Proyectos",
        "Certificación Azure Fundamentals 2024",
    ]
