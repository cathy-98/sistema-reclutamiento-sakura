from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión al contenedor PostgreSQL de Docker.
# Si tu compañero de DB cambió el usuario, clave o usuario de BD, edítalos aquí.
DATABASE_URL = "postgresql://elitsoft_admin:elitsoft_password_2026@127.0.0.1:5432/db_reclutamiento_elitsoft"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear la fábrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán nuestros modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en los endpoints de FastAPI
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()