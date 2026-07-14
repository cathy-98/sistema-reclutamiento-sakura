import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Local: 127.0.0.1 | Docker Compose: host postgres_db (variable DATABASE_URL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://elitsoft_admin:elitsoft_password_2026@127.0.0.1:5432/db_reclutamiento_elitsoft",
)

# Crear el motor de conexión con optimizaciones
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Evita errores de "Conexión perdida" si la base de datos se reinicia o corta la sesión inactiva
    echo=False           # Cámbialo a True si quieres ver las consultas SQL en vivo en tu consola de Docker mientras desarrollas
)

# Crear la fábrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán nuestros modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
