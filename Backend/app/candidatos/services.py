from sqlalchemy.orm import Session
from app.candidatos.models import (
    Candidato, DireccionCandidato, CandidatoHabilidad, 
    ExperienciaLaboral, ExperienciaLaboralHabilidad, EstudioCandidato, Curso
)
from app.candidatos.schemas import CandidatoCreate


def crear_candidato_completo(db: Session, candidato_in: CandidatoCreate) -> Candidato:
    """
    Recibe el DTO con datos anidados y los persiste en cascada dentro de una transacción atómica.
    """
    # 1. Extraer datos del candidato omitiendo listas anidadas
    datos_cand = candidato_in.model_dump(
        exclude={"direccion", "habilidades", "experiencias", "estudios", "cursos"}
    )
	
									
    nuevo_candidato = Candidato(**datos_cand)

    # 2. Mapear Dirección (1:1)
    if candidato_in.direccion:
        nuevo_candidato.direccion = DireccionCandidato(**candidato_in.direccion.model_dump())

    # 3. Mapear Habilidades Generales (1:N)
    for hab in candidato_in.habilidades:
        nuevo_candidato.habilidades.append(CandidatoHabilidad(**hab.model_dump()))

    # 4. Mapear Experiencias Laborales y sus Habilidades Asociadas
    for exp in candidato_in.experiencias:
        habilidades_ids = exp.habilidades_ids
        datos_exp = exp.model_dump(exclude={"habilidades_ids"})
        
        nueva_exp = ExperienciaLaboral(**datos_exp)
        
        # Persistir la relación intermedia M:N (Experiencia -> Habilidades)
        for hab_id in habilidades_ids:
            nueva_exp.habilidades_asociadas.append(
                ExperienciaLaboralHabilidad(exhb_habilidad_id=hab_id)
            )
            
        nuevo_candidato.experiencias.append(nueva_exp)

    # 5. Mapear Estudios (1:N)
    for est in candidato_in.estudios:
        nuevo_candidato.estudios.append(EstudioCandidato(**est.model_dump()))

    # 6. Mapear Cursos (1:N)
    for cur in candidato_in.cursos:
        nuevo_candidato.cursos.append(Curso(**cur.model_dump()))

    # 7. Persistencia Atómica
    db.add(nuevo_candidato)
    db.commit()
    db.refresh(nuevo_candidato)
    return nuevo_candidato
