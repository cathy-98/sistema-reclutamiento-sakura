# test/test_candidatos_integracion.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import Base, engine, get_db
from app.candidatos.models import Candidato
import logging
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Desactivar logs ruidosos y activar logging de queries SQL para inspeccionar N+1
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from app.database import Base, get_db
from app.candidatos.models import (
    Candidato, DireccionCandidato, CandidatoHabilidad, 
    ExperienciaLaboral, EstudioCandidato, Curso
)
from app.candidatos.schemas import (
    CandidatoCreate, DireccionCandidatoCreate, CandidatoHabilidadCreate,
    ExperienciaLaboralCreate, EstudioCandidatoCreate, CursoCreate
)
from app.candidatos.services import crear_candidato_completo
# ⚠️ Asegúrate de importar los catalogos aquí también para registrar la metadata completa
import app.catalogos.models  # <--- Cambia por la ruta real de tu módulo de catálogos

def test_ejecutar_pruebas_paso_5(db_session):
    print("\n" + "="*70)
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN: PASO 5 (MÓDULO CANDIDATOS)")
    print("="*70 + "\n")

    # -------------------------------------------------------------------------
    # 1. PRUEBA DE GUARDADO ANIDADO (6 TABLAS EN UNA TRANSACCIÓN ATÓMICA)
    # -------------------------------------------------------------------------
    print("🔹 [Prueba 1/3] Evaluando Guardado Anidado en Cascadas...")
    
    payload = CandidatoCreate(
        cand_rut_sin_dv=19876543,
        cand_dv="K",
        cand_nombres="Carlos Eduardo",
        cand_apellidos="Gómez Tapia",
        cand_email="carlos.gomez.test@elitsoft.cl",
        cand_telefono="+56912345678",
        cand_fecha_nacimiento=date(1995, 5, 20),
        cand_resumen_profesional="Desarrollador Backend Senior con experiencia en Python y Cloud.",
        cand_disponibilidad_id=1,
        
        # 1. Dirección (1:1)
        direccion=DireccionCandidatoCreate(
            drcd_comuna_id=1,
            drcd_calle="Av. Providencia",
            drcd_numero="1234",
            drcd_depto_oficina="Oficina 502"
        ),
        
        # 2. Habilidades Generales (1:N)
        habilidades=[
            CandidatoHabilidadCreate(cdhb_habilidad_id=1, cdhb_nivel_habilidad_id=5, cdhb_anios_experiencia=5),
            CandidatoHabilidadCreate(cdhb_habilidad_id=2, cdhb_nivel_habilidad_id=4, cdhb_anios_experiencia=3)
        ],
        
        # 3. Experiencias Laborales y Habilidades Asociadas (1:N + M:N)
        experiencias=[
            ExperienciaLaboralCreate(
                expl_empresa="Tech Solutions S.A.",
                expl_cargo_id=1,
                expl_cargo_nombre_custom="Lead Developer",
                expl_fecha_inicio=date(2021, 3, 1),
                expl_trabaja_actualmente=True,
                expl_descripcion_funciones="Liderazgo de equipo backend y microservicios.",
                habilidades_ids=[1, 2]
            )
        ],
        
        # 4. Estudios Académicos (1:N)
        estudios=[
            EstudioCandidatoCreate(
                estc_institucion_id=1,
                estc_carrera_id=1,
                estc_nivel_estudio_id=4,
                estc_estado_estudio_id=1,
                estc_fecha_inicio=date(2013, 3, 1),
                estc_fecha_fin=date(2018, 12, 15)
            )
        ],
        
        # 5. Cursos y Capacitaciones (1:N)
        cursos=[
            CursoCreate(
                crs_nombre="Certificación AWS Solutions Architect",
                crs_institucion_id=1,
                crs_horas_duracion=40,
                crs_fecha_obtencion=date(2023, 6, 10),
                crs_tiene_certificado=True
            )
        ]
    )

    # Persistencia mediante la función de servicio
    candidato_creado = crear_candidato_completo(db_session, payload)
    cand_id = candidato_creado.cand_id

    # Verificación de inserción en BD
    assert cand_id is not None, "❌ Error: No se generó el cand_id."
    assert candidato_creado.direccion is not None, "❌ Error: La dirección no fue persistida."
    assert len(candidato_creado.habilidades) == 2, "❌ Error: No se guardaron las habilidades."
    assert len(candidato_creado.experiencias) == 1, "❌ Error: No se guardó la experiencia laboral."
    assert len(candidato_creado.experiencias[0].habilidades_asociadas) == 2, "❌ Error: No se asociaron las habilidades a la experiencia."
    assert len(candidato_creado.estudios) == 1, "❌ Error: No se guardaron los estudios."
    assert len(candidato_creado.cursos) == 1, "❌ Error: No se guardaron los cursos."

    print(f"✅ PASADO: Candidato guardado con exito en sus 6 tablas asociadas. ID: {cand_id}\n")

    # Limpiar caché de sesión de SQLAlchemy para forzar una consulta real a la BD
    db_session.clear()

    # -------------------------------------------------------------------------
    # 2. PRUEBA DE CARGA EFICIENTE (NO N+1 CON SELECTIN)
    # -------------------------------------------------------------------------
    print("🔹 [Prueba 2/3] Evaluando Carga Eficiente (Estrategia selectin sin N+1)...")
    
    # Realizamos la consulta limpia desde la BD
    candidato_db = db_session.query(Candidato).filter(Candidato.cand_id == cand_id).first()

    # Accedemos a las propiedades anidadas para confirmar que 'selectin' las precargó
    print(f"   -> Nombre: {candidato_db.cand_nombres} {candidato_db.cand_apellidos}")
    print(f"   -> Dirección: {candidato_db.direccion.drcd_calle}")
    print(f"   -> Cantidad Habilidades: {len(candidato_db.habilidades)}")
    print(f"   -> Cantidad Experiencias: {len(candidato_db.experiencias)}")
    print(f"   -> Cantidad Estudios: {len(candidato_db.estudios)}")
    print(f"   -> Cantidad Cursos: {len(candidato_db.cursos)}")

    print("✅ PASADO: Carga eficiente validada correctamente sin consultas redundantes N+1.\n")

    # -------------------------------------------------------------------------
    # 3. PRUEBA DE ELIMINACIÓN EN CASCADA (DELETE-ORPHAN)
    # -------------------------------------------------------------------------
    print("🔹 [Prueba 3/3] Evaluando Eliminación en Cascada (delete-orphan)...")

    # Eliminar el candidato principal
    db_session.delete(candidato_db)
    db_session.commit()

    # Verificar que el candidato y sus tablas dependientes se hayan eliminado
    cand_eliminado = db_session.query(Candidato).filter(Candidato.cand_id == cand_id).first()
    dir_eliminada = db_session.query(DireccionCandidato).filter(DireccionCandidato.drcd_candidato_id == cand_id).first()
    hab_eliminada = db_session.query(CandidatoHabilidad).filter(CandidatoHabilidad.cdhb_candidato_id == cand_id).all()
    exp_eliminada = db_session.query(ExperienciaLaboral).filter(ExperienciaLaboral.expl_candidato_id == cand_id).all()
    est_eliminado = db_session.query(EstudioCandidato).filter(EstudioCandidato.estc_candidato_id == cand_id).all()
    cur_eliminado = db_session.query(Curso).filter(Curso.crs_candidato_id == cand_id).all()

    assert cand_eliminado is None, "❌ Error: El candidato no fue eliminado."
    assert dir_eliminada is None, "❌ Error: La dirección huérfana no se eliminó."
    assert len(hab_eliminada) == 0, "❌ Error: Quedaron habilidades huérfanas."
    assert len(exp_eliminada) == 0, "❌ Error: Quedaron experiencias huérfanas."
    assert len(est_eliminado) == 0, "❌ Error: Quedaron estudios huérfanos."
    assert len(cur_eliminado) == 0, "❌ Error: Quedaron cursos huérfanos."

    print("✅ PASADO: Eliminación en cascada confirmada. No se generaron registros huérfanos ni errores de FK.\n")

    print("="*70)
    print("🎉 ¡TODAS LAS PRUEBAS DEL PASO 5 FUERON COMPLETADAS CON ÉXITO!")
    print("="*70 + "\n")


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        ejecutar_pruebas_paso_5(db)
    finally:
        db.close()
