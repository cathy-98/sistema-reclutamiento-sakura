from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND_ORANGE = colors.HexColor("#E97824")
TEXT = colors.HexColor("#4A4A4A")
LIGHT = colors.HexColor("#F3F3F3")
GREEN = colors.HexColor("#C6EFCE")
YELLOW = colors.HexColor("#FFEB9C")
RED = colors.HexColor("#FFC7CE")
ORANGE_FILL = colors.HexColor("#F4B183")
BLUE_GRAY = colors.HexColor("#D9E2F3")


def _styles():
    s = getSampleStyleSheet()
    return {
        "brand": ParagraphStyle("brand", parent=s["Title"], fontName="Helvetica-Bold", fontSize=24, textColor=BRAND_ORANGE, leading=26),
        "name": ParagraphStyle("name", parent=s["Heading1"], fontName="Helvetica-Bold", fontSize=16, textColor=TEXT, spaceAfter=3),
        "subtitle": ParagraphStyle("subtitle", parent=s["Normal"], fontSize=10, textColor=TEXT, spaceAfter=10),
        "section": ParagraphStyle("section", parent=s["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=BRAND_ORANGE, spaceBefore=8, spaceAfter=6),
        "body": ParagraphStyle("body", parent=s["BodyText"], fontSize=9, leading=12, textColor=TEXT, spaceAfter=5),
        "body_bold": ParagraphStyle("body_bold", parent=s["BodyText"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=TEXT, spaceAfter=3),
        "small": ParagraphStyle("small", parent=s["BodyText"], fontSize=8, leading=10, textColor=TEXT),
        "center": ParagraphStyle("center", parent=s["BodyText"], fontSize=9, leading=11, alignment=TA_CENTER, textColor=TEXT),
    }


def _header(canvas, doc):
    canvas.saveState()
    logo = (os.getenv("REPORTS_LOGO_PATH") or "").strip()
    if logo and Path(logo).is_file():
        try:
            canvas.drawImage(logo, 16 * mm, A4[1] - 28 * mm, width=36 * mm, height=14 * mm, preserveAspectRatio=True, mask="auto")
        except Exception:
            canvas.setFillColor(BRAND_ORANGE)
            canvas.setFont("Helvetica-Bold", 20)
            canvas.drawString(16 * mm, A4[1] - 20 * mm, "ELITSOFT")
    else:
        canvas.setFillColor(BRAND_ORANGE)
        canvas.setFont("Helvetica-Bold", 20)
        canvas.drawString(16 * mm, A4[1] - 20 * mm, "ELITSOFT")
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(A4[0] - 15 * mm, 9 * mm, f"Página {doc.page}")
    canvas.restoreState()


def _doc(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=31 * mm,
        bottomMargin=16 * mm,
        title="ELITSOFT",
        author="Sakura Reclutamiento",
    )


def _p(text: Any, style):
    value = "" if text is None else str(text)
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    return Paragraph(value, style)


def _pm(markup: str, style):
    return Paragraph(markup, style)


def _level_color(level: str | None):
    normalized = _normalize_level(level)
    if normalized == "avanzado":
        return GREEN
    if normalized == "medio":
        return ORANGE_FILL
    if normalized == "basico":
        return YELLOW
    if normalized == "nada":
        return RED
    return BLUE_GRAY


def _normalize_level(level: str | None) -> str:
    value = "" if level is None else str(level).strip().casefold()
    return (
        value.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def _money(value: Any) -> str:
    if value is None:
        return "No informada"
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(value)


def _candidate_identity(index: int, candidate: dict[str, Any]) -> str:
    return "\n".join([
        f"{index}. {candidate.get('nombre') or '-'}",
        candidate.get("correo") or "-",
        f"Pretensión: {_money(candidate.get('pretension_renta'))}",
        f"Disponibilidad: {candidate.get('disponibilidad') or 'No informada'}",
    ])


def _tech_cell(items: list[dict[str, Any]], style) -> Paragraph:
    if not items:
        return _p("Sin tecnologías requeridas", style)
    lines = []
    for item in items:
        level = item.get("nivel_candidato") or "No informado"
        color = _level_color(level).hexval()
        skill = str(item.get("habilidad") or "-").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        label = str(level).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f'{skill} <font color="#{color}">▬</font> <font color="#666666">{label}</font>')
    return _pm("<br/>".join(lines), style)


def _comparative_doc(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return SimpleDocTemplate(
        path,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Informe Comparativo de Candidatos",
        author="Sakura Reclutamiento",
    )


def _comparative_header(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(287 * mm, 7 * mm, f"Página {doc.page}")
    canvas.restoreState()


def generate_comparative_report_pdf(path: str, data: dict[str, Any]) -> None:
    st = _styles()
    story = [
        _p("INFORME DE CANDIDATOS", st["brand"]),
        _p("Resumen comparativo para revisión y selección", st["subtitle"]),
    ]
    solicitud = data.get("solicitud") or {}
    info = [
        ["Cargo", solicitud.get("cargo") or "-", "Empresa", solicitud.get("empresa") or "-", "Vacantes", solicitud.get("vacantes") or "-"],
        ["Solicitud", solicitud.get("codigo") or solicitud.get("solicitud_id") or "-", "Área", solicitud.get("area") or "-", "Modalidad", solicitud.get("modalidad") or "-"],
    ]
    info_table = Table(
        [[_p(x, st["small"]) for x in row] for row in info],
        colWidths=[23 * mm, 46 * mm, 23 * mm, 51 * mm, 23 * mm, 91 * mm],
    )
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT),
        ("BACKGROUND", (4, 0), (4, -1), LIGHT),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [info_table, Spacer(1, 4 * mm), _p("Nivel tecnológico", st["section"])]
    legend = Table(
        [["Avanzado", "Medio", "Básico", "Nada"]],
        colWidths=[28 * mm, 28 * mm, 28 * mm, 28 * mm],
    )
    legend.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), GREEN),
        ("BACKGROUND", (1, 0), (1, 0), ORANGE_FILL),
        ("BACKGROUND", (2, 0), (2, 0), YELLOW),
        ("BACKGROUND", (3, 0), (3, 0), RED),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [legend, Spacer(1, 4 * mm), _p("CANDIDATOS SELECCIONADOS", st["section"])]

    headers = ["Candidato", "Observación operacional", "Observación técnica", "Tecnologías excluyentes", "Tecnologías no excluyentes"]
    rows = [[_p(x, st["small"]) for x in headers]]
    for index, candidate in enumerate(data.get("candidatos") or [], start=1):
        rows.append([
            _p(_candidate_identity(index, candidate), st["small"]),
            _p(candidate.get("observacion_operacional") or "Sin observaciones registradas", st["small"]),
            _p(candidate.get("observacion_tecnica") or "Sin observaciones registradas", st["small"]),
            _tech_cell(candidate.get("tecnologias_excluyentes") or [], st["small"]),
            _tech_cell(candidate.get("tecnologias_no_excluyentes") or [], st["small"]),
        ])
    if len(rows) == 1:
        rows.append([_p("Sin candidatos seleccionados", st["small"]), _p("-", st["small"]), _p("-", st["small"]), _p("-", st["small"]), _p("-", st["small"])])
    table = Table(rows, colWidths=[42 * mm, 54 * mm, 54 * mm, 53 * mm, 54 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_ORANGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    _comparative_doc(path).build(story, onFirstPage=_comparative_header, onLaterPages=_comparative_header)


def generate_corporate_cv(path: str, data: dict[str, Any]) -> None:
    st = _styles()
    story = [Spacer(1, 2 * mm)]
    story.append(_p(data.get("nombre"), st["name"]))
    subtitle = " · ".join(x for x in [data.get("titulo"), data.get("pais")] if x)
    story.append(_p(subtitle, st["subtitle"]))

    story += [_p("I INFORMACIÓN ACADÉMICA", st["section"])]
    studies = data.get("educacion") or []
    if studies:
        for x in studies:
            title = x.get("carrera") or x.get("nivel") or "Estudio"
            dates = x.get("periodo") or ""
            story.append(_p(f"{title}{' - ' + dates if dates else ''}", st["body_bold"]))
            if x.get("institucion"):
                story.append(_p(x["institucion"], st["small"]))
    else:
        story.append(_p("Información académica no informada.", st["body"]))

    story += [_p("II PERFIL PROFESIONAL", st["section"]), _p(data.get("perfil_profesional") or "Perfil profesional no informado.", st["body"])]

    story.append(_p("III EXPERIENCIA LABORAL", st["section"]))
    experiences = data.get("experiencia") or []
    if experiences:
        for x in experiences:
            parts = [x.get("cargo") or "Cargo", x.get("empresa") or ""]
            story.append(_p(parts[0], st["body_bold"]))
            line = " - ".join(v for v in [parts[1], x.get("periodo")] if v)
            if line:
                story.append(_p(line, st["small"]))
            if x.get("descripcion"):
                story.append(_p(x["descripcion"], st["body"]))
            story.append(Spacer(1, 2 * mm))
    else:
        story.append(_p("Experiencia laboral no informada.", st["body"]))

    story.append(_p("IV CONOCIMIENTOS TÉCNICOS ESPECÍFICOS", st["section"]))
    rows = [[_p("Categoría", st["small"]), _p("Habilidades", st["small"]), _p("Nivel", st["small"])]]
    grouped = data.get("habilidades_por_categoria") or {}
    if grouped:
        for category, skills in grouped.items():
            names = "<br/>".join(f"• {x.get('habilidad')}" for x in skills)
            levels = "<br/>".join(f"• {x.get('nivel') or 'No informado'}" for x in skills)
            rows.append([_p(category, st["small"]), _p(names, st["small"]), _p(levels, st["small"])])
    else:
        rows.append([_p("Otros", st["small"]), _p("No informado", st["small"]), _p("-", st["small"])])
    table = Table(rows, colWidths=[45 * mm, 85 * mm, 35 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_ORANGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    story.append(_p("V IDIOMAS", st["section"]))
    languages = data.get("idiomas") or []
    story.append(_p("<br/>".join(f"• {x['idioma']} ({x['nivel']})" for x in languages) if languages else "Idiomas no informados.", st["body"]))

    story.append(_p("VI CERTIFICACIONES", st["section"]))
    certs = data.get("certificaciones") or []
    story.append(_p("<br/>".join(f"• {x['nombre']}{' (' + str(x['anio']) + ')' if x.get('anio') else ''}" for x in certs) if certs else "Certificaciones no informadas.", st["body"]))

    story.append(_p("RESUMEN EJECUTIVO", st["section"]))
    story.append(_p(data.get("resumen_ejecutivo") or data.get("perfil_profesional") or "No informado.", st["body"]))

    story.append(_p("ROLES RECOMENDADOS", st["section"]))
    roles = data.get("roles_recomendados") or []
    story.append(_p("<br/>".join(f"{i}. {x}" for i, x in enumerate(roles, 1)) if roles else "No informado.", st["body"]))

    story.append(_p("FORTALEZAS CLAVE", st["section"]))
    strengths = data.get("fortalezas") or []
    story.append(_p("<br/>".join(f"• {x}" for x in strengths) if strengths else "No informado.", st["body"]))

    _doc(path).build(story, onFirstPage=_header, onLaterPages=_header)


def _traffic(percent: float | None):
    if percent is None:
        return colors.white
    if percent >= float(os.getenv("REPORTS_GREEN_THRESHOLD", "80")):
        return GREEN
    if percent >= float(os.getenv("REPORTS_YELLOW_THRESHOLD", "60")):
        return YELLOW
    return RED


def generate_candidate_summary(path: str, data: dict[str, Any]) -> None:
    st = _styles()
    story = [
        _p("RESUMEN DE CANDIDATO", st["section"]),
        _p(data.get("candidato_nombre"), st["name"]),
        _p(" · ".join(x for x in [data.get("cargo"), data.get("solicitud_codigo")] if x), st["subtitle"]),
    ]
    general = [
        ["Solicitud", data.get("solicitud_codigo") or "-"],
        ["Cargo", data.get("cargo") or "-"],
        ["Disponibilidad", data.get("disponibilidad") or "-"],
        ["% Match", f"{data.get('match'):.2f}%" if data.get("match") is not None else "-"],
        ["Estado", data.get("estado_postulacion") or "-"],
        ["Clasificación M6", data.get("clasificacion") or "-"],
    ]
    gt = Table(general, colWidths=[45 * mm, 115 * mm])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [gt, Spacer(1, 4 * mm), _p("EVALUACIONES TÉCNICAS", st["section"])]

    tech_rows = [["Evaluación", "Resultado", "Estado"]]
    for x in data.get("tecnicas") or []:
        pct = x.get("porcentaje")
        tech_rows.append([x.get("cuestionario") or "-", f"{pct:.2f}%" if pct is not None else "-", "Aprobado" if x.get("aprobado") is True else ("No Aprobado" if x.get("aprobado") is False else x.get("estado") or "Pendiente")])
    if len(tech_rows) == 1:
        tech_rows.append(["Sin evaluaciones", "-", "-"])
    tt = Table(tech_rows, colWidths=[80 * mm, 35 * mm, 45 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_ORANGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]
    for idx, x in enumerate(data.get("tecnicas") or [], start=1):
        style.append(("BACKGROUND", (1, idx), (1, idx), _traffic(x.get("porcentaje"))))
    tt.setStyle(TableStyle(style))
    story.append(tt)

    story += [Spacer(1, 4 * mm), _p("ENTREVISTAS", st["section"])]
    interview_rows = [["Tipo", "Entrevistador", "Resultado"]]
    for x in data.get("entrevistas") or []:
        interview_rows.append([x.get("tipo") or "-", x.get("entrevistador") or "-", x.get("resultado") or "-"])
    if len(interview_rows) == 1:
        interview_rows.append(["Sin evaluaciones", "-", "-"])
    it = Table(interview_rows, colWidths=[55 * mm, 65 * mm, 40 * mm], repeatRows=1)
    it.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_ORANGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(it)

    reasons = data.get("motivo_clasificacion") or []
    story += [Spacer(1, 4 * mm), _p("SÍNTESIS", st["section"])]
    story.append(_p("<br/>".join(f"• {x}" for x in reasons) if reasons else "Sin observaciones de clasificación.", st["body"]))
    _doc(path).build(story, onFirstPage=_header, onLaterPages=_header)
