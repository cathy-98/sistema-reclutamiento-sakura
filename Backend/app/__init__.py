# app/__init__.py
# Importación limpia de los submódulos con modelos ORM
from app import catalogos
from app import usuarios
from app import clientes
from app import solicitudes

__all__ = ["catalogos", "usuarios", "clientes", "solicitudes"]