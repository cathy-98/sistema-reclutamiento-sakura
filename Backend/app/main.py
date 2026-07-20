from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos los enrutadores de nuestros módulos
from app.auth import router as auth_router
from app.usuarios import router as usuarios_router
# 🌟 NUEVO FECHA 20/07/2026: Importar el enrutador de catálogos
from app.catalogos import router as catalogos_router

# 🌟 NUEVO FECHA 20/07/2026: Forzar a SQLAlchemy a registrar los nuevos modelos relacionales geográficos
from app.catalogos import models as catalogos_models

app = FastAPI( # Instancia de FastAPI
    title="Reclutamiento y Selección Sakura Backend API",
    description="Backend de Reclutamiento y Selección para Sakura - 2026",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde Angular (Puerto 4200)
# CORS es para permitir que las peticiones se hagan desde Angular (Puerto 4200)
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware( # Añadir el middleware de CORS  
    CORSMiddleware,
    allow_origins=origins, # Permitir peticiones desde Angular (Puerto 4200)
    allow_credentials=True, # Permitir credenciales
    allow_methods=["*"], # Permitir todos los métodos
    allow_headers=["*"], # Permitir todos los headers
)

# Registrar los enrutadores en la aplicación principal
app.include_router(auth_router.router) # Registrar el enrutador de autenticación
app.include_router(usuarios_router.router) # Registrar el enrutador de usuarios
# 🌟 NUEVO: Fechas 20/07/2026: Registrar el enrutador de catálogos en FastAPI
app.include_router(catalogos_router.router) # Registrar el enrutador de catálogos

@app.get("/")
def health_check(): # Endpoint para verificar el estado de la aplicación
    return {
        "status": "healthy", # Estado de la aplicación
        "service": "Reclutamiento y Selección Sakura Backend", # Nombre del servicio
        "version": "1.0.0" # Versión de la aplicación  
    }