from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.usuarios.models import Rol, EstadoUsuario, Area, Usuario, Permiso
# Importamos los modelos del catálogo
from app.catalogos.models import (
    Pais, Region, Ciudad, Comuna, Habilidad, NivelHabilidad, 
    Cargo, Modalidad, TipoContrato, Disponibilidad, EstadoSolicitud, PrioridadSolicitud
)
from app.auth.utils import hash_password

def sembrar_datos():
    # Asegúrate de pasar el objeto engine importado desde app.database
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        print("🌱 Iniciando la siembra de datos oficiales en Elitsoft ATS (ID Autoincrementables)...")

        # ==========================================================
        # 1. ESTADOS DE USUARIO (Oficiales)
        # ==========================================================
        estados = [
            {"esusr_nombre": "Activo", "esusr_descripcion": "Usuario habilitado para operar plenamente en la plataforma"},
            {"esusr_nombre": "Inactivo", "esusr_descripcion": "Usuario deshabilitado temporalmente (no puede iniciar sesión)"},
            {"esusr_nombre": "Bloqueado", "esusr_descripcion": "Cuenta suspendida automáticamente por exceso de intentos fallidos."},
            {"esusr_nombre": "Eliminado", "esusr_descripcion": "Usuario borrado de forma lógica para conservar auditoría histórica"}
        ]
        for est in estados:
            existe = db.query(EstadoUsuario).filter(EstadoUsuario.esusr_nombre == est["esusr_nombre"]).first()
            if not existe:
                db.add(EstadoUsuario(**est))

        # ==========================================================
        # 2. ROLES (Oficiales)
        # ==========================================================
        roles = [
            {"rol_nombre": "Administrador", "rol_descripcion": "Administrador total del sistema con acceso global a todos los módulos."},
            {"rol_nombre": "Reclutador", "rol_descripcion": "Usuario que realiza el proceso de reclutamiento"},
            {"rol_nombre": "Entrevistador", "rol_descripcion": "Colaboradores técnicos o líderes de área que realizan entrevistas"}
        ]
        for r in roles:
            existe = db.query(Rol).filter(Rol.rol_nombre == r["rol_nombre"]).first()
            if not existe:
                db.add(Rol(**r))

        # ==========================================================
        # 3. PERMISOS (Oficiales)
        # ==========================================================
        permisos_data = [
            {"per_nombre": "USR_CREATE", "per_descripcion": "Permite registrar nuevos usuarios"},
            {"per_nombre": "USR_UPDATE", "per_descripcion": "Permite modificar usuarios"},
            {"per_nombre": "USR_DELETE", "per_descripcion": "Permite eliminar usuarios"},
            {"per_nombre": "SOL_CREATE", "per_descripcion": "Permite crear solicitudes de empleo"},
            {"per_nombre": "SOL_VIEW", "per_descripcion": "Permite visualizar las vacantes"},
            {"per_nombre": "SOL_UPDATE", "per_descripcion": "Permite editar una vacante"},
            {"per_nombre": "SOL_DELETE", "per_descripcion": "Permite cancelar u ocultar vacantes"},
            {"per_nombre": "CAN_VIEW", "per_descripcion": "Permite visualizar perfiles de candidatos"},
            {"per_nombre": "CAN_UPDATE", "per_descripcion": "Permite actualizar estados del postulante"},
            {"per_nombre": "INT_CREATE", "per_descripcion": "Permite agendar citas de entrevista"},
            {"per_nombre": "CUEST_CREATE", "per_descripcion": "Permite configurar cuestionarios"}
        ]
        for p in permisos_data:
            existe = db.query(Permiso).filter(Permiso.per_nombre == p["per_nombre"]).first()
            if not existe:
                db.add(Permiso(**p))

        # ==========================================================
        # 4. ÁREAS INTERNAS
        # ==========================================================
        areas = [
            {"area_nombre": "Tecnología", "area_descripcion": "Desarrollo, infraestructura y soporte"},
            {"area_nombre": "Recursos Humanos", "area_descripcion": "Reclutamiento y Selección"}
        ]
        for a in areas:
            existe = db.query(Area).filter(Area.area_nombre == a["area_nombre"]).first()
            if not existe:
                db.add(Area(**a))

        db.commit()

        # Asignación de permisos a roles
        rol_admin = db.query(Rol).filter(Rol.rol_nombre == "Administrador").first()
        rol_reclutador = db.query(Rol).filter(Rol.rol_nombre == "Reclutador").first()
        rol_entrevistador = db.query(Rol).filter(Rol.rol_nombre == "Entrevistador").first()
        todos_los_permisos = db.query(Permiso).all()

        if rol_admin and not rol_admin.permisos:
            rol_admin.permisos = todos_los_permisos
        if rol_reclutador and not rol_reclutador.permisos:
            rol_reclutador.permisos = db.query(Permiso).filter(Permiso.per_nombre.in_(["SOL_CREATE", "SOL_VIEW", "SOL_UPDATE", "SOL_DELETE", "CAN_VIEW", "CAN_UPDATE", "INT_CREATE", "CUEST_CREATE"])).all()
        if rol_entrevistador and not rol_entrevistador.permisos:
            rol_entrevistador.permisos = db.query(Permiso).filter(Permiso.per_nombre.in_(["SOL_VIEW", "CAN_VIEW", "INT_CREATE"])).all()
        
        db.commit()

        # ==========================================================
        # 🌟 5. GEOGRAFÍA AVANZADA (Chile: Regiones, Ciudades y Comunas)
        # ==========================================================
        print("🌍 Sembrando datos geográficos avanzados...")
        pais_chile = db.query(Pais).filter(Pais.pais_nombre == "Chile").first()
        if not pais_chile:
            pais_chile = Pais(pais_nombre="Chile")
            db.add(pais_chile)
            db.commit()

        # Diccionario estructurado con Regiones -> Ciudades -> Sus Comunas
        geografia_chile = {
            "Región de Valparaíso": {
                "Valparaíso": ["Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana"],
                "San Antonio": ["San Antonio", "Cartagena", "Santo Domingo"]
            },
            "Región Metropolitana": {
                "Santiago": ["Providencia", "Las Condes", "Santiago", "Ñuñoa", "Vitacura", "Maipú", "La Florida"]
            },
            "Región del Biobío": {
                "Concepción": ["Concepción", "Talcahuano", "San Pedro de la Paz", "Chiguayante", "Coronel"],
                "Los Ángeles": ["Los Ángeles", "Cabrero", "Laja"]
            },
            "Región de la Araucanía": {
                "Temuco": ["Temuco", "Padre Las Casas", "Villarrica", "Pucón"]
            }
        }

        for reg_nombre, ciudades in geografia_chile.items():
            region = db.query(Region).filter(Region.reg_nombre == reg_nombre).first()
            if not region:
                region = Region(reg_nombre=reg_nombre, pais=pais_chile)
                db.add(region)
                db.commit()

            for ciu_nombre, comunas in ciudades.items():
                ciudad = db.query(Ciudad).filter(Ciudad.ciu_nombre == ciu_nombre).first()
                if not ciudad:
                    ciudad = Ciudad(ciu_nombre=ciu_nombre, region=region)
                    db.add(ciudad)
                    db.commit()

                for com_nombre in comunas:
                    existe_com = db.query(Comuna).filter(Comuna.com_nombre == com_nombre).first()
                    if not existe_com:
                        db.add(Comuna(com_nombre=com_nombre, ciudad=ciudad))
        
        db.commit()

        # ==========================================================
        # 🌟 6. CATÁLOGOS TÉCNICOS AJUSTADOS
        # ==========================================================
        print("⚙️ Sembrando parámetros técnicos actualizados...")
        
        # Habilidades Base
        habilidades = ["Python", "Angular", "PostgreSQL", "Docker", "Java", "TypeScript", "AWS", "Git"]
        for hab in habilidades:
            if not db.query(Habilidad).filter(Habilidad.hab_nombre == hab).first():
                db.add(Habilidad(hab_nombre=hab, hab_descripcion=f"Competencia en tecnología {hab}"))

        # Niveles de Habilidad
        niveles = [
            {"nvhb_nombre": "Junior", "nvhb_descripcion": "Conocimientos iniciales", "nvhb_puntaje_base": 10, "nvhb_duracion": 2},
            {"nvhb_nombre": "Semi Senior", "nvhb_descripcion": "Autonomía moderada", "nvhb_puntaje_base": 25, "nvhb_duracion": 3},
            {"nvhb_nombre": "Senior", "nvhb_descripcion": "Dominio experto y liderazgo", "nvhb_puntaje_base": 50, "nvhb_duracion": 5}
        ]
        for nv in niveles:
            if not db.query(NivelHabilidad).filter(NivelHabilidad.nvhb_nombre == nv["nvhb_nombre"]).first():
                db.add(NivelHabilidad(**nv))

        # Cargos
        cargos = ["Desarrollador Fullstack", "Ingeniero DevOps", "Analista QA", "Product Owner", "Frontend Developer", "Backend Developer"]
        for crg in cargos:
            if not db.query(Cargo).filter(Cargo.crgo_nombre == crg).first():
                db.add(Cargo(crgo_nombre=crg, crgo_descripcion=f"Rol profesional de {crg}"))

        # Modalidades
        modalidades = ["Remoto", "Híbrido", "Presencial"]
        for mod in modalidades:
            if not db.query(Modalidad).filter(Modalidad.mdld_nombre == mod).first():
                db.add(Modalidad(mdld_nombre=mod, mdld_descripcion=f"Trabajo en formato {mod}"))

        # Tipos de Contrato
        contratos = ["Indefinido", "Plazo Fijo", "Por Proyecto"]
        for ct in contratos:
            if not db.query(TipoContrato).filter(TipoContrato.tpct_nombre == ct).first():
                db.add(TipoContrato(tpct_nombre=ct, tpct_descripcion=f"Contrato de tipo {ct}"))

        # Disponibilidades (Solicitadas de forma oficial)
        dispo = ["Inmediata", "1 semana", "2 semanas", "3 semanas", "4 semanas"]
        for dp in dispo:
            if not db.query(Disponibilidad).filter(Disponibilidad.disp_nombre == dp).first():
                db.add(Disponibilidad(disp_nombre=dp))

        # Estados de Solicitud (Vacantes)
        estados_sol = [
            {"essl_nombre": "Pendiente", "essl_descripcion": "La solicitud fue creada el Admin y espera ser tomada por Reclutador"},
            {"essl_nombre": "En Curso", "essl_descripcion": "La vacante está activa, publicada y recibiendo postulaciones. Administrada por el Reclutador"},
            {"essl_nombre": "En Entrevistas", "essl_descripcion": "Se cerró la recepción de CVs y los finalistas están en evaluación"},
            {"essl_nombre": "Cancelado", "essl_descripcion": "El proceso se detuvo por decisión del cliente o presupuesto"},
            {"essl_nombre": "Cerrado", "essl_descripcion": "La vacante se completó exitosamente con la contratación del candidato"}
        ]

        for es in estados_sol:
            if not db.query(EstadoSolicitud).filter(EstadoSolicitud.essl_nombre == es["essl_nombre"]).first():
                db.add(EstadoSolicitud(**es))

        # Prioridades de Solicitud
        prioridades = [
            {"prsol_nombre": "Alta", "prsol_descripcion": "Cierre crítico y urgente"},
            {"prsol_nombre": "Media", "prsol_descripcion": "Flujo de reclutamiento estándar"},
            {"prsol_nombre": "Baja", "prsol_descripcion": "Planificación a mediano plazo"}
        ]
        for pr in prioridades:
            if not db.query(PrioridadSolicitud).filter(PrioridadSolicitud.prsol_nombre == pr["prsol_nombre"]).first():
                db.add(PrioridadSolicitud(**pr))

        db.commit()

        # ==========================================================
        # 7. USUARIO ADMINISTRADOR DE PRUEBAS
        # ==========================================================
        admin_email = "admin@elitsoft.cl"
        existe_admin = db.query(Usuario).filter(Usuario.usr_email == admin_email).first()
        if not existe_admin:
            obj_rol_admin = db.query(Rol).filter(Rol.rol_nombre == "Administrador").first()
            obj_estado_activo = db.query(EstadoUsuario).filter(EstadoUsuario.esusr_nombre == "Activo").first()
            obj_area_ti = db.query(Area).filter(Area.area_nombre == "Tecnología").first()

            admin_usuario = Usuario(
                usr_rol_id=obj_rol_admin.rol_id if obj_rol_admin else None,
                usr_estado_usuario_id=obj_estado_activo.esusr_id if obj_estado_activo else None,
                usr_area_id=obj_area_ti.area_id if obj_area_ti else None,
                usr_nombres="Admin",
                usr_apellido_paterno="Elitsoft",
                usr_apellido_materno="ATS",
                usr_rut_sin_dv="12345678",
                usr_dv="5",
                usr_telefono="+56912345678",
                usr_email=admin_email,
                usr_contrasena=hash_password("admin123")
            )
            db.add(admin_usuario)
            db.commit()
            print(f"👑 Usuario Administrador de pruebas creado con éxito!")
        
        print("🎉 ¡Proceso de siembra completo finalizado exitosamente de forma avanzada!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la siembra de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sembrar_datos()