# app/catalogos/__init__.py
from .models import (
    Pais,
    Region,
    Comuna,
    Habilidad,
    NivelHabilidad,
    Cargo,
    Modalidad,
    TipoContrato,
    Disponibilidad,
    EstadoSolicitud,
    PrioridadSolicitud,
)

__all__ = [
    "Pais",
    "Region",
    "Comuna",
    "Habilidad",
    "NivelHabilidad",
    "Cargo",
    "Modalidad",
    "TipoContrato",
    "Disponibilidad",
    "EstadoSolicitud",
    "PrioridadSolicitud",
]