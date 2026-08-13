from __future__ import annotations

import io
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


def _norm(text: str) -> str:
    return " ".join(text.replace("\x00", " ").split())


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise ValueError("Para leer DOCX instale python-docx") from exc
        document = Document(io.BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs)
    if suffix == ".txt":
        return content.decode("utf-8", errors="replace")
    raise ValueError("Formato no soportado. Use PDF, DOCX o TXT")


def parse_core(text: str) -> tuple[dict, list[str]]:
    """Extracción conservadora. No inventa datos ausentes en el CV."""
    clean = text.replace("\x00", " ")
    lines = [" ".join(x.split()) for x in clean.splitlines() if x.strip()]
    flat = "\n".join(lines)
    warnings: list[str] = []

    email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", flat, re.I)
    if not email_match:
        raise ValueError("No fue posible identificar un correo electrónico en el CV")
    email = email_match.group(0).lower()

    phone = None
    p = re.search(r"(?:\+?56\s*)?9[\s.-]*\d{4}[\s.-]*\d{4}", flat)
    if p:
        phone = re.sub(r"\D", "", p.group(0))[-9:]

    rut_num = dv = None
    r = re.search(r"\b(\d{7,8})[-\s]?([0-9Kk])\b", flat)
    if r:
        rut_num = int(r.group(1)); dv = 10 if r.group(2).upper() == "K" else int(r.group(2))

    urls = re.findall(r"(?:https?://|www\.)[^\s,;]+", flat, flags=re.I)
    social = [u.rstrip(".)]") for u in urls if "linkedin" in u.lower() or "github" in u.lower()]

    # Nombre: prioriza primeras líneas no-email/no-teléfono con 2-4 palabras alfabéticas.
    name_line = None
    for line in lines[:12]:
        if "@" in line or "linkedin" in line.lower() or "github" in line.lower():
            continue
        parts = line.split()
        if 2 <= len(parts) <= 4 and all(re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ'-]+", p) for p in parts):
            name_line = line; break
    if not name_line:
        local = email.split("@", 1)[0].replace(".", " ").replace("_", " ")
        parts = [p.capitalize() for p in local.split() if p]
        if len(parts) >= 2:
            name_line = " ".join(parts[:3])
            warnings.append("Nombre inferido desde la parte local del correo; revisar manualmente.")
        else:
            raise ValueError("No fue posible identificar nombres y apellido en el CV")

    parts = name_line.split()
    nombres = " ".join(parts[:-1])[:20] if len(parts) == 2 else " ".join(parts[:-2])[:20]
    apellido_paterno = parts[-1][:20] if len(parts) == 2 else parts[-2][:20]
    apellido_materno = None if len(parts) < 3 else parts[-1][:20]

    title = None
    for line in lines[:25]:
        low = line.casefold()
        if line == name_line or "@" in line or len(line) > 120:
            continue
        if any(k in low for k in ("ingenier", "desarrollador", "developer", "analista", "arquitect", "técnico", "tecnico", "scrum", "product", "devops", "data")):
            title = line[:300]; break

    summary = None
    for line in lines:
        if len(line) >= 70 and "@" not in line and not line.lower().startswith("http"):
            summary = line[:300]; break

    return {
        "cand_email": email,
        "cand_nombres": nombres,
        "cand_apellido_paterno": apellido_paterno,
        "cand_apellido_materno": apellido_materno,
        "cand_telefono": phone,
        "cand_rut_sin_dv": rut_num,
        "cand_dv": dv,
        "cand_resumen_profesional": summary,
        "cand_url_1": ";".join(dict.fromkeys(social)) or None,
        "cand_titulo": title,
    }, warnings
