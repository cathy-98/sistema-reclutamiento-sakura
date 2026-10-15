from __future__ import annotations

import html
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAND_ORANGE = "E97824"
TEXT = "4A4A4A"
LIGHT = "F3F3F3"
GRID = "D9D9D9"
GREEN = "C6EFCE"
YELLOW = "FFEB9C"
RED = "FFC7CE"
GRAY = "D9E2F3"

LEVEL_FILLS = {
    "avanzado": GREEN,
    "medio": "F4B183",
    "basico": YELLOW,
    "basico/a": YELLOW,
    "básico": YELLOW,
    "nada": RED,
}


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _norm(value: Any) -> str:
    return _esc(value).lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")


def _level_fill(level: str | None) -> str:
    return LEVEL_FILLS.get(_norm(level), GRAY)


def _run(text: Any, *, bold: bool = False, color: str = TEXT, size: int = 20) -> str:
    props = [f'<w:color w:val="{color}"/>', f'<w:sz w:val="{size}"/>', f'<w:szCs w:val="{size}"/>']
    if bold:
        props.insert(0, "<w:b/>")
    body = []
    parts = str("" if text is None else text).split("\n")
    for index, part in enumerate(parts):
        if index:
            body.append("<w:br/>")
        body.append(f'<w:t xml:space="preserve">{_esc(part)}</w:t>')
    return f"<w:r><w:rPr>{''.join(props)}</w:rPr>{''.join(body)}</w:r>"


def _p(*runs: str, align: str | None = None, before: int = 0, after: int = 120) -> str:
    jc = f'<w:jc w:val="{align}"/>' if align else ""
    return f'<w:p><w:pPr><w:spacing w:before="{before}" w:after="{after}" w:line="264" w:lineRule="auto"/>{jc}</w:pPr>{"".join(runs)}</w:p>'


def _cell(paragraphs: list[str], width: int, *, fill: str | None = None) -> str:
    shade = f'<w:shd w:fill="{fill}"/>' if fill else ""
    margins = (
        '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:start w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:end w:w="120" w:type="dxa"/></w:tcMar>'
    )
    return f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:vAlign w:val="top"/>{shade}{margins}</w:tcPr>{"".join(paragraphs)}</w:tc>'


def _table(rows: list[list[dict[str, Any]]], widths: list[int], *, header_rows: int = 0) -> str:
    total = sum(widths)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    body = []
    for row_index, row in enumerate(rows):
        header = "<w:trPr><w:tblHeader/></w:trPr>" if row_index < header_rows else ""
        cells = [
            _cell(cell["paragraphs"], widths[index], fill=cell.get("fill"))
            for index, cell in enumerate(row)
        ]
        body.append(f"<w:tr>{header}{''.join(cells)}</w:tr>")
    borders = "".join(
        f'<w:{name} w:val="single" w:sz="4" w:space="0" w:color="{GRID}"/>'
        for name in ("top", "left", "bottom", "right", "insideH", "insideV")
    )
    return (
        f'<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="{total}" w:type="dxa"/>'
        f'<w:tblInd w:w="120" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders>{borders}</w:tblBorders></w:tblPr>'
        f"<w:tblGrid>{grid}</w:tblGrid>{''.join(body)}</w:tbl>"
    )


def _field_cell(label: str, value: Any, label_width: int, value_width: int) -> list[dict[str, Any]]:
    return [
        {"fill": LIGHT, "paragraphs": [_p(_run(label, bold=True, size=18))]},
        {"paragraphs": [_p(_run(value or "-", size=18))]},
    ]


def _candidate_identity(index: int, candidate: dict[str, Any]) -> str:
    lines = [f"{index}. {candidate.get('nombre') or '-'}", candidate.get("correo") or "-"]
    rent = candidate.get("pretension_renta")
    lines.append(f"Pretensión: {rent:,}".replace(",", ".") if rent is not None else "Pretensión: No informada")
    lines.append(f"Disponibilidad: {candidate.get('disponibilidad') or 'No informada'}")
    return "\n".join(lines)


def _tech_paragraphs(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return [_p(_run("Sin tecnologías requeridas", color="777777", size=18))]
    paragraphs = []
    for item in items:
        level = item.get("nivel_candidato") or "No informado"
        paragraphs.append(
            _p(
                _run(item.get("habilidad") or "-", size=18),
                _run("  \u25ac", bold=True, color=_level_fill(level), size=24),
                _run(f" {level}", size=16, color="666666"),
                after=60,
            )
        )
    return paragraphs


def _document_xml(data: dict[str, Any]) -> str:
    solicitud = data.get("solicitud") or {}
    candidates = data.get("candidatos") or []
    parts = [
        _p(_run("INFORME DE CANDIDATOS", bold=True, color=BRAND_ORANGE, size=40), after=40),
        _p(_run("Resumen comparativo para revisión y selección", color=TEXT, size=20), after=180),
    ]
    info_widths = [1500, 3100, 1300, 3000, 1200, 3820]
    info_rows = [
        _field_cell("Cargo", solicitud.get("cargo"), 1500, 3100)
        + _field_cell("Empresa", solicitud.get("empresa"), 1300, 3000)
        + _field_cell("Vacantes", solicitud.get("vacantes"), 1200, 3820),
        _field_cell("Solicitud", solicitud.get("codigo") or solicitud.get("solicitud_id"), 1500, 3100)
        + _field_cell("Área", solicitud.get("area"), 1300, 3000)
        + _field_cell("Modalidad", solicitud.get("modalidad"), 1200, 3820),
    ]
    parts.append(_table(info_rows, info_widths))
    parts.append(_p(_run("Nivel tecnológico", bold=True, color=BRAND_ORANGE, size=22), before=180, after=80))
    legend_rows = [[
        {"fill": GREEN, "paragraphs": [_p(_run("Avanzado", bold=True, size=18), align="center")]},
        {"fill": "F4B183", "paragraphs": [_p(_run("Medio", bold=True, size=18), align="center")]},
        {"fill": YELLOW, "paragraphs": [_p(_run("Básico", bold=True, size=18), align="center")]},
        {"fill": RED, "paragraphs": [_p(_run("Nada", bold=True, size=18), align="center")]},
    ]]
    parts.append(_table(legend_rows, [1600, 1600, 1600, 1600]))
    parts.append(_p(_run("CANDIDATOS SELECCIONADOS", bold=True, color=BRAND_ORANGE, size=22), before=220, after=80))

    table_widths = [2300, 2950, 2950, 2850, 2870]
    header = [
        {"fill": BRAND_ORANGE, "paragraphs": [_p(_run(text, bold=True, color="FFFFFF", size=18), align="center")]}
        for text in ("Candidato", "Observación operacional", "Observación técnica", "Tecnologías excluyentes", "Tecnologías no excluyentes")
    ]
    rows = [header]
    for index, candidate in enumerate(candidates, start=1):
        rows.append([
            {"paragraphs": [_p(_run(_candidate_identity(index, candidate), size=18))]},
            {"paragraphs": [_p(_run(candidate.get("observacion_operacional") or "Sin observaciones registradas", size=18))]},
            {"paragraphs": [_p(_run(candidate.get("observacion_tecnica") or "Sin observaciones registradas", size=18))]},
            {"paragraphs": _tech_paragraphs(candidate.get("tecnologias_excluyentes") or [])},
            {"paragraphs": _tech_paragraphs(candidate.get("tecnologias_no_excluyentes") or [])},
        ])
    if len(rows) == 1:
        rows.append([
            {"paragraphs": [_p(_run("Sin candidatos seleccionados", size=18))]},
            {"paragraphs": [_p(_run("-", size=18))]},
            {"paragraphs": [_p(_run("-", size=18))]},
            {"paragraphs": [_p(_run("-", size=18))]},
            {"paragraphs": [_p(_run("-", size=18))]},
        ])
    parts.append(_table(rows, table_widths, header_rows=1))
    sect = (
        '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
        '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="708"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w10="urn:schemas-microsoft-com:office:word" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
        'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
        'mc:Ignorable="w14 wp14"><w:body>'
        + "".join(parts)
        + sect
        + "</w:body></w:document>"
    )


def _styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="22"/></w:rPr>'
        '</w:style><w:style w:type="table" w:default="1" w:styleId="TableGrid"><w:name w:val="Table Grid"/></w:style>'
        '</w:styles>'
    )


def generate_comparative_docx(path: str, data: dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
        '</Relationships>'
    )
    settings = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:zoom w:percent="100"/><w:defaultTabStop w:val="720"/></w:settings>'
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Informe Comparativo de Candidatos</dc:title><dc:creator>Sakura Reclutamiento</dc:creator>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'
    )
    app = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>Sakura Reclutamiento</Application></Properties>'
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", content_types)
        package.writestr("_rels/.rels", rels)
        package.writestr("word/_rels/document.xml.rels", doc_rels)
        package.writestr("word/document.xml", _document_xml(data))
        package.writestr("word/styles.xml", _styles_xml())
        package.writestr("word/settings.xml", settings)
        package.writestr("docProps/core.xml", core)
        package.writestr("docProps/app.xml", app)
