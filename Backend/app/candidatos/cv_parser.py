from __future__ import annotations

import io
import os
import re
import tempfile
import unicodedata
from pathlib import Path

from pypdf import PdfReader


def _norm(text: str) -> str:
    return " ".join(text.replace("\x00", " ").split())


_TITLE_KEYWORDS = (
    "ingenier",
    "desarrollador",
    "developer",
    "analista",
    "arquitect",
    "técnico",
    "tecnico",
    "scrum",
    "product",
    "devops",
    "data",
    "designer",
)

_SECTION_HEADERS = {
    "contacto",
    "educacion",
    "estudios",
    "experiencia",
    "experiencia laboral",
    "formacion",
    "habilidades",
    "perfil",
    "perfil profesional",
    "resumen",
    "resumen profesional",
    "skills",
}

_SECTION_PREFIXES = (
    "educacion",
    "estudios",
    "experiencia",
    "formacion",
    "habilidades",
    "perfil",
    "resumen",
    "skills",
)

_ACADEMIC_TITLE_HEADERS = {
    "academic background",
    "educacion superior",
    "education",
    "formacion academica",
}

_NAME_DOCUMENT_HEADERS = {
    "curriculum",
    "curriculum vitae",
    "datos personales",
    "hoja de vida",
    "informacion personal",
    "perfil profesional",
    "resume",
}

_NAME_INSTITUTION_WORDS = {
    "academia",
    "college",
    "escuela",
    "instituto",
    "school",
    "universidad",
}

_NAME_LOCATION_SIGNALS = {"chile", "rm"}

_NAME_NON_PERSON_WORDS = {
    "aleman",
    "espanol",
    "frances",
    "idiomas",
    "ingles",
    "italiano",
    "languages",
    "portugues",
}

_SUMMARY_HEADERS = {
    "acerca de mi",
    "about me",
    "extracto",
    "perfil",
    "perfil profesional",
    "presentacion",
    "professional profile",
    "professional summary",
    "profile",
    "resumen",
    "resumen profesional",
    "sobre mi",
    "summary",
}

_SUMMARY_STOP_HEADERS = {
    "antecedentes academicos",
    "antecedentes personales",
    "certificaciones",
    "contacto",
    "cursos",
    "datos personales",
    "educacion",
    "education",
    "estudios",
    "experiencia",
    "experiencia laboral",
    "formacion",
    "habilidades",
    "idiomas",
    "proyectos",
    "skills",
    "tecnologias",
    "work experience",
}

_SUMMARY_STOP_PREFIXES = (
    "antecedentes academicos",
    "antecedentes personales",
    "certificaciones",
    "contacto",
    "cursos",
    "datos personales",
    "educacion",
    "education",
    "estudios",
    "experiencia",
    "formacion",
    "habilidades",
    "idiomas",
    "proyectos",
    "skills",
    "tecnologias",
    "work experience",
)

_RUT_LABEL_RE = re.compile(r"\b(?:r\s*\.?\s*u\s*\.?\s*t\.?|rut|run)\b", re.I)

_PHONE_CONTEXT_WORDS = {
    "cel",
    "celular",
    "contacto telefonico",
    "mobile",
    "movil",
    "phone",
    "telefono",
    "telefonos",
}

_OCR_CONTACT_SEPARATOR_TOKENS = {"o", "0"}

PDF_TEXT_MIN_CHARS = 80
PDF_TEXT_MIN_ALPHA_CHARS = 40
PDF_TEXT_PAGE_MIN_ALPHA_CHARS = 20
OCR_MAX_PAGES = 10
OCR_DPI = 200
OCR_LANGUAGES = "spa+eng"
_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
_OCR_EMAIL_DOMAIN_CORRECTIONS = {
    "gmalicom": "gmail.com",
}


class _ExtractedText(str):
    def __new__(cls, value: str, *, from_ocr: bool = False):
        obj = str.__new__(cls, value)
        obj.from_ocr = from_ocr
        return obj


def _fold_for_title(value: str) -> str:
    raw = unicodedata.normalize("NFKD", value or "")
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    raw = re.sub(r"[^a-z0-9]+", " ", raw.casefold())
    return " ".join(raw.split())


def _is_section_header(line: str) -> bool:
    folded = _fold_for_title(line)
    if folded in _SECTION_HEADERS:
        return True
    return any(folded.startswith(f"{prefix} ") and len(folded.split()) <= 4 for prefix in _SECTION_PREFIXES)


def _looks_like_descriptive_sentence(line: str) -> bool:
    words = line.split()
    folded = _fold_for_title(line)
    if len(words) >= 7:
        return True
    return bool(re.search(r"\b(con|experiencia|en|para|orientad[oa]|especializad[oa])\b", folded)) and len(words) >= 5


def _strip_leading_temporal_range(line: str) -> str:
    return re.sub(r"^\s*(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\s*[:,-]?\s*", "", line).strip()


def _looks_like_professional_title_phrase(line: str) -> bool:
    folded = _fold_for_title(line)
    words = folded.split()
    if not 2 <= len(words) <= 8:
        return False
    if any(word in words for word in _NAME_INSTITUTION_WORDS):
        return False
    if re.search(r"(?<![a-z0-9])(?:19|20)\d{2}(?![a-z0-9])", folded):
        return False
    return any(keyword in folded for keyword in _TITLE_KEYWORDS)


def _is_academic_title_header(line: str) -> bool:
    folded = _fold_for_title(line)
    if folded in _ACADEMIC_TITLE_HEADERS:
        return True
    return any(folded.startswith(f"{header} ") and len(folded.split()) <= 4 for header in _ACADEMIC_TITLE_HEADERS)


def _starts_with_temporal_range(line: str) -> bool:
    folded = _fold_for_title(line)
    return bool(re.match(r"^(?:19|20)\d{2}\s+(?:19|20)\d{2}(?![a-z0-9])", folded))


def _has_academic_title_risk(line: str) -> bool:
    folded = _fold_for_title(line)
    # Un rango al inicio suele describir estudios o experiencia; preferimos
    # no contaminar cand_titulo con una carrera/registro fechado.
    if _starts_with_temporal_range(line):
        return True
    # Si el candidato a título trae una institución explícita, se trata como
    # contexto académico y se deja fuera del perfil principal.
    return any(word in folded.split() for word in _NAME_INSTITUTION_WORDS)


def _title_candidate_from_line(line: str) -> str | None:
    candidate = _strip_leading_temporal_range(line)
    if not candidate or candidate != line:
        # Si solo queda una profesión breve tras un rango, puede ser un perfil
        # en una columna de cabecera; si trae institución o frase larga, se deja
        # vacío para evitar tomar estudios fechados como título.
        if not _looks_like_professional_title_phrase(candidate):
            return None
    if _has_academic_title_risk(candidate):
        return None
    if _looks_like_descriptive_sentence(candidate) and not _looks_like_professional_title_phrase(candidate):
        return None
    low = candidate.casefold()
    if any(k in low for k in _TITLE_KEYWORDS):
        return candidate[:300]
    return None


def _detect_professional_title(lines: list[str], name_line: str | None) -> str | None:
    for line in lines[:25]:
        # Al entrar a Educación/Formación cortamos la búsqueda: no inferimos el
        # perfil profesional desde carreras académicas.
        if _is_section_header(line) or _is_academic_title_header(line):
            break
        if line == name_line or "@" in line or len(line) > 120:
            continue
        title = _title_candidate_from_line(line)
        if title:
            return title
    return None


def _detect_title_from_summary(summary: str | None) -> str | None:
    if not summary:
        return None
    first_sentence = re.split(r"(?<=[.!?])\s+", summary.strip(), maxsplit=1)[0]
    first_sentence = re.sub(r"^[•\-\s]+", "", first_sentence).strip()
    # En secciones de presentación, muchos CV abren con "Soy/Ingeniero...".
    # Solo usamos el primer fragmento si parece una profesión acotada; si no,
    # preferimos None antes que contaminar el título con resumen narrativo.
    fragment = re.split(r"\s+(?:con|egresad[oa]|titulado|titulada|y\s+titulado|y\s+titulada)\b", first_sentence, maxsplit=1, flags=re.I)[0].strip(" ,.;")
    if _looks_like_professional_title_phrase(fragment):
        return fragment[:300]
    joined = re.sub(r"\s+y\s+", " ", first_sentence, flags=re.I)
    fragment = re.split(r"\s+(?:con|egresad[oa]|titulado|titulada)\b", joined, maxsplit=1, flags=re.I)[0].strip(" ,.;")
    if _looks_like_professional_title_phrase(fragment):
        return fragment[:300]
    return None


def _detect_summary_after_header_title(lines: list[str], title: str | None) -> str | None:
    if not title:
        return None
    title_idx = None
    for idx, line in enumerate(lines[:12]):
        if line == title:
            title_idx = idx
            break
    if title_idx is None:
        return None

    summary_lines: list[str] = []
    for candidate in lines[title_idx + 1:title_idx + 9]:
        if _is_section_header(candidate) or _is_summary_stop_header(candidate) or _is_summary_header(candidate):
            break
        if not _is_summary_content_line(candidate):
            if summary_lines:
                break
            continue
        if _is_phone_context_line(candidate) or re.search(r"(?:\+?56\s*)?9[\s.-]*\d{4}[\s.-]*\d{4}", candidate):
            if summary_lines:
                break
            continue
        if len(candidate.split()) < 4 and not summary_lines:
            continue
        if len(candidate.split()) < 4:
            break
        summary_lines.append(candidate)

    summary = _norm(" ".join(summary_lines))
    return summary[:300] or None


def _is_document_header_for_name(line: str) -> bool:
    return _fold_for_title(line) in _NAME_DOCUMENT_HEADERS


def _strip_name_prefix(line: str) -> str | None:
    match = re.match(r"^\s*nombre\s*:\s*(.+)$", line, flags=re.I)
    return match.group(1).strip() if match else None


def _name_parts(line: str) -> list[str]:
    parts = line.split()
    if 2 <= len(parts) <= 4 and all(re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ'-]+", p) for p in parts):
        return parts
    return []


def _name_component_parts(line: str) -> list[str]:
    parts = line.split()
    if 1 <= len(parts) <= 3 and all(re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ'-]+", p) for p in parts):
        return parts
    return []


def _has_name_context_risk(line: str) -> bool:
    folded = _fold_for_title(line)
    if not folded:
        return True
    if _is_document_header_for_name(line) or _is_section_header(line):
        return True
    # Líneas tipo "Santiago-Chile AIEP" son ubicación + institución, no nombre;
    # se descartan por estructura sin mantener catálogos de instituciones.
    if re.search(r"^[a-z]+ chile(?: |$)", folded):
        return True
    # En nombres partidos se revisan líneas de un solo token; excluir idiomas
    # evita combinarlos como si fueran nombre y apellido.
    if any(word in _NAME_NON_PERSON_WORDS for word in folded.split()):
        return True
    if any(word in folded.split() for word in _NAME_INSTITUTION_WORDS):
        return True
    if any(keyword in folded for keyword in _TITLE_KEYWORDS):
        return True
    return "@" in line or "linkedin" in folded or "github" in folded or bool(re.search(r"\d", line))


def _is_valid_name_line(line: str) -> bool:
    return bool(_name_parts(line)) and not _has_name_context_risk(line)


def _is_valid_name_component_line(line: str) -> bool:
    return bool(_name_component_parts(line)) and not _has_name_context_risk(line)


def _extract_name_before_metadata(line: str) -> str | None:
    if "," not in line:
        return None
    before, after = line.split(",", 1)
    folded_after = _fold_for_title(after)
    if not any(re.search(rf"(?<![a-z0-9]){signal}(?![a-z0-9])", folded_after) for signal in _NAME_LOCATION_SIGNALS):
        return None
    parts = _name_parts(before)
    if not parts or _has_name_context_risk(before):
        return None
    # En CV reales aparece "Nombre Apellido Ciudad, Región, País". Solo
    # quitamos ese último token cuando la metadata trae dos separadores y
    # región explícita, para no recortar apellidos de tres palabras al azar.
    if len(parts) == 3 and line.count(",") >= 2 and re.search(r"(?<![a-z0-9])rm(?![a-z0-9])", folded_after):
        candidate = " ".join(parts[:2])
        return candidate if _is_valid_name_line(candidate) else None
    return before.strip() if _is_valid_name_line(before.strip()) else None


def _combined_name_line(lines: list[str], idx: int) -> str | None:
    if idx + 1 >= min(len(lines), 12):
        return None
    first = lines[idx]
    second = lines[idx + 1]
    if not _is_valid_name_component_line(first) or not _is_valid_name_component_line(second):
        return None
    combined = f"{first} {second}"
    # Combinamos solo dos líneas consecutivas que por separado parecen
    # componentes de nombre; esto evita unir cargos, ciudades o instituciones
    # al nombre cuando vienen debajo.
    return combined if _is_valid_name_line(combined) else None


def _name_before_ocr_contact(line: str) -> str | None:
    tokens = line.split()
    contact_index = next((idx for idx, token in enumerate(tokens) if "@" in token), None)
    if contact_index is None or contact_index == 0:
        return None
    candidate_tokens = tokens[:contact_index]
    if len(candidate_tokens) > 4:
        return None
    # OCR puede leer iconos de contacto como una letra aislada justo antes del
    # email. Solo se descarta si el prefijo restante sigue siendo un nombre
    # válido; no se infieren apellidos ni se relajan las reglas generales.
    if candidate_tokens[-1].casefold() in _OCR_CONTACT_SEPARATOR_TOKENS:
        candidate_without_separator = " ".join(candidate_tokens[:-1])
        if _is_valid_name_line(candidate_without_separator):
            return candidate_without_separator
    if _is_valid_name_line(" ".join(candidate_tokens)):
        return " ".join(candidate_tokens)
    return None


def _detect_name_line(lines: list[str], *, from_ocr: bool = False) -> str | None:
    upper_block = lines[:12]
    for line in upper_block:
        # "Nombre:" es una etiqueta explícita del CV; se prioriza para evitar
        # caer al fallback de email cuando la línea trae el nombre rotulado.
        prefixed = _strip_name_prefix(line)
        if prefixed and _is_valid_name_line(prefixed):
            return prefixed

    for idx, line in enumerate(upper_block):
        metadata_name = _extract_name_before_metadata(line)
        if metadata_name:
            return metadata_name
        if _has_name_context_risk(line):
            continue
        combined = _combined_name_line(lines, idx)
        if combined:
            return combined
        if _is_valid_name_line(line):
            return line
    if from_ocr:
        for line in upper_block:
            recovered = _name_before_ocr_contact(line)
            if recovered:
                return recovered
    return None


def _is_summary_header(line: str) -> bool:
    return _fold_for_title(line) in _SUMMARY_HEADERS


def _is_summary_stop_header(line: str) -> bool:
    folded = _fold_for_title(line)
    if folded in _SUMMARY_STOP_HEADERS:
        return True
    return any(folded.startswith(f"{prefix} ") and len(folded.split()) <= 4 for prefix in _SUMMARY_STOP_PREFIXES)


def _is_summary_content_line(line: str) -> bool:
    low = line.casefold()
    # Emails y URLs dentro del bloque no se guardan como resumen para evitar
    # contaminar el perfil profesional con datos de contacto.
    return "@" not in line and not low.startswith(("http://", "https://", "www."))


def _detect_professional_summary(lines: list[str]) -> str | None:
    for idx, line in enumerate(lines):
        if not _is_summary_header(line):
            continue
        summary_lines: list[str] = []
        for candidate in lines[idx + 1:]:
            # Solo extraemos el resumen desde una sección explícita y la
            # detenemos ante otro encabezado para no mezclar experiencias,
            # estudios, proyectos u otras secciones con el perfil profesional.
            if _is_summary_stop_header(candidate):
                break
            if _is_summary_header(candidate):
                continue
            if not _is_summary_content_line(candidate):
                continue
            summary_lines.append(candidate)
        summary = _norm(" ".join(summary_lines))
        # Si el encabezado existe pero no trae contenido útil, preferimos None
        # antes que recuperar el antiguo fallback de primera línea larga.
        return summary[:300] or None
    return None


def _detect_professional_summary_by_experience_statement(lines: list[str]) -> str | None:
    for idx, line in enumerate(lines):
        folded = _fold_for_title(line)
        if not re.match(r"^con mas de \d+ anos de experiencia\b", folded):
            continue
        # Este fallback solo acepta una estructura explícita de perfil
        # ("Con más de N años..."). No usamos cualquier párrafo largo porque
        # suele mezclar funciones, estudios o datos de contacto con el resumen.
        summary_lines: list[str] = []
        for candidate in lines[idx:idx + 6]:
            if _is_section_header(candidate) or _is_summary_stop_header(candidate) or _is_summary_header(candidate):
                break
            if not _is_summary_content_line(candidate):
                break
            if _is_phone_context_line(candidate) or re.search(r"(?:\+?56\s*)?9[\s.-]*\d{4}[\s.-]*\d{4}", candidate):
                break
            if len(candidate.split()) < 4 and summary_lines:
                break
            summary_lines.append(candidate)
        summary = _norm(" ".join(summary_lines))
        return summary[:300] or None
    return None


def _expected_rut_dv(body: str) -> str:
    total = 0
    multiplier = 2
    for digit in reversed(body):
        total += int(digit) * multiplier
        multiplier = 2 if multiplier == 7 else multiplier + 1
    value = 11 - (total % 11)
    if value == 11:
        return "0"
    if value == 10:
        return "K"
    return str(value)


def _is_valid_rut(body: str, dv: str) -> bool:
    return bool(re.fullmatch(r"\d{7,8}", body)) and _expected_rut_dv(body) == dv.upper()


def _is_phone_context_line(line: str) -> bool:
    folded = _fold_for_title(line)
    return any(word in folded for word in _PHONE_CONTEXT_WORDS)


def _rut_candidates_from_line(line: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    patterns = (
        r"(?<![a-z0-9])(\d{1,2}\.\d{3}\.\d{3})\s*-\s*([0-9Kk])(?![a-z0-9])",
        r"(?<![a-z0-9])(\d{7,8})\s*-\s*([0-9Kk])(?![a-z0-9])",
        r"(?<![a-z0-9])(\d{7,8})([0-9Kk])(?![a-z0-9])",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, line, flags=re.I):
            body = re.sub(r"\D", "", match.group(1))
            candidates.append((body, match.group(2).upper()))
    return candidates


def _detect_rut(lines: list[str]) -> tuple[int | None, int | None]:
    # Las etiquetas RUT/RUN tienen prioridad porque reducen el riesgo de tomar
    # números genéricos del CV como identificación del candidato.
    for line in lines:
        if not _RUT_LABEL_RE.search(line):
            continue
        for body, dv in _rut_candidates_from_line(line):
            if _is_valid_rut(body, dv):
                return int(body), 10 if dv == "K" else int(dv)

    for line in lines:
        # Las líneas de teléfono se descartan aunque contengan números con
        # longitud compatible; validamos de forma conservadora para evitar
        # casos como "Teléfonos : 22380440 - 89351800".
        if _is_phone_context_line(line):
            continue
        for body, dv in _rut_candidates_from_line(line):
            # El DV módulo 11 es obligatorio para aceptar RUT sin depender solo
            # del largo numérico, que también puede aparecer en teléfonos.
            if _is_valid_rut(body, dv):
                return int(body), 10 if dv == "K" else int(dv)
    return None, None


def _recover_ocr_email(flat: str) -> str | None:
    candidates: list[str] = []
    for raw_token in re.findall(r"\S*@\S+", flat):
        token = raw_token.strip(" \t\r\n<>()[]{}\"'“”‘’,;:")
        if token.count("@") != 1:
            continue
        local, domain = token.split("@", 1)
        local = local.strip(" \t\r\n<>()[]{}\"'“”‘’,;:")
        domain = domain.strip(" \t\r\n<>()[]{}\"'“”‘’,;:")
        if not re.fullmatch(r"[A-Z0-9._%+-]+", local, re.I):
            continue
        domain_key = re.sub(r"[^a-z0-9]+", "", domain.casefold())
        corrected_domain = _OCR_EMAIL_DOMAIN_CORRECTIONS.get(domain_key)
        if not corrected_domain:
            continue
        # La reparación OCR se limita al dominio: corregir el local-part
        # implicaría adivinar la identidad de la casilla personal.
        candidates.append(f"{local}@{corrected_domain}".lower())
    # Si hubiera más de un token reparable distinto, no elegimos uno al azar.
    unique = list(dict.fromkeys(candidates))
    return unique[0] if len(unique) == 1 else None


def _alpha_count(text: str) -> int:
    return sum(1 for char in text if char.isalpha())


def _has_sufficient_text(text: str) -> bool:
    normalized = _norm(text)
    return len(normalized) >= PDF_TEXT_MIN_CHARS and _alpha_count(normalized) >= PDF_TEXT_MIN_ALPHA_CHARS


def _has_sufficient_pdf_text(page_texts: list[str]) -> bool:
    text = "\n".join(page_texts)
    pages_with_text = sum(1 for page_text in page_texts if _alpha_count(page_text) >= PDF_TEXT_PAGE_MIN_ALPHA_CHARS)
    # No basta con que pypdf devuelva algo: algunos PDFs escaneados entregan
    # basura mínima. Pedimos texto útil y al menos una página con letras reales.
    return _has_sufficient_text(text) and pages_with_text >= 1


def _extract_pdf_text_with_pypdf(content: bytes) -> list[str]:
    try:
        reader = PdfReader(io.BytesIO(content))
        return [(page.extract_text() or "") for page in reader.pages]
    except Exception as exc:
        raise ValueError("No fue posible leer el PDF. El archivo puede estar corrupto o no ser procesable.") from exc


def _load_ocr_dependencies():
    try:
        import fitz
        import pytesseract
    except ImportError as exc:
        raise ValueError("El PDF no contiene texto utilizable y OCR no está disponible en el entorno.") from exc
    return fitz, pytesseract


def _ocr_pdf_text(content: bytes) -> str:
    fitz, pytesseract = _load_ocr_dependencies()
    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise ValueError("No fue posible leer el PDF. El archivo puede estar corrupto o no ser procesable.") from exc

    page_texts: list[str] = []
    pages_to_process = min(len(document), OCR_MAX_PAGES)
    zoom = OCR_DPI / 72
    matrix = fitz.Matrix(zoom, zoom)

    # OCR es costoso; se limita a las primeras páginas de CV para evitar
    # consumo excesivo de CPU/memoria ante documentos grandes o escaneos pesados.
    for page_index in range(pages_to_process):
        temp_path = None
        try:
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
                tmp.write(pixmap.tobytes("png"))
            page_texts.append(pytesseract.image_to_string(temp_path, lang=OCR_LANGUAGES) or "")
        except pytesseract.TesseractNotFoundError as exc:
            raise ValueError("El PDF no contiene texto utilizable y OCR no está disponible en el entorno.") from exc
        except Exception as exc:
            raise ValueError("No fue posible ejecutar OCR sobre el PDF.") from exc
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

    return "\n\n".join(page_texts)


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        # pypdf es el camino principal: es rápido y conserva el flujo actual
        # para PDFs con capa de texto. OCR se usa solo cuando ese texto no sirve.
        page_texts = _extract_pdf_text_with_pypdf(content)
        text = "\n".join(page_texts)
        if _has_sufficient_pdf_text(page_texts):
            return _ExtractedText(text, from_ocr=False)

        # El OCR solo transforma imagen a texto; el resultado vuelve al mismo
        # parse_core/derive_nested_from_cv para no duplicar reglas de negocio.
        ocr_text = _ocr_pdf_text(content)
        if not _has_sufficient_text(ocr_text):
            raise ValueError("No fue posible extraer texto utilizable del PDF mediante OCR.")
        return _ExtractedText(ocr_text, from_ocr=True)
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

    email_match = _EMAIL_RE.search(flat)
    if email_match:
        email = email_match.group(0).lower()
    elif getattr(text, "from_ocr", False):
        # Solo reparamos dominios cuando sabemos que el texto viene de OCR:
        # en PDFs textuales, un email mal formado debe seguir fallando.
        email = _recover_ocr_email(flat)
        if not email:
            raise ValueError("No fue posible identificar un correo electrónico en el CV")
    else:
        raise ValueError("No fue posible identificar un correo electrónico en el CV")

    phone = None
    p = re.search(r"(?:\+?56\s*)?9[\s.-]*\d{4}[\s.-]*\d{4}", flat)
    if p:
        phone = re.sub(r"\D", "", p.group(0))[-9:]

    rut_num, dv = _detect_rut(lines)

    urls = re.findall(r"(?:https?://|www\.)[^\s,;]+", flat, flags=re.I)
    social = [u.rstrip(".)]") for u in urls if "linkedin" in u.lower() or "github" in u.lower()]

    # El nombre se busca con filtros de contexto: las primeras líneas del CV
    # pueden ser headings, instituciones, ubicaciones o metadatos, no identidad.
    name_line = _detect_name_line(lines, from_ocr=getattr(text, "from_ocr", False))
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

    summary = _detect_professional_summary(lines)
    title = _detect_professional_title(lines, name_line)
    if title is None:
        title = _detect_title_from_summary(summary)
    if summary is None:
        summary = _detect_summary_after_header_title(lines, title)
    if summary is None:
        summary = _detect_professional_summary_by_experience_statement(lines)

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


# ==========================================================
# IDIOMAS - extracción conservadora para M3
# ==========================================================

_LANGUAGE_ALIASES = {
    "ingles": {"ingles", "english"},
    "espanol": {"espanol", "spanish", "castellano"},
    "portugues": {"portugues", "portuguese"},
    "frances": {"frances", "french"},
    "aleman": {"aleman", "german"},
    "italiano": {"italiano", "italian"},
    "mandarin": {"mandarin", "chino mandarin", "mandarin chinese"},
}


def fold_text(value: str) -> str:
    raw = unicodedata.normalize("NFKD", value or "")
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    return " ".join(raw.casefold().strip().split())


def language_aliases(catalog_name: str) -> set[str]:
    folded = fold_text(catalog_name)
    aliases = {folded}
    aliases.update(_LANGUAGE_ALIASES.get(folded, set()))
    return {x for x in aliases if x}


def detect_language_level_code(value: str) -> str | None:
    """Retorna código estable del catálogo de nivel, sin inventar precisión CEFR."""
    folded = fold_text(value)
    # CEFR explícito tiene prioridad.
    m = re.search(r"(?<![a-z0-9])([abc][12])(?![a-z0-9])", folded, re.I)
    if m:
        return m.group(1).upper()
    if re.search(r"\b(nativo|native|native speaker|mother tongue|lengua materna)\b", folded):
        return "NAT"
    if re.search(r"\b(avanzado|advanced|fluent|fluido)\b", folded):
        return "AVA"
    if re.search(r"\b(intermedio|intermediate)\b", folded):
        return "INT"
    if re.search(r"\b(basico|basic|elementary)\b", folded):
        return "BAS"
    return None


def candidate_language_lines(text: str) -> list[str]:
    """Líneas limpias para detección de idiomas; conserva contexto local del CV."""
    return [" ".join(x.split()) for x in (text or "").splitlines() if x.strip()]
