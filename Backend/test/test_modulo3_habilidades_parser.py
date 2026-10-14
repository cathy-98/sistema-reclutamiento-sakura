from types import SimpleNamespace

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
    def __init__(self, *, habilidades=None, niveles_habilidad=None):
        self._values_by_model = {
            Empresa: [],
            Cargo: [],
            NivelHabilidad: niveles_habilidad or [],
            Habilidad: habilidades or [],
            Institucion: [],
            Carrera: [],
            NivelEducacional: [],
            NivelIdioma: [],
            Idioma: [],
        }

    def scalars(self, statement):
        model = statement.column_descriptions[0]["entity"]
        return _ScalarResult(self._values_by_model.get(model, []))


def _habilidad(item_id: int, nombre: str):
    return SimpleNamespace(hab_id=item_id, hab_nombre=nombre)


def _nivel(item_id: int, nombre: str):
    return SimpleNamespace(nvhb_id=item_id, nvhb_nombre=nombre)


def _derive_habilidades(texto: str, *, habilidades, niveles_habilidad=None):
    nested, _warnings = services.derive_nested_from_cv(
        _FakeDb(habilidades=habilidades, niveles_habilidad=niveles_habilidad),
        texto,
    )
    return nested["habilidades"]


def _by_skill_id(payload):
    return {item["cdhb_habilidad_id"]: item for item in payload}


def test_detecta_habilidad_python_por_coincidencia_exacta():
    habilidades = _derive_habilidades("Habilidades\nPython", habilidades=[_habilidad(10, "Python")])

    assert _by_skill_id(habilidades)[10]["cdhb_anios_experiencia"] is None


def test_detecta_habilidad_python_ignorando_mayusculas():
    habilidades = _derive_habilidades("Habilidades\nPYTHON", habilidades=[_habilidad(10, "Python")])

    assert _by_skill_id(habilidades)[10]["cdhb_habilidad_id"] == 10


def test_detecta_habilidad_javascript_con_variante_de_mayusculas():
    habilidades = _derive_habilidades(
        "Stack: Javascript",
        habilidades=[_habilidad(10, "JavaScript")],
    )

    assert _by_skill_id(habilidades)[10]["cdhb_habilidad_id"] == 10


def test_no_detecta_go_dentro_de_palabra_mas_larga():
    habilidades = _derive_habilidades(
        "Experiencia en Golang y Django",
        habilidades=[_habilidad(10, "Go")],
    )

    assert habilidades == []


def test_detecta_go_como_token_independiente():
    habilidades = _derive_habilidades("Stack: Go / Python", habilidades=[_habilidad(10, "Go")])

    assert _by_skill_id(habilidades)[10]["cdhb_habilidad_id"] == 10


def test_no_detecta_r_dentro_de_palabra_mas_larga():
    habilidades = _derive_habilidades(
        "Experiencia en retail y reporting",
        habilidades=[_habilidad(10, "R")],
    )

    assert habilidades == []


def test_detecta_r_como_token_independiente():
    habilidades = _derive_habilidades("Herramientas: R, SQL", habilidades=[_habilidad(10, "R")])

    assert _by_skill_id(habilidades)[10]["cdhb_habilidad_id"] == 10


def test_no_detecta_c_dentro_de_palabra_mas_larga():
    habilidades = _derive_habilidades(
        "Contacto: candidato@example.com",
        habilidades=[_habilidad(10, "C")],
    )

    assert habilidades == []


def test_detecta_c_como_token_independiente():
    habilidades = _derive_habilidades("Lenguajes: C / Python", habilidades=[_habilidad(10, "C")])

    assert _by_skill_id(habilidades)[10]["cdhb_habilidad_id"] == 10


def test_detecta_habilidad_con_puntuacion_y_separadores_equivalentes():
    habilidades = _derive_habilidades(
        "Stack principal: Node js",
        habilidades=[_habilidad(10, "Node.js")],
    )

    assert _by_skill_id(habilidades)[10]["cdhb_habilidad_id"] == 10


def test_extrae_anios_despues_de_la_habilidad_en_misma_linea():
    habilidades = _derive_habilidades(
        "Habilidades: Python - 5 años",
        habilidades=[_habilidad(10, "Python")],
    )

    assert _by_skill_id(habilidades)[10]["cdhb_anios_experiencia"] == 5


def test_extrae_anios_antes_de_la_habilidad_en_misma_linea():
    habilidades = _derive_habilidades(
        "5 años de experiencia en Python",
        habilidades=[_habilidad(10, "Python")],
    )

    assert _by_skill_id(habilidades)[10]["cdhb_anios_experiencia"] == 5


def test_habilidad_sin_anios_explicitos_mantiene_null():
    habilidades = _derive_habilidades(
        "Habilidades: Python",
        habilidades=[_habilidad(10, "Python")],
    )

    assert _by_skill_id(habilidades)[10]["cdhb_anios_experiencia"] is None


def test_no_asocia_numero_cercano_si_no_expresa_anios_de_habilidad():
    habilidades = _derive_habilidades(
        "Python proyectos 2024 equipo de 5 personas",
        habilidades=[_habilidad(10, "Python")],
    )

    assert _by_skill_id(habilidades)[10]["cdhb_anios_experiencia"] is None


def test_dos_habilidades_cercanas_reciben_anios_distintos():
    habilidades = _derive_habilidades(
        "Python - 5 años; Java - 3 años",
        habilidades=[_habilidad(10, "Python"), _habilidad(20, "Java")],
    )

    by_id = _by_skill_id(habilidades)
    assert by_id[10]["cdhb_anios_experiencia"] == 5
    assert by_id[20]["cdhb_anios_experiencia"] == 3


def test_coincidencia_ambigua_no_elije_habilidad_arbitrariamente():
    habilidades = _derive_habilidades(
        "Habilidades: Java Script",
        habilidades=[_habilidad(10, "Java"), _habilidad(20, "Java Script")],
    )

    assert habilidades == []


def test_integracion_liviana_derive_nested_confirma_id_anios_y_nivel():
    habilidades = _derive_habilidades(
        "Habilidades\nPython - 5 años avanzado",
        habilidades=[_habilidad(10, "Python")],
        niveles_habilidad=[_nivel(30, "Avanzado")],
    )

    assert habilidades == [
        {
            "cdhb_habilidad_id": 10,
            "cdhb_nivel_habilidad_id": 30,
            "cdhb_anios_experiencia": 5,
        }
    ]
