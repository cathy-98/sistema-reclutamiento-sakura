import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from app.solicitudes.models import Solicitud, SolicitudHabilidad
from app.solicitudes.schemas import SolicitudCreate, SolicitudHabilidadCreate
from app.solicitudes.services import evaluar_candidato_cumple_excluyentes


def test_property_habilidades_excluyentes():
    """Valida que las @property .habilidades_excluyentes y .habilidades_deseables filtren correctamente."""
    sol = Solicitud(sol_codigo="TEST-01", sol_titulo="Test Python")
    
    h1 = SolicitudHabilidad(solhb_habilidad_id=1, solhb_es_excluyente=True, solhb_anios_experiencia_req=2)
    h2 = SolicitudHabilidad(solhb_habilidad_id=2, solhb_es_excluyente=False, solhb_anios_experiencia_req=1)
    
    sol.habilidades.extend([h1, h2])
    
    assert len(sol.habilidades_excluyentes) == 1
    assert len(sol.habilidades_deseables) == 1
    assert sol.habilidades_excluyentes[0].solhb_habilidad_id == 1


def test_schema_validacion_al_menos_una_excluyente():
    """Valida que Pydantic rechace una solicitud sin habilidades excluyentes."""
    with pytest.raises(ValidationError):
        SolicitudCreate(
            sol_codigo="SOL-TEST",
            sol_titulo="Test Backend",
            sol_cliente_id=1,
            sol_estado_id=1,
            sol_usuario_creador_id=1,
            habilidades=[
                SolicitudHabilidadCreate(solhb_habilidad_id=1, solhb_es_excluyente=False)
            ]
        )


def test_helper_matching_candidato_descarte():
    """Valida la detección de brechas usando un objeto Mockeado en memoria (sin tocar PostgreSQL)."""
    
    # 1. Crear el objeto en memoria (Sin guardarlo en BD)
    solicitud_mock = Solicitud(sol_id=999, sol_codigo="MOCK-01", sol_titulo="Mock Dev")
    
    # Agregar habilidad excluyente (ID: 10, Requiere: 3 años)
    sh = SolicitudHabilidad(
        solhb_solicitud_id=999,
        solhb_habilidad_id=10,
        solhb_anios_experiencia_req=3,
        solhb_es_excluyente=True
    )
    solicitud_mock.habilidades.append(sh)
    
    # 2. Configurar la "Fake DB" usando MagicMock de unittest
    # Hacemos que cuando el servicio haga db.query().filter().first(), retorne nuestro objeto en memoria
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = solicitud_mock

    # 3. Evaluar candidato que NO cumple (solo tiene 1 año de experiencia)
    cand_insuficiente = [{"habilidad_id": 10, "anios_experiencia": 1}]
    
    res = evaluar_candidato_cumple_excluyentes(db_mock, 999, cand_insuficiente)

    # 4. Assertions
    assert res["cumple_excluyentes"] is False
    assert res["descartado_automaticamente"] is True
    assert len(res["habilidades_faltantes"]) == 1
    assert res["habilidades_faltantes"][0]["habilidad_id"] == 10