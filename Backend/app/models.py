from sqlalchemy import Column, Integer, String
from app.database import Base

# ==========================================
# MODELO DE USUARIO (SQLAlchemy)
# ==========================================
# Adaptado exactamente a la estructura de la tabla 'public.usuarios'
# que nos entregó el equipo de Base de Datos.

class Usuario(Base):
    __tablename__ = "usuarios"

    # Llave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)
    
    # Campo 'usuario' (reemplaza al anterior 'nombre' para el login/identificación)
    usuario = Column(String(50), nullable=False)
    
    # Campo 'contrasena' (anteriormente password_hash, mapea directamente la columna de la BD)
    contrasena = Column(String(255), nullable=False)
    
    # Email único e indexado para las búsquedas del login
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Rol asignado para el control de accesos (ADMIN, RECLUTADOR)
    rol = Column(String(30), nullable=False)