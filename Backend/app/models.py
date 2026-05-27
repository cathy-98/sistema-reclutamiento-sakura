from sqlalchemy import Column, Integer, String
from app.database import Base

# ==========================================
# MODELO DE USUARIO (SQLAlchemy)
# ==========================================
# Define la estructura exacta de la tabla "usuarios" en PostgreSQL.
# Se utiliza para realizar consultas y persistir información desde Python.

class Usuario(Base):
    __tablename__ = "usuarios"

    # Llave primaria autoincremental
    id = Column(Integer, primary_key=True, index=True)
    
    # Email único e indexado para búsquedas ultra rápidas en el login
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Hash de la contraseña (nunca guardamos texto plano en la BD)
    password_hash = Column(String, nullable=False)
    
    # Nombre completo del usuario
    nombre = Column(String, nullable=False)
    
    # Rol asignado para el control de accesos (ADMIN, RECLUTADOR)
    rol = Column(String, default="RECLUTADOR", nullable=False)