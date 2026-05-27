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
# CONFIGURACIÓN DE CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ENDPOINTS
# ==========================================

# 1. Endpoint de Prueba (GET /)
@app.get("/", tags=["Pruebas"])
def verificar_conexion_db(db: Session = Depends(obtener_db)):
    """
    Realiza una consulta de prueba rápida a PostgreSQL en Docker.
    """
    try:
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
    Valida las credenciales de los usuarios comparando la contraseña hash 
    con la nueva columna 'contrasena' de PostgreSQL.
    """
    # 1. Buscamos al usuario en la base de datos por su email
    usuario = db.query(Usuario).filter(Usuario.email == solicitud.email).first()
    
    # 2. Validamos que exista y que la contraseña coincida con 'usuario.contrasena'
    if not usuario or not verificar_password(solicitud.password, usuario.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # 3. Datos que viajarán en el Token (Se utiliza 'usuario.usuario' en vez de nombre)
    datos_token = {
        "sub": usuario.email,
        "rol": usuario.rol,
        "usuario": usuario.usuario
    }
    
    # 4. Generamos el JWT firmado
    token_jwt = crear_token_acceso(datos_token)
    
    # 5. Respondemos al frontend con el TokenResponse adaptado
    return TokenResponse(
        access_token=token_jwt,
        token_type="bearer",
        usuario=usuario.usuario,
        rol=usuario.rol
    )