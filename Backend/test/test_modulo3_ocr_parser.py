import io
from types import SimpleNamespace

import pytest

from app.candidatos import cv_parser
from app.candidatos.cv_parser import extract_text, parse_core


def _textual_pdf_bytes(text: str) -> bytes:
    reportlab = pytest.importorskip("reportlab.pdfgen.canvas")
    buffer = io.BytesIO()
    canvas = reportlab.Canvas(buffer)
    y = 720
    for line in text.splitlines():
        canvas.drawString(72, y, line)
        y -= 18
    canvas.save()
    return buffer.getvalue()


def test_pdf_normal_con_texto_suficiente_no_llama_ocr(monkeypatch):
    text = (
        "Catherine Rebolledo\n"
        "catherine@example.cl\n"
        "UX/UI Designer\n"
        "Texto suficientemente largo para pypdf y para evitar OCR."
    )
    content = _textual_pdf_bytes(text)

    def fail_ocr(_content):
        raise AssertionError("OCR no debe ejecutarse para PDF textual")

    monkeypatch.setattr(cv_parser, "_ocr_pdf_text", fail_ocr)

    extracted = extract_text("cv.pdf", content)

    assert "catherine@example.cl" in extracted


def test_pdf_sin_texto_llama_ocr(monkeypatch):
    calls = {"ocr": 0}
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: ["", ""])

    def fake_ocr(_content):
        calls["ocr"] += 1
        return "Catherine Rebolledo\ncatherine@example.cl\nTexto OCR suficientemente largo para continuar."

    monkeypatch.setattr(cv_parser, "_ocr_pdf_text", fake_ocr)

    assert "catherine@example.cl" in extract_text("cv.pdf", b"%PDF fake")
    assert calls["ocr"] == 1


def test_pdf_con_texto_insuficiente_llama_ocr(monkeypatch):
    calls = {"ocr": 0}
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: ["abc"])

    def fake_ocr(_content):
        calls["ocr"] += 1
        return "Catherine Rebolledo\ncatherine@example.cl\nTexto OCR suficiente para el parser actual."

    monkeypatch.setattr(cv_parser, "_ocr_pdf_text", fake_ocr)

    assert "catherine@example.cl" in extract_text("cv.pdf", b"%PDF fake")
    assert calls["ocr"] == 1


def test_ocr_devuelve_texto_suficiente(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (
            "Catherine Rebolledo\n"
            "catherine@example.cl\n"
            "Texto OCR suficiente para importar el curriculum con contenido legible y verificable."
        ),
    )

    assert "catherine@example.cl" in extract_text("cv.pdf", b"%PDF fake")


def test_ocr_devuelve_texto_insuficiente_error_controlado(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(cv_parser, "_ocr_pdf_text", lambda _content: "abc")

    with pytest.raises(ValueError, match="No fue posible extraer texto utilizable"):
        extract_text("cv.pdf", b"%PDF fake")


def test_ocr_requerido_pero_tesseract_no_disponible(monkeypatch):
    class FakePixmap:
        def tobytes(self, _format):
            return b"fake-image"

    class FakePage:
        def get_pixmap(self, **_kwargs):
            return FakePixmap()

    class FakeDocument:
        def __len__(self):
            return 1

        def load_page(self, _index):
            return FakePage()

    class FakeFitz:
        @staticmethod
        def open(**_kwargs):
            return FakeDocument()

        @staticmethod
        def Matrix(_x, _y):
            return object()

    class MissingTesseract(Exception):
        pass

    class FakePytesseract:
        TesseractNotFoundError = MissingTesseract

        @staticmethod
        def image_to_string(_path, lang):
            raise MissingTesseract("missing")

    monkeypatch.setattr(cv_parser, "_load_ocr_dependencies", lambda: (FakeFitz, FakePytesseract))

    with pytest.raises(ValueError, match="OCR no está disponible"):
        cv_parser._ocr_pdf_text(b"%PDF fake")


def test_pdf_corrupto_error_controlado(monkeypatch):
    def fail_pypdf(_content):
        raise ValueError("No fue posible leer el PDF. El archivo puede estar corrupto o no ser procesable.")

    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", fail_pypdf)

    with pytest.raises(ValueError, match="No fue posible leer el PDF"):
        extract_text("cv.pdf", b"not a pdf")


def test_texto_ocr_con_email_continua_por_parse_core(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (
            "Catherine Rebolledo\n"
            "UX/UI Designer\n"
            "catherine@example.cl\n"
            "RUT: 12.345.678-5\n"
            "Texto OCR suficiente para continuar usando parse_core sin reglas alternativas."
        ),
    )

    data, _warnings = parse_core(extract_text("cv.pdf", b"%PDF fake"))

    assert data["cand_email"] == "catherine@example.cl"
    assert data["cand_nombres"] == "Catherine"
    assert data["cand_rut_sin_dv"] == 12345678
    assert data["cand_titulo"] == "UX/UI Designer"


def test_texto_ocr_sin_email_mantiene_error_de_parser(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (
            "Catherine Rebolledo\n"
            "Texto OCR suficiente pero sin correo electronico declarado en el documento original."
        ),
    )

    with pytest.raises(ValueError, match="No fue posible identificar un correo electrónico"):
        parse_core(extract_text("cv.pdf", b"%PDF fake"))


def test_email_normal_se_detecta_sin_reparacion_ocr():
    data, _warnings = parse_core(
        "Catherine Rebolledo\n"
        "catherine@example.cl\n"
        "UX/UI Designer\n"
        "Texto suficiente para mantener el comportamiento normal del parser."
    )

    assert data["cand_email"] == "catherine@example.cl"


def test_email_ocr_repara_dominio_gmalicom(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (
            "Catherine Rebolledo\n"
            "Cathyrehopas@gmalicom\n"
            "UX/UI Designer\n"
            "Texto OCR suficiente para probar reparacion conservadora de dominio conocido."
        ),
    )

    data, _warnings = parse_core(extract_text("cv.pdf", b"%PDF fake"))

    assert data["cand_email"] == "cathyrehopas@gmail.com"


def test_email_ocr_no_inventa_dominio_desconocido(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (
            "Catherine Rebolledo\n"
            "catherine@dominiodeformado\n"
            "Texto OCR suficiente pero con dominio desconocido que no debe corregirse."
        ),
    )

    with pytest.raises(ValueError, match="No fue posible identificar un correo electrónico"):
        parse_core(extract_text("cv.pdf", b"%PDF fake"))


def test_email_ocr_conserva_local_part_deformado(monkeypatch):
    monkeypatch.setattr(cv_parser, "_extract_pdf_text_with_pypdf", lambda _content: [""])
    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (
            "Catherine Rebolledo\n"
            "Cathyrehopas@gmalicom\n"
            "Texto OCR suficiente para confirmar que no se adivina la parte personal."
        ),
    )

    data, _warnings = parse_core(extract_text("cv.pdf", b"%PDF fake"))

    assert data["cand_email"].split("@", 1)[0] == "cathyrehopas"


def test_email_deformado_en_texto_no_ocr_no_se_repara():
    with pytest.raises(ValueError, match="No fue posible identificar un correo electrónico"):
        parse_core(
            "Catherine Rebolledo\n"
            "cathyrehopas@gmalicom\n"
            "Texto PDF normal suficiente: no debe aplicar reparacion OCR."
        )


def test_txt_mantiene_comportamiento_actual():
    content = "Catherine Rebolledo\ncatherine@example.cl".encode()

    assert extract_text("cv.txt", content) == "Catherine Rebolledo\ncatherine@example.cl"


def test_docx_mantiene_comportamiento_actual():
    docx = pytest.importorskip("docx")
    document = docx.Document()
    document.add_paragraph("Catherine Rebolledo")
    document.add_paragraph("catherine@example.cl")
    buffer = io.BytesIO()
    document.save(buffer)

    assert "catherine@example.cl" in extract_text("cv.docx", buffer.getvalue())


def test_pdf_textual_regresion_utiliza_pypdf(monkeypatch):
    content = _textual_pdf_bytes(
        "Pablo Palma\n"
        "Desarrollador Full Stack\n"
        "pablo@example.cl\n"
        "Texto suficiente para mantener pypdf como camino principal."
    )

    monkeypatch.setattr(
        cv_parser,
        "_ocr_pdf_text",
        lambda _content: (_ for _ in ()).throw(AssertionError("OCR no debe ejecutarse")),
    )

    data, _warnings = parse_core(extract_text("cv.pdf", content))

    assert data["cand_email"] == "pablo@example.cl"
    assert data["cand_titulo"] == "Desarrollador Full Stack"
