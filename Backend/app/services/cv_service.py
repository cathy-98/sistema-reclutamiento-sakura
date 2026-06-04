import io
import re
from pypdf import PdfReader
from fastapi import HTTPException
from app.schemas import CandidatoCreate

def extraer_texto_pdf(contenido_archivo: bytes) -> str:
    """
    Lee los bytes de un archivo PDF en memoria y extrae todo su texto plano utilizando pypdf.
    """
    try:
        pdf_file = io.BytesIO(contenido_archivo)
        reader = PdfReader(pdf_file)
        texto_completo = []
        
        for pagina in reader.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo.append(texto_pagina)
                
        return "\n".join(texto_completo)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo extraer el texto del archivo PDF: {str(e)}"
        )

def extraer_texto_docx(contenido_archivo: bytes) -> str:
    """
    Lee los bytes de un archivo DOCX en memoria y extrae todo su texto plano utilizando python-docx.
    """
    try:
        import docx
        docx_file = io.BytesIO(contenido_archivo)
        doc = docx.Document(docx_file)
        texto_completo = []
        
        for parrafo in doc.paragraphs:
            if parrafo.text:
                texto_completo.append(parrafo.text)
                
        for tabla in doc.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    if celda.text:
                        texto_completo.append(celda.text)
                        
        return "\n".join(texto_completo)
    except ImportError:
        raise HTTPException(
            status_code=502,
            detail="La librería 'python-docx' no está instalada. Por favor ejecute: pip install python-docx"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo extraer el texto del archivo DOCX: {str(e)}"
        )

async def procesar_cv_con_python(texto_cv: str) -> CandidatoCreate:
    """
    Mantiene el nombre de la función por compatibilidad, pero procesa el 
    texto de forma 100% local usando expresiones regulares y lógica nativa de Python.
    """
    # 1. Extraer Correo Electrónico
    pattern_email = r'[a-zA-Z0-9-_\.]+@[a-zA-Z0-9-_\.]+\.[a-zA-Z]{2,5}'
    match_email = re.search(pattern_email, texto_cv)
    correo = match_email.group(0).strip() if match_email else None

    if not correo:
        raise HTTPException(
            status_code=422,
            detail="No se pudo procesar el CV: No se encontró un correo electrónico válido."
        )

    # 2. Extraer Teléfono de Contacto (+569... o similares)
    # Busca números que empiecen con + y tengan entre 8 y 12 dígitos, o secuencias numéricas comunes
    pattern_tel = r'\+?\d[\d\s-]{7,13}\d'
    matches_tel = re.findall(pattern_tel, texto_cv)
    telefono = None
    
    # Filtrar falsos positivos (como años o fechas) buscando el que tenga estructura de celular o fono
    for tel in matches_tel:
        limpio = tel.replace(" ", "").replace("-", "")
        if "569" in limpio or len(limpio) >= 9:
            telefono = limpio
            break

    # 3. Extraer Nombre y Apellidos de las primeras líneas del CV
    lineas = [l.strip() for l in texto_cv.split('\n') if l.strip()]
    nombres = "Candidato"
    apellido_paterno = "Desconocido"
    apellido_materno = None

    # Intentamos leer la primera línea significativa que suele ser el nombre completo
    if lineas:
        nombre_completo_candidato = lineas[0]
        # Si la primera línea tiene texto sospechoso de no ser un nombre (como "Curriculum"), bajamos a la segunda
        if any(x in nombre_completo_candidato.lower() for x in ["curriculum", "cv", "hoja de vida", "resumen"]) and len(lineas) > 1:
            nombre_completo_candidato = lineas[1]
            
        palabras = nombre_completo_candidato.split()
        
        if len(palabras) == 2:
            nombres = palabras[0]
            apellido_paterno = palabras[1]
        elif len(palabras) == 3:
            nombres = palabras[0]
            apellido_paterno = palabras[1]
            apellido_materno = palabras[2]
        elif len(palabras) >= 4:
            nombres = f"{palabras[0]} {palabras[1]}"
            apellido_paterno = palabras[2]
            apellido_materno = palabras[3]

    # 4. Extraer URLs (LinkedIn / GitHub) si están presentes
    linkedin_url = None
    github_url = None
    
    match_li = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', texto_cv, re.IGNORECASE)
    if match_li:
        linkedin_url = match_li.group(0)
    else:
        # Intento de captura si viene simplificado como 'linkedin: /nombre'
        match_li_short = re.search(r'linkedin:\s*/([a-zA-Z0-9_-]+)', texto_cv, re.IGNORECASE)
        if match_li_short:
            linkedin_url = f"https://www.linkedin.com/in/{match_li_short.group(1)}"

    match_gh = re.search(r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+', texto_cv, re.IGNORECASE)
    if match_gh:
        github_url = match_gh.group(0)

    # 5. Intentar armar el resumen profesional con las primeras líneas descriptivas
    resumen_lineas = lineas[1:4] if len(lineas) > 4 else lineas
    resumen_profesional = " ".join(resumen_lineas)[:250] + "..."

    # Retornamos el esquema validado por Pydantic listo para persistir en Postgres
    return CandidatoCreate(
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        correo_electronico=correo,
        telefono_contacto=telefono,
        rut_candidato=None,
        fecha_nacimiento=None,
        linkedin_url=linkedin_url,
        github_url=github_url,
        pretension_renta=None,
        disponibilidad=None,
        resumen_profesional=resumen_profesional
    )