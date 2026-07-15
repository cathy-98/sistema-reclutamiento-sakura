from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos los enrutadores de nuestros módulos
from app.auth import router as auth_router
from app.usuarios import router as usuarios_router

app = FastAPI(
    title="ATS Elitsoft API",
    description="Backend de Reclutamiento y Selección para Elitsoft - 2026",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde Angular (Puerto 4200)
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los enrutadores en la aplicación principal
app.include_router(auth_router.router)
app.include_router(usuarios_router.router)

@app.get("/")
def health_check():
    return {
        "status": "healthy", 
        "service": "ATS Elitsoft Backend",
        "version": "1.0.0"
    }