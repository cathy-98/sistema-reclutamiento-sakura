import pytest

from app.candidatos.cv_parser import (
    candidate_language_lines,
    detect_language_level_code,
    fold_text,
    language_aliases,
)


@pytest.mark.parametrize(
    "texto,codigo",
    [
        ("Inglés C1", "C1"),
        ("English C1", "C1"),
        ("Español Nativo", "NAT"),
        ("Spanish Native", "NAT"),
        ("English Advanced", "AVA"),
        ("Inglés Avanzado", "AVA"),
        ("Portugués B2", "B2"),
        ("Francés Intermedio", "INT"),
        ("German C2", "C2"),
        ("English A2", "A2"),
        ("Inglés Básico", "BAS"),
        ("English Basic", "BAS"),
    ],
)
def test_detect_language_level_code(texto, codigo):
    assert detect_language_level_code(texto) == codigo


@pytest.mark.parametrize(
    "texto",
    [
        "Inglés",
        "English",
        "Idiomas",
        "Languages",
        "Portugués",
    ],
)
def test_detect_language_level_code_no_inventa_nivel(texto):
    assert detect_language_level_code(texto) is None


def test_cefr_explicito_tiene_prioridad_sobre_texto_generico():
    assert detect_language_level_code("English advanced C2") == "C2"
    assert detect_language_level_code("Inglés intermedio B2") == "B2"


@pytest.mark.parametrize(
    "catalogo,alias_esperado",
    [
        ("Inglés", "english"),
        ("Español", "spanish"),
        ("Español", "castellano"),
        ("Portugués", "portuguese"),
        ("Francés", "french"),
        ("Alemán", "german"),
        ("Italiano", "italian"),
        ("Mandarín", "mandarin"),
    ],
)
def test_language_aliases_incluye_variantes(catalogo, alias_esperado):
    aliases = language_aliases(catalogo)
    assert alias_esperado in aliases


def test_language_aliases_incluye_nombre_catalogo_normalizado():
    aliases = language_aliases("Inglés")
    assert "ingles" in aliases


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("INGLÉS", "ingles"),
        ("  Inglés   Avanzado  ", "ingles avanzado"),
        ("Español", "espanol"),
        ("PORTUGUÉS", "portugues"),
        ("Francés", "frances"),
        ("Alemán", "aleman"),
    ],
)
def test_fold_text_normaliza_acentos_mayusculas_y_espacios(entrada, esperado):
    assert fold_text(entrada) == esperado


def test_candidate_language_lines_limpia_lineas():
    texto = """
    IDIOMAS

       Inglés     C1

    Español    Nativo
    """
    assert candidate_language_lines(texto) == [
        "IDIOMAS",
        "Inglés C1",
        "Español Nativo",
    ]


def test_candidate_language_lines_vacio():
    assert candidate_language_lines("") == []
    assert candidate_language_lines(None) == []


def test_aliases_no_duplican_nombre_normalizado():
    aliases = language_aliases("English")
    assert len(aliases) == len(set(aliases))


def test_nivel_fluid_se_normaliza_avanzado_generico():
    assert detect_language_level_code("English Fluent") == "AVA"


def test_native_speaker_se_normaliza_nativo():
    assert detect_language_level_code("English Native Speaker") == "NAT"


def test_mother_tongue_se_normaliza_nativo():
    assert detect_language_level_code("English Mother Tongue") == "NAT"
