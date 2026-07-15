from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.usuarios.models import Rol, EstadoUsuario, Area, Usuario, Permiso
from app.auth.utils import hash_password

def sembrar_datos():
    db: Session = SessionLocal()
    try:
        print("🌱 Iniciando la siembra de datos oficiales en Elitsoft ATS (ID Autoincrementables)...")

        # ==========================================================
        # 1. Crear Estados de Usuario (Oficiales)
        # ==========================================================
        estados = [
            {"esusr_nombre": "Activo", "esusr_descripcion": "Usuario habilitado para operar plenamente en la plataforma"},
            {"esusr_nombre": "Inactivo", "esusr_descripcion": "Usuario deshabilitado temporalmente (no puede iniciar sesión)"},
            {"esusr_nombre": "Bloqueado", "esusr_descripcion": "Cuenta suspendida automáticamente por exceso de intentos fallidos."},
            {"esusr_nombre": "Eliminado", "esusr_descripcion": "Usuario borrado de forma lógica para conservar auditoría histórica"}
        ]
        for est in estados:
            # Buscamos por nombre único para evitar conflictos con IDs auto-incrementales
            existe = db.query(EstadoUsuario).filter(EstadoUsuario.esusr_nombre == est["esusr_nombre"]).first()
            if not existe:
                db.add(EstadoUsuario(**est))
                print(f"✔️ Estado oficial creado: {est['esusr_nombre']}")

        # ==========================================================
        # 2. Crear Roles (Oficiales)
        # ==========================================================
        roles = [
            {"rol_nombre": "Administrador", "rol_descripcion": "Administrador total del sistema con acceso global a todos los módulos."},
            {"rol_nombre": "Reclutador", "rol_descripcion": "Usuario que realiza el proceso de reclutamiento"},
            {"rol_nombre": "Entrevistador", "rol_descripcion": "Colaboradores técnicos o líderes de área que realizan entrevistas"}
        ]
        for r in roles:
            # Buscamos por nombre único
            existe = db.query(Rol).filter(Rol.rol_nombre == r["rol_nombre"]).first()
            if not existe:
                db.add(Rol(**r))
                print(f"✔️ Rol oficial creado: {r['rol_nombre']}")

        # ==========================================================
        # 3. Crear Permisos (Oficiales)
        # ==========================================================
        permisos_data = [
            {"per_nombre": "USR_CREATE", "per_descripcion": "Permite registrar nuevos usuarios y colaboradores en la plataforma"},
            {"per_nombre": "USR_UPDATE", "per_descripcion": "Permite modificar datos de cuentas de usuarios existentes"},
            {"per_nombre": "USR_DELETE", "per_descripcion": "Permite ejecutar la baja lógica de usuarios del sistema"},
            {"per_nombre": "SOL_CREATE", "per_descripcion": "Permite a usuarios crear solicitudes de empleo (vacantes)."},
            {"per_nombre": "SOL_VIEW", "per_descripcion": "Permite a usuarios visualizar las vacantes"},
            {"per_nombre": "SOL_UPDATE", "per_descripcion": "Permite editar datos de una vacante."},
            {"per_nombre": "SOL_DELETE", "per_descripcion": "Permite cancelar, pausar o cerrar solicitudes de empleo"},
            {"per_nombre": "CAN_VIEW", "per_descripcion": "Permite visualizar los perfiles, respuestas y CVs de los candidatos"},
            {"per_nombre": "CAN_UPDATE", "per_descripcion": "Permite actualizar el estado de avance de un postulante en el flujo"},
            {"per_nombre": "INT_CREATE", "per_descripcion": "Permite agendar citas de entrevista y asignar entrevistadores"},
            {"per_nombre": "CUEST_CREATE", "per_descripcion": "Permite configurar el banco de preguntas y reglas de cuestionarios"}
        ]
        for p in permisos_data:
            # Buscamos por nombre único
            existe = db.query(Permiso).filter(Permiso.per_nombre == p["per_nombre"]).first()
            if not existe:
                db.add(Permiso(**p))
                print(f"✔️ Permiso oficial creado: {p['per_nombre']}")

        # ==========================================================
        # 4. Crear Áreas mínimas de apoyo
        # ==========================================================
        areas = [
            {"area_nombre": "Tecnología", "area_descripcion": "Desarrollo, infraestructura y soporte"},
            {"area_nombre": "Recursos Humanos", "area_descripcion": "Reclutamiento y Selección"}
        ]
        for a in areas:
            # Buscamos por nombre único
            existe = db.query(Area).filter(Area.area_nombre == a["area_nombre"]).first()
            if not existe:
                db.add(Area(**a))
                print(f"✔️ Área de soporte creada: {a['area_nombre']}")

        # Confirmamos la inserción de catálogos para que la DB les asigne IDs autoincrementales reales
        db.commit() 

        # ==========================================================
        # 5. Asociar Permisos a los Roles de forma coherente
        # ==========================================================
        # Obtenemos las referencias a los objetos directamente desde la DB usando sus nombres únicos
        rol_admin = db.query(Rol).filter(Rol.rol_nombre == "Administrador").first()
        rol_reclutador = db.query(Rol).filter(Rol.rol_nombre == "Reclutador").first()
        rol_entrevistador = db.query(Rol).filter(Rol.rol_nombre == "Entrevistador").first()

        todos_los_permisos = db.query(Permiso).all()

        # A) Administrador: Tiene TODOS los permisos
        if rol_admin and not rol_admin.permisos:
            rol_admin.permisos = todos_los_permisos
            print("🔗 Todos los permisos asociados al Administrador")

        # B) Reclutador: Gestión de vacantes, candidatos y agendamientos (Permisos de negocio)
        if rol_reclutador and not rol_reclutador.permisos:
            permisos_reclutador = db.query(Permiso).filter(
                Permiso.per_nombre.in_([
                    "SOL_CREATE", "SOL_VIEW", "SOL_UPDATE", "SOL_DELETE",
                    "CAN_VIEW", "CAN_UPDATE", "INT_CREATE", "CUEST_CREATE"
                ])
            ).all()
            rol_reclutador.permisos = permisos_reclutador
            print("🔗 Permisos de negocio asociados al Reclutador")

        # C) Entrevistador: Solo ver vacantes, ver candidatos asignados y agendar entrevistas
        if rol_entrevistador and not rol_entrevistador.permisos:
            permisos_entrevistador = db.query(Permiso).filter(
                Permiso.per_nombre.in_(["SOL_VIEW", "CAN_VIEW", "INT_CREATE"])
            ).all()
            rol_entrevistador.permisos = permisos_entrevistador
            print("🔗 Permisos de lectura y agenda asociados al Entrevistador")

        db.commit()

        # ==========================================================
        # 6. Crear el Usuario Administrador de pruebas
        # ==========================================================
        admin_email = "admin@elitsoft.cl"
        existe_admin = db.query(Usuario).filter(Usuario.usr_email == admin_email).first()
        
        if not existe_admin:
            # Traemos los objetos vinculados que acabamos de guardar para evitar "forzar" IDs numéricos manuales
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
            print(f"👑 Usuario Administrador de pruebas creado con éxito! (admin@elitsoft.cl / admin123)")
        else:
            print("⚠️ El usuario administrador ya existe.")

        print("🎉 ¡Proceso de siembra finalizado exitosamente de forma autoincremental!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la siembra de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sembrar_datos()