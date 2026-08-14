from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.cuestionarios.schemas import CuestionarioCreate, PreguntaCreate, RespuestaSave


def test_porcentaje_cuestionario_valido():
    obj = CuestionarioCreate(
        cues_nombre="QA",
        cues_descripcion="Prueba",
        cues_porcentaje_aprobacion=Decimal("70"),
        cues_solicitud_id=1,
    )
    assert obj.cues_porcentaje_aprobacion == Decimal("70")


def test_porcentaje_fuera_de_rango():
    with pytest.raises(ValidationError):
        CuestionarioCreate(
            cues_nombre="QA",
            cues_porcentaje_aprobacion=Decimal("101"),
            cues_solicitud_id=1,
        )


def test_pregunta_schema():
    obj = PreguntaCreate(
        preg_texto_pregunta="Pregunta QA",
        preg_habilidad_id=1,
        preg_nivel_habilidad_id=3,
    )
    assert obj.preg_texto_pregunta == "Pregunta QA"


def test_respuesta_schema():
    obj = RespuestaSave(pregunta_cuestionario_id=1, opcion_respuesta_id=2)
    assert obj.opcion_respuesta_id == 2
