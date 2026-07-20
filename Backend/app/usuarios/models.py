from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Area(Base):
    """Mapea la tabla tbl_area necesaria para la FK de usuario"""
    __tablename__ = "tbl_area"

    area_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_nombre: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    area_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Relación inversa con Usuario
    usuarios: Mapped[list["Usuario"]] = relationship("Usuario", back_populates="area")


class Permiso(Base):
    """Mapea los permisos individuales del sistema (ej: 'CREAR_USUARIO')"""
    __tablename__ = "tbl_permiso"

    per_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    per_nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    per_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Relación Muchos a Muchos con Rol mediante la tabla asociativa
    roles: Mapped[list["Rol"]] = relationship(
        "Rol", secondary="tbl_rol_permiso", back_populates="permisos"
    )


class RolPermiso(Base):
    """Tabla asociativa física intermedia tbl_rol_permiso"""
    __tablename__ = "tbl_rol_permiso"

    rlpm_rol_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_rol.rol_id"), primary_key=True
    )
    rlmp_permiso_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_permiso.per_id"), primary_key=True
    )


class Rol(Base):
    """Mapea los roles del sistema (ej: 'Administrador', 'Reclutador')"""
    __tablename__ = "tbl_rol"

    rol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rol_nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    rol_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Relaciones
    permisos: Mapped[list["Permiso"]] = relationship(
        "Permiso", secondary="tbl_rol_permiso", back_populates="roles"
    )
    usuarios: Mapped[list["Usuario"]] = relationship("Usuario", back_populates="rol")


class EstadoUsuario(Base):
    """Mapea los estados que puede tener un usuario (ej: 'Activo', 'Inactivo')"""
    __tablename__ = "tbl_estado_usuario"

    esusr_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    esusr_nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    esusr_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Relación inversa con Usuario
    usuarios: Mapped[list["Usuario"]] = relationship("Usuario", back_populates="estado")


class Usuario(Base):
    """Mapea los usuarios administrativos o reclutadores de Elitsoft"""
    __tablename__ = "tbl_usuario"

    usr_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usr_rol_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_rol.rol_id"), nullable=True)
    usr_estado_usuario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_estado_usuario.esusr_id"), nullable=True)
    usr_area_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_area.area_id"), nullable=True)
    
    usr_nombres: Mapped[str] = mapped_column(String(15), nullable=False)
    usr_apellido_paterno: Mapped[str] = mapped_column(String(15), nullable=False)
    usr_apellido_materno: Mapped[str | None] = mapped_column(String(15), nullable=True)
    usr_rut_sin_dv: Mapped[str | None] = mapped_column(String(15), nullable=True)
    usr_dv: Mapped[str | None] = mapped_column(String(1), nullable=True)
    usr_telefono: Mapped[str | None] = mapped_column(String(15), nullable=True)
    usr_email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    usr_contrasena: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relaciones del ORM
    rol: Mapped["Rol"] = relationship("Rol", back_populates="usuarios")
    estado: Mapped["EstadoUsuario"] = relationship("EstadoUsuario", back_populates="usuarios")
    area: Mapped["Area"] = relationship("Area", back_populates="usuarios")