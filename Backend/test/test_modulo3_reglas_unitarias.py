from app.candidatos.cv_parser import parse_core
from app.candidatos.schemas import CandidatoUpdate, normalize_semicolon_values


def test_urls_separadas_por_punto_y_coma_se_normalizan_y_deduplican():
    assert normalize_semicolon_values(" a.pdf ; b.pdf;;a.pdf ") == "a.pdf;b.pdf"


def test_dv_k_se_normaliza_a_10():
    assert CandidatoUpdate(cand_dv="K").cand_dv == 10


def test_parser_cv_extrae_correo_y_datos_basicos():
    text = """
    Ana Perez Soto
    Ingeniera en Informatica
    ana.perez@example.cl
    +56 9 1234 5678
    12345678-K
    https://www.linkedin.com/in/anaperez
    Profesional con más de ocho años de experiencia en desarrollo de software y gestión de proyectos tecnológicos.
    """
    data, warnings = parse_core(text)
    assert data["cand_email"] == "ana.perez@example.cl"
    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_dv"] == 10
    assert "linkedin" in (data["cand_url_1"] or "")
