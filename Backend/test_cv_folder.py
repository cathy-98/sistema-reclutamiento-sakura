import os
import asyncio
from sqlalchemy.orm import Session

# Importamos la sesión de base de datos y modelos del proyecto
from app.database import engine
from app.models import Candidato
from app.services.cv_service import extraer_texto_pdf, extraer_texto_docx, procesar_cv_con_python

# Carpeta que escaneará el script (Ubicada en la raíz Backend/temp_cvs)
FOLDER_PATH = "./temp_cvs"

async def procesar_archivo_local(file_path: str, db: Session):
    file_name = os.path.basename(file_path)
    extension = file_name.split(".")[-1].lower()
    
    print(f"\n🔍 [PROCESANDO]: '{file_name}'...")
    
    try:
        with open(file_path, "rb") as f:
            contenido_bytes = f.read()

        if extension == "pdf":
            texto_extraido = extraer_texto_pdf(contenido_bytes)
        elif extension == "docx":
            texto_extraido = extraer_texto_docx(contenido_bytes)
        else:
            print(f"⚠️ [IGNORADO]: Extensión '.{extension}' no soportada para {file_name}.")
            return

        if not texto_extraido.strip():
            print(f"❌ [ERROR]: El archivo '{file_name}' no contiene texto extraíble.")
            return

        print(f"⚙️ [PYTHON]: Analizando texto de '{file_name}' localmente con Regex...")
        candidato_esquema = await procesar_cv_con_python(texto_extraido)

        # Buscar si ya existe un candidato con el mismo correo electrónico
        existente = db.query(Candidato).filter(
            Candidato.correo_electronico == candidato_esquema.correo_electronico
        ).first()

        if existente:
            print(f"🔄 [ACTUALIZANDO]: El correo '{candidato_esquema.correo_electronico}' ya existe en la BD.")
            print(f"   Modificando ficha de: {existente.nombres} {existente.apellido_paterno} (ID: {existente.id_candidato})")
            
            # Actualizamos de forma inteligente solo los campos que no sean nulos en el nuevo análisis
            datos_nuevos = candidato_esquema.model_dump()
            for clave, valor in datos_nuevos.items():
                if valor is not None:
                    setattr(existente, clave, valor)
            
            db.commit()
            db.refresh(existente)
            print(f"✅ [ACTUALIZADO]: Ficha del candidato guardada exitosamente.")
            
        else:
            # Si no existe, creamos el registro nuevo desde cero
            nuevo_candidato = Candidato(**candidato_esquema.model_dump())
            db.add(nuevo_candidato)
            db.commit()
            db.refresh(nuevo_candidato)
            print(f"✅ [GUARDADO]: {nuevo_candidato.nombres} {nuevo_candidato.apellido_paterno} insertado como nuevo registro.")

    except Exception as e:
        db.rollback()
        print(f"❌ [FALLIDO]: Error al procesar '{file_name}': {str(e)}")


async def main():
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
        print(f"📁 Se creó la carpeta '{FOLDER_PATH}'. Coloca tus archivos allí y vuelve a ejecutar.")
        return

    archivos = [
        os.path.join(FOLDER_PATH, f) 
        for f in os.listdir(FOLDER_PATH) 
        if f.lower().endswith((".pdf", ".docx"))
    ]

    if not archivos:
        print(f"ℹ️ La carpeta '{FOLDER_PATH}' está vacía. Coloca archivos .pdf o .docx en ella.")
        return

    print(f"🚀 Se encontraron {len(archivos)} currículum(s) en '{FOLDER_PATH}'. Iniciando procesamiento local...")

    from app.database import SessionLocal
    db = SessionLocal()

    try:
        for ruta_archivo in archivos:
            await procesar_archivo_local(ruta_archivo, db)
    finally:
        db.close()
        print("\n🏁 [FIN DEL PROCESO]: Escaneo de currículums completado.")

if __name__ == "__main__":
    asyncio.run(main())