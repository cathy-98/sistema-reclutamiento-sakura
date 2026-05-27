from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import obtener_db
from app.models import Usuario
from app.schemas import LoginRequest, TokenResponse
from app.security import verificar_password, crear_token_acceso

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="P&E Platform - API de Autenticación",
    description="Servidor de servicios backend para el Sprint 0 de la plataforma P&E",
    version="1.0.0"
)

# ==========================================
# CONFIGURACIÓN DE CORS (¡Crucial para Angular!)
# ==========================================
# Permite que la aplicación frontend (Angular) alojada en el puerto 4200
# pueda realizar peticiones HTTP sin ser bloqueada por las políticas del navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ENDPOINTS / RUTAS DE LA API
# ==========================================

# 1. Endpoint de Prueba de Base de Datos (GET /)
@app.get("/", tags=["Pruebas"])
def verificar_conexion_db(db: Session = Depends(obtener_db)):
    """
    Realiza una consulta de prueba rápida a PostgreSQL en Docker
    para asegurar que la conexión en el puerto 5432 esté 100% activa.
    """
    try:
        # Ejecuta una instrucción SQL nativa simple
        db.execute(text("SELECT 1"))
        return {
            "estado": "¡Al abordaje! Backend activo y conectado a PostgreSQL",
            "puerto_db": 5432,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con la base de datos de Docker: {str(e)}"
        )


# 2. Endpoint de Login (POST /api/auth/login)
@app.post(
    "/api/auth/login", 
    response_model=TokenResponse, 
    tags=["Autenticación"]
)
def login(
    solicitud: LoginRequest, 
    db: Session = Depends(obtener_db)
):
    """
    Valida las credenciales de los usuarios. Si son correctas, genera un
    token JWT firmado con su rol para permitir la navegación segura en Angular.
    """
    # 1. Buscamos al usuario en la base de datos por su email
    usuario = db.query(Usuario).filter(Usuario.email == solicitud.email).first()
    
    # 2. Validamos que el usuario exista y que el Hash de la clave coincida
    if not usuario or not verificar_password(solicitud.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # 3. Datos del usuario que viajarán encriptados en el Token (Payload)
    datos_token = {
        "sub": usuario.email,
        "rol": usuario.rol,
        "nombre": usuario.nombre
    }
    
    # 4. Generamos el JWT firmado
    token_jwt = crear_token_acceso(datos_token)
    
    # 5. Retornamos la respuesta esperada por el Frontend
    return TokenResponse(
        access_token=token_jwt,
        token_type="bearer",
        nombre=usuario.nombre,
        rol=usuario.rol
    )