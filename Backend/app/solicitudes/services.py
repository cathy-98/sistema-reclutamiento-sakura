from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.solicitudes.models import Solicitud


def evaluar_candidato_cumple_excluyentes(
    db: Session, 
    solicitud_id: int, 
    habilidades_candidato: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evalúa si un candidato cumple con el 100% de las habilidades excluyentes.
    
    Estructura de `habilidades_candidato`:
    [{"habilidad_id": 1, "anios_experiencia": 3}, ...]
    """
    solicitud = db.query(Solicitud).filter(Solicitud.sol_id == solicitud_id).first()
    
    if not solicitud:
        raise ValueError(f"Solicitud con ID {solicitud_id} no encontrada.")
    
    # Obtenemos las habilidades obligatorias mediante la @property del modelo
    habilidades_req = solicitud.habilidades_excluyentes
    
    if not habilidades_req:
        return {
            "cumple_excluyentes": True,
            "descartado_automaticamente": False,
            "motivo": "La vacante no posee habilidades excluyentes configuradas.",
            "habilidades_faltantes": []
        }
    
    # Búsqueda en tiempo constante O(1)
    cand_map = {h['habilidad_id']: h.get('anios_experiencia', 0) for h in habilidades_candidato}
    
    faltantes = []
    
    for req in habilidades_req:
        hab_id = req.solhb_habilidad_id
        anios_req = req.solhb_anios_experiencia_req
        
        # Validación 1: Presencia de la habilidad
        if hab_id not in cand_map:
            faltantes.append({
                "habilidad_id": hab_id,
                "motivo": "Habilidad obligatoria no poseída por el candidato"
            })
            continue
            
        # Validación 2: Años de experiencia mínimos
        if cand_map[hab_id] < anios_req:
            faltantes.append({
                "habilidad_id": hab_id,
                "motivo": f"Experiencia insuficiente ({cand_map[hab_id]} años dados vs {anios_req} requeridos)"
            })

    cumple = len(faltantes) == 0
    
    return {
        "cumple_excluyentes": cumple,
        "descartado_automaticamente": not cumple,
        "habilidades_faltantes": faltantes
    }