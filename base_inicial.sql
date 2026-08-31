--
-- PostgreSQL database dump
--

\restrict QxoTx3f0RRc8mzfUmYZOba4AO4FbmAMG7KPcNadJ0J6bV4A7D2F1ahPGp8fz0HW

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.tbl_plantilla_notificacion DROP CONSTRAINT IF EXISTS tbl_plantilla_notificacion_plnt_usuario_actualizacion_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_notificacion_reclutamiento DROP CONSTRAINT IF EXISTS tbl_notificacion_reclutamiento_ntfr_usuario_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_notificacion_reclutamiento DROP CONSTRAINT IF EXISTS tbl_notificacion_reclutamiento_ntfr_solicitud_candidato_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_documento_reporte_candidato DROP CONSTRAINT IF EXISTS tbl_documento_reporte_candidato_drcp_usuario_generador_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_documento_reporte_candidato DROP CONSTRAINT IF EXISTS tbl_documento_reporte_candidat_drcp_solicitud_candidato_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_idioma DROP CONSTRAINT IF EXISTS tbl_candidato_idioma_cdio_idioma_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_idioma DROP CONSTRAINT IF EXISTS tbl_candidato_idioma_cdio_candidato_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario DROP CONSTRAINT IF EXISTS fk_tbl_usuario_rol;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato DROP CONSTRAINT IF EXISTS fk_tbl_usuario_estado_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario DROP CONSTRAINT IF EXISTS fk_tbl_usuario_estado;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_usuario_cita_entrevista_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_usuario_cita_entrevista_tipo;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_usuario_cita_entrevista_cita;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario DROP CONSTRAINT IF EXISTS fk_tbl_usuario_area;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_usuario_creador;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_usuario_asignado;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_tipo_contrato;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_prioridad;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_modalidad;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_habilidad_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_habilidad_nivel;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_habilidad_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_estado;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_cliente;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_cargo;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_candidato_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_candidato_motivo_rechazo;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_candidato_estado;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS fk_tbl_solicitud_candidato_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_rol_permiso DROP CONSTRAINT IF EXISTS fk_tbl_rol_permiso_rol;
ALTER TABLE IF EXISTS ONLY public.tbl_rol_permiso DROP CONSTRAINT IF EXISTS fk_tbl_rol_permiso_permiso;
ALTER TABLE IF EXISTS ONLY public.tbl_respuesta_pregunta DROP CONSTRAINT IF EXISTS fk_tbl_respuesta_pregunta_pregunta_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_respuesta_pregunta DROP CONSTRAINT IF EXISTS fk_tbl_respuesta_pregunta_opcion_respuesta;
ALTER TABLE IF EXISTS ONLY public.tbl_respuesta_pregunta DROP CONSTRAINT IF EXISTS fk_tbl_respuesta_pregunta_candidato_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_region DROP CONSTRAINT IF EXISTS fk_tbl_region_pais;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta DROP CONSTRAINT IF EXISTS fk_tbl_pregunta_nivel_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta DROP CONSTRAINT IF EXISTS fk_tbl_pregunta_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta_cuestionario DROP CONSTRAINT IF EXISTS fk_tbl_pregunta_cuestionario_pregunta;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta_cuestionario DROP CONSTRAINT IF EXISTS fk_tbl_pregunta_cuestionario_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_password_reset_token DROP CONSTRAINT IF EXISTS fk_tbl_password_reset_token_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_opcion_respuesta DROP CONSTRAINT IF EXISTS fk_tbl_opcion_respuesta_pregunta;
ALTER TABLE IF EXISTS ONLY public.tbl_institucion DROP CONSTRAINT IF EXISTS fk_tbl_institucion_tipo_institucion;
ALTER TABLE IF EXISTS ONLY public.tbl_historial_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_historial_solicitud_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_historial_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_historial_solicitud_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_historial_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_historial_solicitud_estado_anterior;
ALTER TABLE IF EXISTS ONLY public.tbl_historial_solicitud DROP CONSTRAINT IF EXISTS fk_tbl_historial_solicitud_estado_actual;
ALTER TABLE IF EXISTS ONLY public.tbl_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_habilidad_categoria_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_expl_habilidad_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_expl_habilidad_experiencia;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral DROP CONSTRAINT IF EXISTS fk_tbl_experiencia_laboral_empresa;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral DROP CONSTRAINT IF EXISTS fk_tbl_experiencia_laboral_cargo;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral DROP CONSTRAINT IF EXISTS fk_tbl_experiencia_laboral_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_evaluacion_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_evaluacion_entrevista_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_evaluacion_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_evaluacion_entrevista_tipo;
ALTER TABLE IF EXISTS ONLY public.tbl_evaluacion_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_evaluacion_entrevista_resultado;
ALTER TABLE IF EXISTS ONLY public.tbl_evaluacion_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_evaluacion_entrevista_cita;
ALTER TABLE IF EXISTS ONLY public.tbl_estudio_candidato DROP CONSTRAINT IF EXISTS fk_tbl_estudio_candidato_nivel_educacional;
ALTER TABLE IF EXISTS ONLY public.tbl_estudio_candidato DROP CONSTRAINT IF EXISTS fk_tbl_estudio_candidato_institucion;
ALTER TABLE IF EXISTS ONLY public.tbl_estudio_candidato DROP CONSTRAINT IF EXISTS fk_tbl_estudio_candidato_carrera;
ALTER TABLE IF EXISTS ONLY public.tbl_estudio_candidato DROP CONSTRAINT IF EXISTS fk_tbl_estudio_candidato_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_direccion_candidato DROP CONSTRAINT IF EXISTS fk_tbl_direccion_candidato_comuna;
ALTER TABLE IF EXISTS ONLY public.tbl_direccion_candidato DROP CONSTRAINT IF EXISTS fk_tbl_direccion_candidato_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_curso DROP CONSTRAINT IF EXISTS fk_tbl_curso_institucion;
ALTER TABLE IF EXISTS ONLY public.tbl_curso DROP CONSTRAINT IF EXISTS fk_tbl_curso_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_cuestionario DROP CONSTRAINT IF EXISTS fk_tbl_cuestionario_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_comuna DROP CONSTRAINT IF EXISTS fk_tbl_comuna_region;
ALTER TABLE IF EXISTS ONLY public.tbl_cliente DROP CONSTRAINT IF EXISTS fk_tbl_cliente_empresa;
ALTER TABLE IF EXISTS ONLY public.tbl_cliente DROP CONSTRAINT IF EXISTS fk_tbl_cliente_cargo_empresa;
ALTER TABLE IF EXISTS ONLY public.tbl_cliente DROP CONSTRAINT IF EXISTS fk_tbl_cliente_area_empresa;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_tipo_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_cita_tipo_entrevista_tipo_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_tipo_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_cita_tipo_entrevista_cita;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_cita_entrevista_usuario_creador;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_cita_entrevista_tipo;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_cita_entrevista_solicitud_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_entrevista DROP CONSTRAINT IF EXISTS fk_tbl_cita_entrevista_estado;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_idioma DROP CONSTRAINT IF EXISTS fk_tbl_candidato_idioma_nivel;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_candidato_habilidad_nivel;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_candidato_habilidad_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_habilidad DROP CONSTRAINT IF EXISTS fk_tbl_candidato_habilidad_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato DROP CONSTRAINT IF EXISTS fk_tbl_candidato_disponibilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_cuestionario DROP CONSTRAINT IF EXISTS fk_tbl_candidato_cuestionario_estado;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_cuestionario DROP CONSTRAINT IF EXISTS fk_tbl_candidato_cuestionario_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_cuestionario DROP CONSTRAINT IF EXISTS fk_tbl_candidato_cuestionario_candidato;
DROP INDEX IF EXISTS public.uq_m5_evaluacion_cita_usuario_tipo;
DROP INDEX IF EXISTS public.ix_tbl_solicitud_candidato_solicitud_estado;
DROP INDEX IF EXISTS public.ix_tbl_notificacion_postulacion;
DROP INDEX IF EXISTS public.ix_tbl_notificacion_fecha;
DROP INDEX IF EXISTS public.ix_tbl_notificacion_estado;
DROP INDEX IF EXISTS public.ix_tbl_nivel_idioma_grupo;
DROP INDEX IF EXISTS public.ix_tbl_nivel_idioma_activo_orden;
DROP INDEX IF EXISTS public.ix_tbl_habilidad_categoria;
DROP INDEX IF EXISTS public.ix_tbl_documento_reporte_postulacion;
DROP INDEX IF EXISTS public.ix_tbl_documento_reporte_fecha;
DROP INDEX IF EXISTS public.ix_tbl_candidato_idioma_nivel;
DROP INDEX IF EXISTS public.ix_tbl_candidato_idioma_candidato;
DROP INDEX IF EXISTS public.ix_tbl_candidato_email_lower;
DROP INDEX IF EXISTS public.ix_password_reset_usuario;
DROP INDEX IF EXISTS public.ix_password_reset_expiracion;
DROP INDEX IF EXISTS public.idx_tbl_usuario_rol;
DROP INDEX IF EXISTS public.idx_tbl_usuario_nombre_completo;
DROP INDEX IF EXISTS public.idx_tbl_usuario_estado;
DROP INDEX IF EXISTS public.idx_tbl_usuario_email;
DROP INDEX IF EXISTS public.idx_tbl_usuario_cita_entrevista_usuario;
DROP INDEX IF EXISTS public.idx_tbl_usuario_cita_entrevista_cita;
DROP INDEX IF EXISTS public.idx_tbl_usuario_area;
DROP INDEX IF EXISTS public.idx_tbl_usuario_apellidos;
DROP INDEX IF EXISTS public.idx_tbl_tipo_institucion_nombre;
DROP INDEX IF EXISTS public.idx_tbl_tipo_entrevista_nombre;
DROP INDEX IF EXISTS public.idx_tbl_tipo_contrato_nombre;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_usuario_creador;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_usuario_asignado;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_tipo_contrato;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_prioridad;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_modalidad;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_habilidad_solicitud;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_habilidad_nivel;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_habilidad_habilidad;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_habilidad_excluyente;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_fecha_inicio_busqueda;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_fecha_creacion;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_fecha_cierre_busqueda;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_estado;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_codigo;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_cliente;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_cargo;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_candidato_solicitud;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_candidato_puntaje;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_candidato_motivo_rechazo;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_candidato_fecha_postulacion;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_candidato_estado;
DROP INDEX IF EXISTS public.idx_tbl_solicitud_candidato_candidato;
DROP INDEX IF EXISTS public.idx_tbl_rol_permiso_rol;
DROP INDEX IF EXISTS public.idx_tbl_rol_permiso_permiso;
DROP INDEX IF EXISTS public.idx_tbl_rol_nombre;
DROP INDEX IF EXISTS public.idx_tbl_respuesta_pregunta_pregunta_cuestionario;
DROP INDEX IF EXISTS public.idx_tbl_respuesta_pregunta_opcion_respuesta;
DROP INDEX IF EXISTS public.idx_tbl_respuesta_pregunta_correcta;
DROP INDEX IF EXISTS public.idx_tbl_respuesta_pregunta_candidato_cuestionario;
DROP INDEX IF EXISTS public.idx_tbl_respuesta_asignacion;
DROP INDEX IF EXISTS public.idx_tbl_region_pais;
DROP INDEX IF EXISTS public.idx_tbl_region_nombre;
DROP INDEX IF EXISTS public.idx_tbl_prioridad_solicitud_nombre;
DROP INDEX IF EXISTS public.idx_tbl_pregunta_nivel_habilidad;
DROP INDEX IF EXISTS public.idx_tbl_pregunta_habilidad;
DROP INDEX IF EXISTS public.idx_tbl_pregunta_fecha_creacion;
DROP INDEX IF EXISTS public.idx_tbl_pregunta_cuestionario_pregunta;
DROP INDEX IF EXISTS public.idx_tbl_pregunta_cuestionario_cuestionario;
DROP INDEX IF EXISTS public.idx_tbl_permiso_nombre;
DROP INDEX IF EXISTS public.idx_tbl_pais_nombre;
DROP INDEX IF EXISTS public.idx_tbl_opcion_respuesta_pregunta;
DROP INDEX IF EXISTS public.idx_tbl_opcion_respuesta_correcta;
DROP INDEX IF EXISTS public.idx_tbl_nombre_resultado_nombre;
DROP INDEX IF EXISTS public.idx_tbl_nivel_habilidad_puntaje;
DROP INDEX IF EXISTS public.idx_tbl_nivel_habilidad_nombre;
DROP INDEX IF EXISTS public.idx_tbl_nivel_educacional_nombre;
DROP INDEX IF EXISTS public.idx_tbl_motivo_rechazo_nombre;
DROP INDEX IF EXISTS public.idx_tbl_modalidad_nombre;
DROP INDEX IF EXISTS public.idx_tbl_institucion_tipo;
DROP INDEX IF EXISTS public.idx_tbl_institucion_nombre;
DROP INDEX IF EXISTS public.idx_tbl_historial_solicitud_usuario;
DROP INDEX IF EXISTS public.idx_tbl_historial_solicitud_solicitud;
DROP INDEX IF EXISTS public.idx_tbl_historial_solicitud_fecha_cambio;
DROP INDEX IF EXISTS public.idx_tbl_historial_solicitud_estado_anterior;
DROP INDEX IF EXISTS public.idx_tbl_historial_solicitud_estado_actual;
DROP INDEX IF EXISTS public.idx_tbl_habilidad_nombre;
DROP INDEX IF EXISTS public.idx_tbl_expl_habilidad_habilidad;
DROP INDEX IF EXISTS public.idx_tbl_expl_habilidad_experiencia;
DROP INDEX IF EXISTS public.idx_tbl_experiencia_laboral_fecha_inicio;
DROP INDEX IF EXISTS public.idx_tbl_experiencia_laboral_fecha_fin;
DROP INDEX IF EXISTS public.idx_tbl_experiencia_laboral_empresa;
DROP INDEX IF EXISTS public.idx_tbl_experiencia_laboral_cargo;
DROP INDEX IF EXISTS public.idx_tbl_experiencia_laboral_candidato;
DROP INDEX IF EXISTS public.idx_tbl_evaluacion_entrevista_resultado;
DROP INDEX IF EXISTS public.idx_tbl_evaluacion_entrevista_cita;
DROP INDEX IF EXISTS public.idx_tbl_estudio_candidato_nivel_educacional;
DROP INDEX IF EXISTS public.idx_tbl_estudio_candidato_institucion;
DROP INDEX IF EXISTS public.idx_tbl_estudio_candidato_fecha_inicio;
DROP INDEX IF EXISTS public.idx_tbl_estudio_candidato_fecha_fin;
DROP INDEX IF EXISTS public.idx_tbl_estudio_candidato_carrera;
DROP INDEX IF EXISTS public.idx_tbl_estudio_candidato_candidato;
DROP INDEX IF EXISTS public.idx_tbl_estado_usuario_nombre;
DROP INDEX IF EXISTS public.idx_tbl_estado_solicitud_nombre;
DROP INDEX IF EXISTS public.idx_tbl_estado_solicitud_candidato_nombre;
DROP INDEX IF EXISTS public.idx_tbl_estado_entrevista_nombre;
DROP INDEX IF EXISTS public.idx_tbl_estado_cuestionario_candidato_nombre;
DROP INDEX IF EXISTS public.idx_tbl_empresa_nombre;
DROP INDEX IF EXISTS public.idx_tbl_empresa_identificacion;
DROP INDEX IF EXISTS public.idx_tbl_disponibilidad_nombre;
DROP INDEX IF EXISTS public.idx_tbl_direccion_candidato_comuna;
DROP INDEX IF EXISTS public.idx_tbl_direccion_candidato_candidato;
DROP INDEX IF EXISTS public.idx_tbl_direccion_candidato_calle;
DROP INDEX IF EXISTS public.idx_tbl_curso_nombre;
DROP INDEX IF EXISTS public.idx_tbl_curso_institucion;
DROP INDEX IF EXISTS public.idx_tbl_curso_candidato;
DROP INDEX IF EXISTS public.idx_tbl_curso_anio;
DROP INDEX IF EXISTS public.idx_tbl_cuestionario_solicitud;
DROP INDEX IF EXISTS public.idx_tbl_cuestionario_porcentaje_aprobacion;
DROP INDEX IF EXISTS public.idx_tbl_cuestionario_nombre;
DROP INDEX IF EXISTS public.idx_tbl_comuna_nombre;
DROP INDEX IF EXISTS public.idx_tbl_comuna_ciudad;
DROP INDEX IF EXISTS public.idx_tbl_cliente_nombre;
DROP INDEX IF EXISTS public.idx_tbl_cliente_empresa;
DROP INDEX IF EXISTS public.idx_tbl_cliente_email;
DROP INDEX IF EXISTS public.idx_tbl_cliente_cargo_empresa;
DROP INDEX IF EXISTS public.idx_tbl_cliente_area_empresa;
DROP INDEX IF EXISTS public.idx_tbl_cita_tipo_entrevista_tipo;
DROP INDEX IF EXISTS public.idx_tbl_cita_tipo_entrevista_cita;
DROP INDEX IF EXISTS public.idx_tbl_cita_entrevista_tipo;
DROP INDEX IF EXISTS public.idx_tbl_cita_entrevista_solicitud_candidato;
DROP INDEX IF EXISTS public.idx_tbl_cita_entrevista_fecha_inicio;
DROP INDEX IF EXISTS public.idx_tbl_cita_entrevista_fecha_fin;
DROP INDEX IF EXISTS public.idx_tbl_cita_entrevista_fecha_creacion;
DROP INDEX IF EXISTS public.idx_tbl_cita_entrevista_estado;
DROP INDEX IF EXISTS public.idx_tbl_carrera_nombre;
DROP INDEX IF EXISTS public.idx_tbl_cargo_nombre;
DROP INDEX IF EXISTS public.idx_tbl_candidato_titulo;
DROP INDEX IF EXISTS public.idx_tbl_candidato_habilidad_nivel;
DROP INDEX IF EXISTS public.idx_tbl_candidato_habilidad_habilidad;
DROP INDEX IF EXISTS public.idx_tbl_candidato_habilidad_candidato;
DROP INDEX IF EXISTS public.idx_tbl_candidato_habilidad_anios;
DROP INDEX IF EXISTS public.idx_tbl_candidato_fecha_creacion;
DROP INDEX IF EXISTS public.idx_tbl_candidato_email;
DROP INDEX IF EXISTS public.idx_tbl_candidato_disponibilidad;
DROP INDEX IF EXISTS public.idx_tbl_candidato_cuestionario_fecha_asignacion;
DROP INDEX IF EXISTS public.idx_tbl_candidato_cuestionario_estado;
DROP INDEX IF EXISTS public.idx_tbl_candidato_cuestionario_cuestionario;
DROP INDEX IF EXISTS public.idx_tbl_candidato_cuestionario_candidato;
DROP INDEX IF EXISTS public.idx_tbl_candidato_cuestionario_aprobado;
DROP INDEX IF EXISTS public.idx_tbl_candidato_apellidos;
DROP INDEX IF EXISTS public.idx_tbl_area_nombre;
DROP INDEX IF EXISTS public.idx_m5_usuario_cita_usuario;
DROP INDEX IF EXISTS public.idx_m5_usuario_cita_tipo;
DROP INDEX IF EXISTS public.idx_m5_eval_cita;
DROP INDEX IF EXISTS public.idx_m5_cita_slcd;
DROP INDEX IF EXISTS public.idx_m5_cita_fecha;
DROP INDEX IF EXISTS public.idx_m5_cita_estado;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario DROP CONSTRAINT IF EXISTS uq_tbl_usuario_rut;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario DROP CONSTRAINT IF EXISTS uq_tbl_usuario_email;
ALTER TABLE IF EXISTS ONLY public.tbl_tipo_institucion DROP CONSTRAINT IF EXISTS uq_tbl_tipo_institucion_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_tipo_entrevista DROP CONSTRAINT IF EXISTS uq_tbl_tipo_entrevista_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_tipo_contrato DROP CONSTRAINT IF EXISTS uq_tbl_tipo_contrato_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_habilidad DROP CONSTRAINT IF EXISTS uq_tbl_solicitud_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS uq_tbl_solicitud_codigo;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS uq_tbl_solicitud_candidato_solicitud_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS uq_tbl_solicitud_candidato_postulacion;
ALTER TABLE IF EXISTS ONLY public.tbl_rol DROP CONSTRAINT IF EXISTS uq_tbl_rol_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_respuesta_pregunta DROP CONSTRAINT IF EXISTS uq_tbl_respuesta_pregunta_candidato_pregunta;
ALTER TABLE IF EXISTS ONLY public.tbl_respuesta_pregunta DROP CONSTRAINT IF EXISTS uq_tbl_respuesta_asignacion_pregunta;
ALTER TABLE IF EXISTS ONLY public.tbl_region DROP CONSTRAINT IF EXISTS uq_tbl_region_pais_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_prioridad_solicitud DROP CONSTRAINT IF EXISTS uq_tbl_prioridad_solicitud_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta DROP CONSTRAINT IF EXISTS uq_tbl_pregunta_texto_habilidad_nivel;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta_cuestionario DROP CONSTRAINT IF EXISTS uq_tbl_pregunta_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_plantilla_notificacion DROP CONSTRAINT IF EXISTS uq_tbl_plantilla_notificacion_tipo;
ALTER TABLE IF EXISTS ONLY public.tbl_permiso DROP CONSTRAINT IF EXISTS uq_tbl_permiso_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_password_reset_token DROP CONSTRAINT IF EXISTS uq_tbl_password_reset_token_hash;
ALTER TABLE IF EXISTS ONLY public.tbl_pais DROP CONSTRAINT IF EXISTS uq_tbl_pais_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_opcion_respuesta DROP CONSTRAINT IF EXISTS uq_tbl_opcion_respuesta_pregunta_opcion;
ALTER TABLE IF EXISTS ONLY public.tbl_nombre_resultado DROP CONSTRAINT IF EXISTS uq_tbl_nombre_resultado_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_idioma DROP CONSTRAINT IF EXISTS uq_tbl_nivel_idioma_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_idioma DROP CONSTRAINT IF EXISTS uq_tbl_nivel_idioma_codigo;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_habilidad DROP CONSTRAINT IF EXISTS uq_tbl_nivel_habilidad_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_educacional DROP CONSTRAINT IF EXISTS uq_tbl_nivel_educacional_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_motivo_rechazo DROP CONSTRAINT IF EXISTS uq_tbl_motivo_rechazo_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_modalidad DROP CONSTRAINT IF EXISTS uq_tbl_modalidad_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_institucion DROP CONSTRAINT IF EXISTS uq_tbl_institucion_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_idioma DROP CONSTRAINT IF EXISTS uq_tbl_idioma_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_habilidad DROP CONSTRAINT IF EXISTS uq_tbl_habilidad_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral DROP CONSTRAINT IF EXISTS uq_tbl_experiencia_laboral_registro;
ALTER TABLE IF EXISTS ONLY public.tbl_estudio_candidato DROP CONSTRAINT IF EXISTS uq_tbl_estudio_candidato_registro;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_usuario DROP CONSTRAINT IF EXISTS uq_tbl_estado_usuario_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_solicitud DROP CONSTRAINT IF EXISTS uq_tbl_estado_solicitud_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_solicitud_candidato DROP CONSTRAINT IF EXISTS uq_tbl_estado_solicitud_candidato_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_entrevista DROP CONSTRAINT IF EXISTS uq_tbl_estado_entrevista_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_cuestionario_candidato DROP CONSTRAINT IF EXISTS uq_tbl_estado_cuestionario_candidato_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_empresa DROP CONSTRAINT IF EXISTS uq_tbl_empresa_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_empresa DROP CONSTRAINT IF EXISTS uq_tbl_empresa_identificacion;
ALTER TABLE IF EXISTS ONLY public.tbl_disponibilidad DROP CONSTRAINT IF EXISTS uq_tbl_disponibilidad_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_direccion_candidato DROP CONSTRAINT IF EXISTS uq_tbl_direccion_candidato_direccion;
ALTER TABLE IF EXISTS ONLY public.tbl_curso DROP CONSTRAINT IF EXISTS uq_tbl_curso_candidato_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_cuestionario DROP CONSTRAINT IF EXISTS uq_tbl_cuestionario_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_comuna DROP CONSTRAINT IF EXISTS uq_tbl_comuna_comuna_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_cliente DROP CONSTRAINT IF EXISTS uq_tbl_cliente_email2;
ALTER TABLE IF EXISTS ONLY public.tbl_cliente DROP CONSTRAINT IF EXISTS uq_tbl_cliente_email;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_entrevista DROP CONSTRAINT IF EXISTS uq_tbl_cita_entrevista_agenda;
ALTER TABLE IF EXISTS ONLY public.tbl_categoria_habilidad DROP CONSTRAINT IF EXISTS uq_tbl_categoria_habilidad_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_carrera DROP CONSTRAINT IF EXISTS uq_tbl_carrera_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_cargo DROP CONSTRAINT IF EXISTS uq_tbl_cargo_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato DROP CONSTRAINT IF EXISTS uq_tbl_candidato_rut;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_idioma DROP CONSTRAINT IF EXISTS uq_tbl_candidato_idioma;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_habilidad DROP CONSTRAINT IF EXISTS uq_tbl_candidato_habilidad_candidato_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_habilidad DROP CONSTRAINT IF EXISTS uq_tbl_candidato_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato DROP CONSTRAINT IF EXISTS uq_tbl_candidato_email;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_cuestionario DROP CONSTRAINT IF EXISTS uq_tbl_candidato_cuestionario_candidato_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_area DROP CONSTRAINT IF EXISTS uq_tbl_area_nombre;
ALTER TABLE IF EXISTS ONLY public.tbl_plantilla_notificacion DROP CONSTRAINT IF EXISTS tbl_plantilla_notificacion_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_password_reset_token DROP CONSTRAINT IF EXISTS tbl_password_reset_token_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_notificacion_reclutamiento DROP CONSTRAINT IF EXISTS tbl_notificacion_reclutamiento_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_idioma DROP CONSTRAINT IF EXISTS tbl_nivel_idioma_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_idioma DROP CONSTRAINT IF EXISTS tbl_idioma_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_documento_reporte_candidato DROP CONSTRAINT IF EXISTS tbl_documento_reporte_candidato_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_categoria_habilidad DROP CONSTRAINT IF EXISTS tbl_categoria_habilidad_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_idioma DROP CONSTRAINT IF EXISTS tbl_candidato_idioma_pkey;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario_cita_entrevista DROP CONSTRAINT IF EXISTS pk_tbl_usuario_cita_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_usuario DROP CONSTRAINT IF EXISTS pk_tbl_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_tipo_institucion DROP CONSTRAINT IF EXISTS pk_tbl_tipo_institucion;
ALTER TABLE IF EXISTS ONLY public.tbl_tipo_entrevista DROP CONSTRAINT IF EXISTS pk_tbl_tipo_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_tipo_contrato DROP CONSTRAINT IF EXISTS pk_tbl_tipo_contrato;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_habilidad DROP CONSTRAINT IF EXISTS pk_tbl_solicitud_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud_candidato DROP CONSTRAINT IF EXISTS pk_tbl_solicitud_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_solicitud DROP CONSTRAINT IF EXISTS pk_tbl_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_rol_permiso DROP CONSTRAINT IF EXISTS pk_tbl_rol_permiso;
ALTER TABLE IF EXISTS ONLY public.tbl_rol DROP CONSTRAINT IF EXISTS pk_tbl_rol;
ALTER TABLE IF EXISTS ONLY public.tbl_respuesta_pregunta DROP CONSTRAINT IF EXISTS pk_tbl_respuesta_pregunta;
ALTER TABLE IF EXISTS ONLY public.tbl_region DROP CONSTRAINT IF EXISTS pk_tbl_region;
ALTER TABLE IF EXISTS ONLY public.tbl_prioridad_solicitud DROP CONSTRAINT IF EXISTS pk_tbl_prioridad_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta_cuestionario DROP CONSTRAINT IF EXISTS pk_tbl_pregunta_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_pregunta DROP CONSTRAINT IF EXISTS pk_tbl_pregunta;
ALTER TABLE IF EXISTS ONLY public.tbl_permiso DROP CONSTRAINT IF EXISTS pk_tbl_permiso;
ALTER TABLE IF EXISTS ONLY public.tbl_pais DROP CONSTRAINT IF EXISTS pk_tbl_pais;
ALTER TABLE IF EXISTS ONLY public.tbl_opcion_respuesta DROP CONSTRAINT IF EXISTS pk_tbl_opcion_respuesta;
ALTER TABLE IF EXISTS ONLY public.tbl_nombre_resultado DROP CONSTRAINT IF EXISTS pk_tbl_nombre_resultado;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_habilidad DROP CONSTRAINT IF EXISTS pk_tbl_nivel_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_nivel_educacional DROP CONSTRAINT IF EXISTS pk_tbl_nivel_educacional;
ALTER TABLE IF EXISTS ONLY public.tbl_motivo_rechazo DROP CONSTRAINT IF EXISTS pk_tbl_motivo_rechazo;
ALTER TABLE IF EXISTS ONLY public.tbl_modalidad DROP CONSTRAINT IF EXISTS pk_tbl_modalidad;
ALTER TABLE IF EXISTS ONLY public.tbl_institucion DROP CONSTRAINT IF EXISTS pk_tbl_institucion;
ALTER TABLE IF EXISTS ONLY public.tbl_historial_solicitud DROP CONSTRAINT IF EXISTS pk_tbl_historial_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_habilidad DROP CONSTRAINT IF EXISTS pk_tbl_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral_habilidad DROP CONSTRAINT IF EXISTS pk_tbl_experiencia_laboral_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_experiencia_laboral DROP CONSTRAINT IF EXISTS pk_tbl_experiencia_laboral;
ALTER TABLE IF EXISTS ONLY public.tbl_evaluacion_entrevista DROP CONSTRAINT IF EXISTS pk_tbl_evaluacion_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_estudio_candidato DROP CONSTRAINT IF EXISTS pk_tbl_estudio_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_usuario DROP CONSTRAINT IF EXISTS pk_tbl_estado_usuario;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_solicitud_candidato DROP CONSTRAINT IF EXISTS pk_tbl_estado_solicitud_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_solicitud DROP CONSTRAINT IF EXISTS pk_tbl_estado_solicitud;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_entrevista DROP CONSTRAINT IF EXISTS pk_tbl_estado_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_estado_cuestionario_candidato DROP CONSTRAINT IF EXISTS pk_tbl_estado_cuestionario_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_empresa DROP CONSTRAINT IF EXISTS pk_tbl_empresa;
ALTER TABLE IF EXISTS ONLY public.tbl_disponibilidad DROP CONSTRAINT IF EXISTS pk_tbl_disponibilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_direccion_candidato DROP CONSTRAINT IF EXISTS pk_tbl_direccion_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_curso DROP CONSTRAINT IF EXISTS pk_tbl_curso;
ALTER TABLE IF EXISTS ONLY public.tbl_cuestionario DROP CONSTRAINT IF EXISTS pk_tbl_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_comuna DROP CONSTRAINT IF EXISTS pk_tbl_comuna;
ALTER TABLE IF EXISTS ONLY public.tbl_cliente DROP CONSTRAINT IF EXISTS pk_tbl_cliente;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_tipo_entrevista DROP CONSTRAINT IF EXISTS pk_tbl_cita_tipo_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_cita_entrevista DROP CONSTRAINT IF EXISTS pk_tbl_cita_entrevista;
ALTER TABLE IF EXISTS ONLY public.tbl_carrera DROP CONSTRAINT IF EXISTS pk_tbl_carrera;
ALTER TABLE IF EXISTS ONLY public.tbl_cargo DROP CONSTRAINT IF EXISTS pk_tbl_cargo;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_habilidad DROP CONSTRAINT IF EXISTS pk_tbl_candidato_habilidad;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato_cuestionario DROP CONSTRAINT IF EXISTS pk_tbl_candidato_cuestionario;
ALTER TABLE IF EXISTS ONLY public.tbl_candidato DROP CONSTRAINT IF EXISTS pk_tbl_candidato;
ALTER TABLE IF EXISTS ONLY public.tbl_area DROP CONSTRAINT IF EXISTS pk_tbl_area;
DROP TABLE IF EXISTS public.tbl_usuario_cita_entrevista;
DROP TABLE IF EXISTS public.tbl_usuario;
DROP TABLE IF EXISTS public.tbl_tipo_institucion;
DROP TABLE IF EXISTS public.tbl_tipo_entrevista;
DROP TABLE IF EXISTS public.tbl_tipo_contrato;
DROP TABLE IF EXISTS public.tbl_solicitud_habilidad;
DROP TABLE IF EXISTS public.tbl_solicitud_candidato;
DROP TABLE IF EXISTS public.tbl_solicitud;
DROP TABLE IF EXISTS public.tbl_rol_permiso;
DROP TABLE IF EXISTS public.tbl_rol;
DROP TABLE IF EXISTS public.tbl_respuesta_pregunta;
DROP TABLE IF EXISTS public.tbl_region;
DROP TABLE IF EXISTS public.tbl_prioridad_solicitud;
DROP TABLE IF EXISTS public.tbl_pregunta_cuestionario;
DROP TABLE IF EXISTS public.tbl_pregunta;
DROP TABLE IF EXISTS public.tbl_plantilla_notificacion;
DROP TABLE IF EXISTS public.tbl_permiso;
DROP TABLE IF EXISTS public.tbl_password_reset_token;
DROP TABLE IF EXISTS public.tbl_pais;
DROP TABLE IF EXISTS public.tbl_opcion_respuesta;
DROP TABLE IF EXISTS public.tbl_notificacion_reclutamiento;
DROP TABLE IF EXISTS public.tbl_nombre_resultado;
DROP TABLE IF EXISTS public.tbl_nivel_idioma;
DROP TABLE IF EXISTS public.tbl_nivel_habilidad;
DROP TABLE IF EXISTS public.tbl_nivel_educacional;
DROP TABLE IF EXISTS public.tbl_motivo_rechazo;
DROP TABLE IF EXISTS public.tbl_modalidad;
DROP TABLE IF EXISTS public.tbl_institucion;
DROP TABLE IF EXISTS public.tbl_idioma;
DROP TABLE IF EXISTS public.tbl_historial_solicitud;
DROP TABLE IF EXISTS public.tbl_habilidad;
DROP TABLE IF EXISTS public.tbl_experiencia_laboral_habilidad;
DROP TABLE IF EXISTS public.tbl_experiencia_laboral;
DROP TABLE IF EXISTS public.tbl_evaluacion_entrevista;
DROP TABLE IF EXISTS public.tbl_estudio_candidato;
DROP TABLE IF EXISTS public.tbl_estado_usuario;
DROP TABLE IF EXISTS public.tbl_estado_solicitud_candidato;
DROP TABLE IF EXISTS public.tbl_estado_solicitud;
DROP TABLE IF EXISTS public.tbl_estado_entrevista;
DROP TABLE IF EXISTS public.tbl_estado_cuestionario_candidato;
DROP TABLE IF EXISTS public.tbl_empresa;
DROP TABLE IF EXISTS public.tbl_documento_reporte_candidato;
DROP TABLE IF EXISTS public.tbl_disponibilidad;
DROP TABLE IF EXISTS public.tbl_direccion_candidato;
DROP TABLE IF EXISTS public.tbl_curso;
DROP TABLE IF EXISTS public.tbl_cuestionario;
DROP TABLE IF EXISTS public.tbl_comuna;
DROP TABLE IF EXISTS public.tbl_cliente;
DROP TABLE IF EXISTS public.tbl_cita_tipo_entrevista;
DROP TABLE IF EXISTS public.tbl_cita_entrevista;
DROP TABLE IF EXISTS public.tbl_categoria_habilidad;
DROP TABLE IF EXISTS public.tbl_carrera;
DROP TABLE IF EXISTS public.tbl_cargo;
DROP TABLE IF EXISTS public.tbl_candidato_idioma;
DROP TABLE IF EXISTS public.tbl_candidato_habilidad;
DROP TABLE IF EXISTS public.tbl_candidato_cuestionario;
DROP TABLE IF EXISTS public.tbl_candidato;
DROP TABLE IF EXISTS public.tbl_area;
DROP EXTENSION IF EXISTS unaccent;
DROP EXTENSION IF EXISTS pgcrypto;
-- *not* dropping schema, since initdb creates it
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: elitsoft_admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO elitsoft_admin;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: elitsoft_admin
--

COMMENT ON SCHEMA public IS '';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tbl_area; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_area (
    area_id integer NOT NULL,
    area_nombre character varying(50),
    area_descripcion character varying(300),
    CONSTRAINT chk_tbl_area_descripcion_vacia CHECK (((area_descripcion IS NULL) OR (TRIM(BOTH FROM area_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_area_nombre_vacio CHECK ((TRIM(BOTH FROM area_nombre) <> ''::text))
);


ALTER TABLE public.tbl_area OWNER TO elitsoft_admin;

--
-- Name: tbl_area_area_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_area ALTER COLUMN area_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_area_area_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato (
    cand_id integer NOT NULL,
    cand_email character varying(255),
    cand_password character varying(255),
    cand_nombres character varying(20),
    cand_apellido_paterno character varying(20),
    cand_apellido_materno character varying(20),
    cand_fecha_nacimiento date,
    cand_telefono character varying(20),
    cand_rut_sin_dv integer,
    cand_dv integer,
    cand_disponibilidad_id integer,
    cand_resumen_profesional character varying(300),
    cand_fecha_creacion timestamp without time zone,
    cand_url_1 character varying(300),
    cand_titulo character varying(300),
    cand_estado_usuario_id integer,
    cand_cv_urls character varying(2000),
    CONSTRAINT chk_tbl_candidato_apellido_paterno_vacio CHECK ((TRIM(BOTH FROM cand_apellido_paterno) <> ''::text)),
    CONSTRAINT chk_tbl_candidato_dv CHECK ((((cand_dv >= 0) AND (cand_dv <= 9)) OR (cand_dv = 10))),
    CONSTRAINT chk_tbl_candidato_email_vacio CHECK ((TRIM(BOTH FROM cand_email) <> ''::text)),
    CONSTRAINT chk_tbl_candidato_fecha_nacimiento CHECK ((cand_fecha_nacimiento <= CURRENT_DATE)),
    CONSTRAINT chk_tbl_candidato_nombres_vacio CHECK ((TRIM(BOTH FROM cand_nombres) <> ''::text)),
    CONSTRAINT chk_tbl_candidato_rut CHECK ((cand_rut_sin_dv > 0))
);


ALTER TABLE public.tbl_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_cand_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato ALTER COLUMN cand_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_cand_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_cuestionario (
    cdcu_id integer NOT NULL,
    cdcu_candidato_id integer,
    cdcu_cuestionario_id integer,
    cdcu_fecha_asignacion timestamp without time zone,
    cdcu_fecha_resolucion timestamp without time zone,
    cdcu_porcentaje_obtenido numeric(5,2),
    cdcu_estado_cuestionario_candidato_id integer,
    cdcu_tiempo_utilizado integer,
    cdcu_permitir_reintento boolean DEFAULT false NOT NULL,
    cdcu_aprobado boolean,
    cdcu_fecha_inicio timestamp without time zone,
    cdcu_fecha_vencimiento timestamp without time zone NOT NULL,
    CONSTRAINT chk_tbl_candidato_cuestionario_fechas CHECK (((cdcu_fecha_resolucion IS NULL) OR (cdcu_fecha_resolucion >= cdcu_fecha_asignacion))),
    CONSTRAINT chk_tbl_candidato_cuestionario_porcentaje CHECK (((cdcu_porcentaje_obtenido IS NULL) OR ((cdcu_porcentaje_obtenido >= (0)::numeric) AND (cdcu_porcentaje_obtenido <= (100)::numeric)))),
    CONSTRAINT chk_tbl_candidato_cuestionario_tiempo CHECK (((cdcu_tiempo_utilizado IS NULL) OR (cdcu_tiempo_utilizado >= 0)))
);


ALTER TABLE public.tbl_candidato_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_cuestionario_cdcu_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato_cuestionario ALTER COLUMN cdcu_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_cuestionario_cdcu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_habilidad (
    cdhb_id integer NOT NULL,
    cdhb_candidato_id integer,
    cdhb_habilidad_id integer,
    cdhb_nivel_habilidad_id integer,
    cdhb_anios_experiencia integer,
    CONSTRAINT chk_tbl_candidato_habilidad_anios CHECK ((cdhb_anios_experiencia >= 0))
);


ALTER TABLE public.tbl_candidato_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_candidato_habilidad_cdhb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato_habilidad ALTER COLUMN cdhb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_habilidad_cdhb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_candidato_idioma; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_candidato_idioma (
    cdio_id integer NOT NULL,
    cdio_candidato_id integer NOT NULL,
    cdio_idioma_id integer NOT NULL,
    cdio_nivel_idioma_id integer NOT NULL
);


ALTER TABLE public.tbl_candidato_idioma OWNER TO elitsoft_admin;

--
-- Name: COLUMN tbl_candidato_idioma.cdio_nivel_idioma_id; Type: COMMENT; Schema: public; Owner: elitsoft_admin
--

COMMENT ON COLUMN public.tbl_candidato_idioma.cdio_nivel_idioma_id IS 'Nivel normalizado del idioma del candidato. FK a tbl_nivel_idioma.';


--
-- Name: tbl_candidato_idioma_cdio_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_candidato_idioma ALTER COLUMN cdio_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_candidato_idioma_cdio_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cargo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cargo (
    crgo_id integer NOT NULL,
    crgo_nombre character varying(50),
    crgo_descripcion character varying(300),
    CONSTRAINT chk_tbl_cargo_descripcion_vacia CHECK (((crgo_descripcion IS NULL) OR (TRIM(BOTH FROM crgo_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_cargo_nombre_vacio CHECK ((TRIM(BOTH FROM crgo_nombre) <> ''::text))
);


ALTER TABLE public.tbl_cargo OWNER TO elitsoft_admin;

--
-- Name: tbl_cargo_crgo_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cargo ALTER COLUMN crgo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cargo_crgo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_carrera; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_carrera (
    crra_id integer NOT NULL,
    crra_nombre character varying(255),
    CONSTRAINT chk_tbl_carrera_nombre_vacio CHECK ((TRIM(BOTH FROM crra_nombre) <> ''::text))
);


ALTER TABLE public.tbl_carrera OWNER TO elitsoft_admin;

--
-- Name: tbl_carrera_crra_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_carrera ALTER COLUMN crra_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_carrera_crra_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_categoria_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_categoria_habilidad (
    cthb_id integer NOT NULL,
    cthb_nombre character varying(100) NOT NULL,
    cthb_descripcion character varying(300),
    CONSTRAINT chk_tbl_categoria_habilidad_nombre CHECK ((TRIM(BOTH FROM cthb_nombre) <> ''::text))
);


ALTER TABLE public.tbl_categoria_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_categoria_habilidad_cthb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_categoria_habilidad ALTER COLUMN cthb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_categoria_habilidad_cthb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cita_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cita_entrevista (
    ctev_id integer NOT NULL,
    ctev_solicitud_candidato_id integer,
    ctev_tipo_entrevista_id integer,
    ctev_estado_entrevista_id integer,
    ctev_fecha_hora_inicio timestamp without time zone,
    ctev_fecha_hora_fin timestamp without time zone,
    ctev_fecha_creacion timestamp without time zone,
    ctev_enlace_reunion character varying(300),
    ctev_comentarios_convocatoria character varying(300),
    ctev_titulo_evento character varying(300),
    ctev_usuario_creador_id integer,
    ctev_fecha_actualizacion timestamp without time zone,
    ctev_motivo_estado character varying(300),
    CONSTRAINT chk_tbl_cita_entrevista_enlace CHECK (((ctev_enlace_reunion IS NULL) OR (length(TRIM(BOTH FROM ctev_enlace_reunion)) > 0))),
    CONSTRAINT chk_tbl_cita_entrevista_fechas CHECK (((ctev_fecha_hora_fin IS NULL) OR (ctev_fecha_hora_inicio < ctev_fecha_hora_fin))),
    CONSTRAINT chk_tbl_cita_entrevista_titulo CHECK ((TRIM(BOTH FROM ctev_titulo_evento) <> ''::text))
);


ALTER TABLE public.tbl_cita_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_cita_entrevista_ctev_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cita_entrevista ALTER COLUMN ctev_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cita_entrevista_ctev_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cita_tipo_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cita_tipo_entrevista (
    cten_tipo_entrevista_id integer NOT NULL,
    cten_cita_entrevista_id integer NOT NULL
);


ALTER TABLE public.tbl_cita_tipo_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_cliente; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cliente (
    cli_id integer NOT NULL,
    cli_nombre character varying(30),
    cli_cargo_empresa_id integer,
    cli_area_empresa_id integer,
    cli_email character varying(100),
    cli_email2 character varying(100),
    cli_telefono1 character varying(12),
    cli_telefono2 character varying(12),
    cli_empresa_id integer,
    CONSTRAINT chk_tbl_cliente_email2_formato CHECK (((cli_email2 IS NULL) OR ((cli_email2)::text ~~ '%@%.%'::text))),
    CONSTRAINT chk_tbl_cliente_email_diferentes CHECK (((cli_email2 IS NULL) OR ((cli_email)::text <> (cli_email2)::text))),
    CONSTRAINT chk_tbl_cliente_email_formato CHECK (((cli_email IS NULL) OR ((cli_email)::text ~~ '%@%.%'::text))),
    CONSTRAINT chk_tbl_cliente_nombre_vacio CHECK ((TRIM(BOTH FROM cli_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_cliente_telefono_diferentes CHECK (((cli_telefono2 IS NULL) OR ((cli_telefono1)::text <> (cli_telefono2)::text)))
);


ALTER TABLE public.tbl_cliente OWNER TO elitsoft_admin;

--
-- Name: tbl_cliente_cli_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cliente ALTER COLUMN cli_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cliente_cli_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_comuna; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_comuna (
    com_id integer NOT NULL,
    com_region_id integer,
    com_nombre character varying(100),
    CONSTRAINT chk_tbl_comuna_nombre_vacio CHECK ((TRIM(BOTH FROM com_nombre) <> ''::text))
);


ALTER TABLE public.tbl_comuna OWNER TO elitsoft_admin;

--
-- Name: tbl_comuna_com_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_comuna ALTER COLUMN com_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_comuna_com_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_cuestionario (
    cues_id integer NOT NULL,
    cues_nombre character varying(300),
    cues_descripcion character varying(300),
    cues_porcentaje_aprobacion numeric(5,2),
    cues_solicitud_id integer,
    CONSTRAINT chk_tbl_cuestionario_nombre CHECK ((TRIM(BOTH FROM cues_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_cuestionario_porcentaje_aprobacion CHECK (((cues_porcentaje_aprobacion >= (0)::numeric) AND (cues_porcentaje_aprobacion <= (100)::numeric)))
);


ALTER TABLE public.tbl_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_cuestionario_cues_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_cuestionario ALTER COLUMN cues_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_cuestionario_cues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_curso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_curso (
    curs_id integer NOT NULL,
    curs_candidato_id integer,
    curs_nombre_curso character varying(40),
    curs_institucion_id integer,
    curs_es_certificado boolean,
    curs_anio_curso integer,
    CONSTRAINT chk_tbl_curso_anio CHECK (((curs_anio_curso IS NULL) OR ((curs_anio_curso >= 1900) AND ((curs_anio_curso)::numeric <= EXTRACT(year FROM CURRENT_DATE))))),
    CONSTRAINT chk_tbl_curso_nombre_vacio CHECK ((TRIM(BOTH FROM curs_nombre_curso) <> ''::text))
);


ALTER TABLE public.tbl_curso OWNER TO elitsoft_admin;

--
-- Name: tbl_curso_curs_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_curso ALTER COLUMN curs_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_curso_curs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_direccion_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_direccion_candidato (
    drcd_id integer NOT NULL,
    drcd_candidato_id integer,
    drcd_comuna_id integer,
    drcd_calle character varying(40),
    drcd_numero integer,
    drcd_dpto_oficina character varying(10),
    CONSTRAINT chk_tbl_direccion_candidato_calle CHECK ((TRIM(BOTH FROM drcd_calle) <> ''::text)),
    CONSTRAINT chk_tbl_direccion_candidato_numero CHECK ((drcd_numero > 0))
);


ALTER TABLE public.tbl_direccion_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_direccion_candidato_drcd_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_direccion_candidato ALTER COLUMN drcd_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_direccion_candidato_drcd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_disponibilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_disponibilidad (
    disp_id integer NOT NULL,
    disp_nombre character varying(40),
    CONSTRAINT chk_tbl_disponibilidad_nombre_vacio CHECK ((TRIM(BOTH FROM disp_nombre) <> ''::text))
);


ALTER TABLE public.tbl_disponibilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_disponibilidad_disp_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_disponibilidad ALTER COLUMN disp_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_disponibilidad_disp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_documento_reporte_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_documento_reporte_candidato (
    drcp_id integer NOT NULL,
    drcp_solicitud_candidato_id integer NOT NULL,
    drcp_tipo_documento character varying(30) NOT NULL,
    drcp_nombre_archivo character varying(255) NOT NULL,
    drcp_ruta_archivo character varying(1000) NOT NULL,
    drcp_fecha_generacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    drcp_usuario_generador_id integer NOT NULL,
    drcp_hash_sha256 character varying(64) NOT NULL,
    drcp_snapshot_json jsonb,
    CONSTRAINT chk_tbl_documento_reporte_hash CHECK ((length((drcp_hash_sha256)::text) = 64)),
    CONSTRAINT chk_tbl_documento_reporte_nombre CHECK ((TRIM(BOTH FROM drcp_nombre_archivo) <> ''::text)),
    CONSTRAINT chk_tbl_documento_reporte_tipo CHECK (((drcp_tipo_documento)::text = ANY ((ARRAY['RESUMEN'::character varying, 'CV_CORPORATIVO'::character varying])::text[])))
);


ALTER TABLE public.tbl_documento_reporte_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_documento_reporte_candidato_drcp_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_documento_reporte_candidato ALTER COLUMN drcp_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_documento_reporte_candidato_drcp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_empresa; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_empresa (
    emp_id integer NOT NULL,
    emp_nombre character varying(30),
    emp_identificacion character varying(15),
    CONSTRAINT chk_tbl_empresa_identificacion_vacia CHECK ((TRIM(BOTH FROM emp_identificacion) <> ''::text)),
    CONSTRAINT chk_tbl_empresa_nombre_vacio CHECK ((TRIM(BOTH FROM emp_nombre) <> ''::text))
);


ALTER TABLE public.tbl_empresa OWNER TO elitsoft_admin;

--
-- Name: tbl_empresa_emp_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_empresa ALTER COLUMN emp_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_empresa_emp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_cuestionario_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_cuestionario_candidato (
    escc_id integer NOT NULL,
    escc_nombre character varying(40),
    CONSTRAINT chk_tbl_estado_cuestionario_candidato_nombre CHECK ((TRIM(BOTH FROM escc_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_cuestionario_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_cuestionario_candidato_escc_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_cuestionario_candidato ALTER COLUMN escc_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_cuestionario_candidato_escc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_entrevista (
    esev_id integer NOT NULL,
    esev_nombre character varying(40),
    esev_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_entrevista_nombre CHECK ((TRIM(BOTH FROM esev_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_entrevista_esev_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_entrevista ALTER COLUMN esev_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_entrevista_esev_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_solicitud (
    essl_id integer NOT NULL,
    essl_nombre character varying(20),
    essl_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_solicitud_descripcion_vacia CHECK (((essl_descripcion IS NULL) OR (TRIM(BOTH FROM essl_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_estado_solicitud_nombre_vacio CHECK ((TRIM(BOTH FROM essl_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_solicitud_candidato (
    essc_id integer NOT NULL,
    essc_nombre character varying(40),
    essc_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_solicitud_candidato_nombre CHECK ((TRIM(BOTH FROM essc_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_solicitud_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_solicitud_candidato_essc_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_solicitud_candidato ALTER COLUMN essc_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_solicitud_candidato_essc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_solicitud_essl_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_solicitud ALTER COLUMN essl_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_solicitud_essl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estado_usuario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estado_usuario (
    esusr_id integer NOT NULL,
    esusr_nombre character varying(20),
    esusr_descripcion character varying(300),
    CONSTRAINT chk_tbl_estado_usuario_descripcion_vacia CHECK (((esusr_descripcion IS NULL) OR (TRIM(BOTH FROM esusr_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_estado_usuario_nombre_vacio CHECK ((TRIM(BOTH FROM esusr_nombre) <> ''::text))
);


ALTER TABLE public.tbl_estado_usuario OWNER TO elitsoft_admin;

--
-- Name: tbl_estado_usuario_esusr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estado_usuario ALTER COLUMN esusr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estado_usuario_esusr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_estudio_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_estudio_candidato (
    etcd_id integer NOT NULL,
    etcd_candidato_id integer,
    etcd_nivel_educacional_id integer,
    etcd_institucion_id integer,
    etcd_carrera_id integer,
    etcd_fecha_inicio date,
    etcd_fecha_fin date,
    CONSTRAINT chk_tbl_estudio_candidato_fechas CHECK (((etcd_fecha_fin IS NULL) OR (etcd_fecha_inicio <= etcd_fecha_fin)))
);


ALTER TABLE public.tbl_estudio_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_estudio_candidato_etcd_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_estudio_candidato ALTER COLUMN etcd_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_estudio_candidato_etcd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_evaluacion_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_evaluacion_entrevista (
    even_id integer NOT NULL,
    even_nombre_resultado_id integer,
    even_observacion character varying(300),
    even_cita_entrevista_id integer,
    even_usuario_id integer,
    even_tipo_entrevista_id integer,
    even_fecha_creacion timestamp without time zone,
    even_fecha_actualizacion timestamp without time zone,
    CONSTRAINT chk_tbl_evaluacion_entrevista_observacion CHECK (((even_observacion IS NULL) OR (length(TRIM(BOTH FROM even_observacion)) > 0)))
);


ALTER TABLE public.tbl_evaluacion_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_evaluacion_entrevista_even_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_evaluacion_entrevista ALTER COLUMN even_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_evaluacion_entrevista_even_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_experiencia_laboral; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_experiencia_laboral (
    expl_id integer NOT NULL,
    expl_candidato_id integer,
    expl_empresa_id integer,
    expl_cargo_id integer,
    expl_descripcion_funciones character varying(300),
    expl_fecha_inicio date,
    expl_fecha_fin date,
    CONSTRAINT chk_tbl_experiencia_laboral_descripcion CHECK ((TRIM(BOTH FROM expl_descripcion_funciones) <> ''::text)),
    CONSTRAINT chk_tbl_experiencia_laboral_fechas CHECK (((expl_fecha_fin IS NULL) OR (expl_fecha_inicio <= expl_fecha_fin)))
);


ALTER TABLE public.tbl_experiencia_laboral OWNER TO elitsoft_admin;

--
-- Name: tbl_experiencia_laboral_expl_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_experiencia_laboral ALTER COLUMN expl_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_experiencia_laboral_expl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_experiencia_laboral_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_experiencia_laboral_habilidad (
    exph_experiencia_laboral_id integer NOT NULL,
    exph_habilidad_id integer NOT NULL
);


ALTER TABLE public.tbl_experiencia_laboral_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_habilidad (
    hab_id integer NOT NULL,
    hab_nombre character varying(255),
    hab_descripcion character varying(300),
    hab_categoria_habilidad_id integer,
    CONSTRAINT chk_tbl_habilidad_nombre_vacio CHECK ((TRIM(BOTH FROM hab_nombre) <> ''::text))
);


ALTER TABLE public.tbl_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_habilidad_hab_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_habilidad ALTER COLUMN hab_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_habilidad_hab_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_historial_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_historial_solicitud (
    hsol_id integer NOT NULL,
    hsol_solicitud_id integer,
    hsol_estado_anterior_id integer,
    hsol_estado_actual_id integer,
    hsol_fecha_cambio timestamp without time zone,
    hsol_usuario_id integer,
    hsol_comentario character varying(300),
    CONSTRAINT chk_tbl_historial_solicitud_comentario_vacio CHECK (((hsol_comentario IS NULL) OR (TRIM(BOTH FROM hsol_comentario) <> ''::text))),
    CONSTRAINT chk_tbl_historial_solicitud_estados_diferentes CHECK (((hsol_estado_anterior_id IS NULL) OR (hsol_estado_actual_id IS NULL) OR (hsol_estado_anterior_id <> hsol_estado_actual_id)))
);


ALTER TABLE public.tbl_historial_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_historial_solicitud_hsol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_historial_solicitud ALTER COLUMN hsol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_historial_solicitud_hsol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_idioma; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_idioma (
    idio_id integer NOT NULL,
    idio_nombre character varying(100) NOT NULL,
    CONSTRAINT chk_tbl_idioma_nombre CHECK ((TRIM(BOTH FROM idio_nombre) <> ''::text))
);


ALTER TABLE public.tbl_idioma OWNER TO elitsoft_admin;

--
-- Name: tbl_idioma_idio_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_idioma ALTER COLUMN idio_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_idioma_idio_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_institucion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_institucion (
    inst_id integer NOT NULL,
    inst_nombre character varying(40),
    inst_tipo_institucion_id integer,
    CONSTRAINT chk_tbl_institucion_nombre_vacio CHECK ((TRIM(BOTH FROM inst_nombre) <> ''::text))
);


ALTER TABLE public.tbl_institucion OWNER TO elitsoft_admin;

--
-- Name: tbl_institucion_inst_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_institucion ALTER COLUMN inst_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_institucion_inst_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_modalidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_modalidad (
    mdld_id integer NOT NULL,
    mdld_nombre character varying(20),
    mdld_descripcion character varying(300),
    CONSTRAINT chk_tbl_modalidad_descripcion_vacia CHECK (((mdld_descripcion IS NULL) OR (TRIM(BOTH FROM mdld_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_modalidad_nombre_vacio CHECK ((TRIM(BOTH FROM mdld_nombre) <> ''::text))
);


ALTER TABLE public.tbl_modalidad OWNER TO elitsoft_admin;

--
-- Name: tbl_modalidad_mdld_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_modalidad ALTER COLUMN mdld_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_modalidad_mdld_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_motivo_rechazo; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_motivo_rechazo (
    mtrc_id integer NOT NULL,
    mtrc_nombre character varying(40),
    mtrc_descripcion character varying(300),
    CONSTRAINT chk_tbl_motivo_rechazo_nombre CHECK ((TRIM(BOTH FROM mtrc_nombre) <> ''::text))
);


ALTER TABLE public.tbl_motivo_rechazo OWNER TO elitsoft_admin;

--
-- Name: tbl_motivo_rechazo_mtrc_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_motivo_rechazo ALTER COLUMN mtrc_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_motivo_rechazo_mtrc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nivel_educacional; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_educacional (
    nved_id integer NOT NULL,
    nved_nombre character varying(40),
    CONSTRAINT chk_tbl_nivel_educacional_nombre_vacio CHECK ((TRIM(BOTH FROM nved_nombre) <> ''::text))
);


ALTER TABLE public.tbl_nivel_educacional OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_educacional_nved_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nivel_educacional ALTER COLUMN nved_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nivel_educacional_nved_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nivel_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_habilidad (
    nvhb_id integer NOT NULL,
    nvhb_nombre character varying(20),
    nvhb_descripcion character varying(300),
    nvhb_puntaje_base integer,
    nvhb_duracion integer,
    CONSTRAINT chk_tbl_nivel_habilidad_duracion CHECK ((nvhb_duracion >= 0)),
    CONSTRAINT chk_tbl_nivel_habilidad_nombre_vacio CHECK ((TRIM(BOTH FROM nvhb_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_nivel_habilidad_puntaje CHECK ((nvhb_puntaje_base >= 0))
);


ALTER TABLE public.tbl_nivel_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_nivel_habilidad_nvhb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nivel_habilidad ALTER COLUMN nvhb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nivel_habilidad_nvhb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nivel_idioma; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nivel_idioma (
    nvid_id integer NOT NULL,
    nvid_codigo character varying(20) NOT NULL,
    nvid_nombre character varying(100) NOT NULL,
    nvid_grupo character varying(30) NOT NULL,
    nvid_es_generico boolean DEFAULT false NOT NULL,
    nvid_orden integer NOT NULL,
    nvid_descripcion character varying(255),
    nvid_activo boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_tbl_nivel_idioma_codigo CHECK ((TRIM(BOTH FROM nvid_codigo) <> ''::text)),
    CONSTRAINT chk_tbl_nivel_idioma_grupo CHECK (((nvid_grupo)::text = ANY ((ARRAY['Basico'::character varying, 'Intermedio'::character varying, 'Avanzado'::character varying, 'Nativo'::character varying])::text[]))),
    CONSTRAINT chk_tbl_nivel_idioma_nombre CHECK ((TRIM(BOTH FROM nvid_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_nivel_idioma_orden CHECK ((nvid_orden > 0))
);


ALTER TABLE public.tbl_nivel_idioma OWNER TO elitsoft_admin;

--
-- Name: TABLE tbl_nivel_idioma; Type: COMMENT; Schema: public; Owner: elitsoft_admin
--

COMMENT ON TABLE public.tbl_nivel_idioma IS 'Cat├ílogo normalizado de niveles de dominio de idiomas. Incluye niveles gen├®ricos hist├│ricos y niveles CEFR.';


--
-- Name: COLUMN tbl_nivel_idioma.nvid_codigo; Type: COMMENT; Schema: public; Owner: elitsoft_admin
--

COMMENT ON COLUMN public.tbl_nivel_idioma.nvid_codigo IS 'C├│digo estable del nivel. Ejemplos: BAS, A1, A2, INT, B1, B2, AVA, C1, C2, NAT.';


--
-- Name: COLUMN tbl_nivel_idioma.nvid_grupo; Type: COMMENT; Schema: public; Owner: elitsoft_admin
--

COMMENT ON COLUMN public.tbl_nivel_idioma.nvid_grupo IS 'Grupo funcional resumido utilizado por Sakura: Basico, Intermedio, Avanzado o Nativo.';


--
-- Name: COLUMN tbl_nivel_idioma.nvid_es_generico; Type: COMMENT; Schema: public; Owner: elitsoft_admin
--

COMMENT ON COLUMN public.tbl_nivel_idioma.nvid_es_generico IS 'TRUE cuando el nivel representa una clasificaci├│n general sin precisi├│n CEFR.';


--
-- Name: tbl_nivel_idioma_nvid_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nivel_idioma ALTER COLUMN nvid_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nivel_idioma_nvid_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_nombre_resultado; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_nombre_resultado (
    nore_id integer NOT NULL,
    nore_nombre character varying(40),
    CONSTRAINT chk_tbl_nombre_resultado_nombre CHECK ((TRIM(BOTH FROM nore_nombre) <> ''::text))
);


ALTER TABLE public.tbl_nombre_resultado OWNER TO elitsoft_admin;

--
-- Name: tbl_nombre_resultado_nore_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_nombre_resultado ALTER COLUMN nore_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_nombre_resultado_nore_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_notificacion_reclutamiento; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_notificacion_reclutamiento (
    ntfr_id integer NOT NULL,
    ntfr_solicitud_candidato_id integer NOT NULL,
    ntfr_tipo character varying(30) NOT NULL,
    ntfr_destinatario character varying(2000) NOT NULL,
    ntfr_cc character varying(2000),
    ntfr_asunto character varying(300) NOT NULL,
    ntfr_cuerpo text NOT NULL,
    ntfr_estado character varying(20) NOT NULL,
    ntfr_usuario_id integer NOT NULL,
    ntfr_fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ntfr_fecha_envio timestamp without time zone,
    ntfr_error text,
    CONSTRAINT chk_tbl_notificacion_asunto CHECK ((TRIM(BOTH FROM ntfr_asunto) <> ''::text)),
    CONSTRAINT chk_tbl_notificacion_cuerpo CHECK ((TRIM(BOTH FROM ntfr_cuerpo) <> ''::text)),
    CONSTRAINT chk_tbl_notificacion_destinatario CHECK ((TRIM(BOTH FROM ntfr_destinatario) <> ''::text)),
    CONSTRAINT chk_tbl_notificacion_estado CHECK (((ntfr_estado)::text = ANY ((ARRAY['BORRADOR'::character varying, 'ENVIADO'::character varying, 'ERROR'::character varying])::text[]))),
    CONSTRAINT chk_tbl_notificacion_tipo CHECK (((ntfr_tipo)::text = ANY ((ARRAY['RECHAZO'::character varying, 'AGRADECIMIENTO'::character varying, 'DIRECTIVOS'::character varying])::text[])))
);


ALTER TABLE public.tbl_notificacion_reclutamiento OWNER TO elitsoft_admin;

--
-- Name: tbl_notificacion_reclutamiento_ntfr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_notificacion_reclutamiento ALTER COLUMN ntfr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_notificacion_reclutamiento_ntfr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_opcion_respuesta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_opcion_respuesta (
    opcr_id integer NOT NULL,
    opcr_pregunta_id integer,
    opcr_texto_opcion character varying(300),
    opcr_es_correcta boolean,
    CONSTRAINT chk_tbl_opcion_respuesta_texto CHECK ((TRIM(BOTH FROM opcr_texto_opcion) <> ''::text))
);


ALTER TABLE public.tbl_opcion_respuesta OWNER TO elitsoft_admin;

--
-- Name: tbl_opcion_respuesta_opcr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_opcion_respuesta ALTER COLUMN opcr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_opcion_respuesta_opcr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_pais; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pais (
    pais_id integer NOT NULL,
    pais_nombre character varying(100),
    CONSTRAINT chk_tbl_pais_nombre_vacio CHECK ((TRIM(BOTH FROM pais_nombre) <> ''::text))
);


ALTER TABLE public.tbl_pais OWNER TO elitsoft_admin;

--
-- Name: tbl_pais_pais_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_pais ALTER COLUMN pais_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_pais_pais_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_password_reset_token; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_password_reset_token (
    prst_id integer NOT NULL,
    prst_usuario_id integer NOT NULL,
    prst_token_hash character varying(64) NOT NULL,
    prst_fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    prst_fecha_expiracion timestamp with time zone NOT NULL,
    prst_fecha_uso timestamp with time zone,
    prst_fecha_revocacion timestamp with time zone
);


ALTER TABLE public.tbl_password_reset_token OWNER TO elitsoft_admin;

--
-- Name: tbl_password_reset_token_prst_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_password_reset_token ALTER COLUMN prst_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_password_reset_token_prst_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_permiso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_permiso (
    per_id integer NOT NULL,
    per_nombre character varying(20),
    per_descripcion character varying(300),
    CONSTRAINT chk_tbl_permiso_descripcion_vacia CHECK (((per_descripcion IS NULL) OR (TRIM(BOTH FROM per_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_permiso_nombre_vacio CHECK ((TRIM(BOTH FROM per_nombre) <> ''::text))
);


ALTER TABLE public.tbl_permiso OWNER TO elitsoft_admin;

--
-- Name: tbl_permiso_per_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_permiso ALTER COLUMN per_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_permiso_per_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_plantilla_notificacion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_plantilla_notificacion (
    plnt_id integer NOT NULL,
    plnt_tipo character varying(30) NOT NULL,
    plnt_nombre character varying(100) NOT NULL,
    plnt_asunto character varying(300) NOT NULL,
    plnt_cuerpo text NOT NULL,
    plnt_activa boolean DEFAULT true NOT NULL,
    plnt_fecha_actualizacion timestamp without time zone,
    plnt_usuario_actualizacion_id integer,
    CONSTRAINT chk_tbl_plantilla_notificacion_asunto CHECK ((TRIM(BOTH FROM plnt_asunto) <> ''::text)),
    CONSTRAINT chk_tbl_plantilla_notificacion_cuerpo CHECK ((TRIM(BOTH FROM plnt_cuerpo) <> ''::text)),
    CONSTRAINT chk_tbl_plantilla_notificacion_nombre CHECK ((TRIM(BOTH FROM plnt_nombre) <> ''::text)),
    CONSTRAINT chk_tbl_plantilla_notificacion_tipo CHECK (((plnt_tipo)::text = ANY ((ARRAY['RECHAZO'::character varying, 'AGRADECIMIENTO'::character varying, 'DIRECTIVOS'::character varying])::text[])))
);


ALTER TABLE public.tbl_plantilla_notificacion OWNER TO elitsoft_admin;

--
-- Name: tbl_plantilla_notificacion_plnt_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_plantilla_notificacion ALTER COLUMN plnt_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_plantilla_notificacion_plnt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_pregunta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pregunta (
    preg_id integer NOT NULL,
    preg_texto_pregunta character varying(300),
    preg_habilidad_id integer,
    preg_nivel_habilidad_id integer,
    preg_fecha_creacion timestamp without time zone,
    CONSTRAINT chk_tbl_pregunta_texto CHECK ((TRIM(BOTH FROM preg_texto_pregunta) <> ''::text))
);


ALTER TABLE public.tbl_pregunta OWNER TO elitsoft_admin;

--
-- Name: tbl_pregunta_cuestionario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_pregunta_cuestionario (
    prcu_pregunta_id integer NOT NULL,
    prcu_cuestionario_id integer NOT NULL,
    prcu_id integer NOT NULL
);


ALTER TABLE public.tbl_pregunta_cuestionario OWNER TO elitsoft_admin;

--
-- Name: tbl_pregunta_cuestionario_prcu_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_pregunta_cuestionario ALTER COLUMN prcu_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.tbl_pregunta_cuestionario_prcu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_pregunta_preg_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_pregunta ALTER COLUMN preg_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_pregunta_preg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_prioridad_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_prioridad_solicitud (
    prsol_id integer NOT NULL,
    prsol_nombre character varying(15),
    prsol_descripcion character varying(300),
    CONSTRAINT chk_tbl_prioridad_descripcion_vacia CHECK (((prsol_descripcion IS NULL) OR (TRIM(BOTH FROM prsol_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_prioridad_nombre_vacio CHECK ((TRIM(BOTH FROM prsol_nombre) <> ''::text))
);


ALTER TABLE public.tbl_prioridad_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_prioridad_solicitud_prsol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_prioridad_solicitud ALTER COLUMN prsol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_prioridad_solicitud_prsol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_region; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_region (
    reg_id integer NOT NULL,
    reg_pais_id integer,
    reg_nombre character varying(100),
    CONSTRAINT chk_tbl_region_nombre_vacio CHECK ((TRIM(BOTH FROM reg_nombre) <> ''::text))
);


ALTER TABLE public.tbl_region OWNER TO elitsoft_admin;

--
-- Name: tbl_region_reg_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_region ALTER COLUMN reg_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_region_reg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_respuesta_pregunta; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_respuesta_pregunta (
    rspr_id integer NOT NULL,
    rspr_candidato_cuestionario_id integer,
    rspr_es_correcta boolean,
    rspr_puntaje_obtenido integer,
    rspr_opcion_respuesta_id integer,
    rspr_pregunta_cuestionario_id integer,
    CONSTRAINT chk_tbl_respuesta_pregunta_puntaje CHECK ((rspr_puntaje_obtenido >= 0))
);


ALTER TABLE public.tbl_respuesta_pregunta OWNER TO elitsoft_admin;

--
-- Name: tbl_respuesta_pregunta_rspr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_respuesta_pregunta ALTER COLUMN rspr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_respuesta_pregunta_rspr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_rol; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_rol (
    rol_id integer NOT NULL,
    rol_nombre character varying(20),
    rol_descripcion character varying(300),
    CONSTRAINT chk_tbl_rol_descripcion_vacia CHECK (((rol_descripcion IS NULL) OR (TRIM(BOTH FROM rol_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_rol_nombre_vacio CHECK ((TRIM(BOTH FROM rol_nombre) <> ''::text))
);


ALTER TABLE public.tbl_rol OWNER TO elitsoft_admin;

--
-- Name: tbl_rol_permiso; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_rol_permiso (
    rlpm_rol_id integer NOT NULL,
    rlpm_permiso_id integer NOT NULL
);


ALTER TABLE public.tbl_rol_permiso OWNER TO elitsoft_admin;

--
-- Name: tbl_rol_rol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_rol ALTER COLUMN rol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_rol_rol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_solicitud; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud (
    sol_id integer NOT NULL,
    sol_codigo character varying(10),
    sol_titulo character varying(300),
    sol_cargo_id integer,
    sol_descripcion character varying(300),
    sol_prioridad_id integer,
    sol_cantidad_vacantes integer,
    sol_cliente_id integer,
    sol_usuario_creador_id integer,
    sol_usuario_asignado_id integer,
    sol_modalidad_id integer,
    sol_salario_min integer,
    sol_salario_max integer,
    sol_fecha_creacion timestamp without time zone,
    sol_fecha_inicio_busqueda timestamp without time zone,
    sol_fecha_cierre_busqueda timestamp without time zone,
    sol_fecha_inicio_cliente timestamp without time zone,
    sol_estado_solicitud_id integer,
    sol_hora_inicio_jornada time without time zone,
    sol_hora_fin_jornada time without time zone,
    sol_tipo_contrato_id integer,
    sol_observacion character varying(300),
    CONSTRAINT chk_tbl_solicitud_codigo CHECK (((sol_codigo)::text ~ '^SOL-[0-9]{6}$'::text)),
    CONSTRAINT chk_tbl_solicitud_horario CHECK (((sol_hora_inicio_jornada IS NULL) OR (sol_hora_fin_jornada IS NULL) OR (sol_hora_inicio_jornada < sol_hora_fin_jornada))),
    CONSTRAINT chk_tbl_solicitud_salarios CHECK (((sol_salario_min IS NULL) OR (sol_salario_max IS NULL) OR (sol_salario_min <= sol_salario_max))),
    CONSTRAINT chk_tbl_solicitud_vacantes CHECK ((sol_cantidad_vacantes > 0))
);


ALTER TABLE public.tbl_solicitud OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_candidato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud_candidato (
    slcd_id integer NOT NULL,
    slcd_candidato_id integer,
    slcd_solicitud_id integer,
    slcd_pretension_renta integer,
    slcd_puntaje_compatibilidad numeric(5,2),
    slcd_estado_solicitud_candidato_id integer,
    slcd_fecha_postulacion timestamp without time zone,
    slcd_observaciones character varying(300),
    slcd_motivo_rechazo_id integer,
    CONSTRAINT chk_tbl_solicitud_candidato_observaciones CHECK (((slcd_observaciones IS NULL) OR (length(TRIM(BOTH FROM slcd_observaciones)) > 0))),
    CONSTRAINT chk_tbl_solicitud_candidato_pretension_renta CHECK (((slcd_pretension_renta IS NULL) OR (slcd_pretension_renta >= 0))),
    CONSTRAINT chk_tbl_solicitud_candidato_puntaje CHECK (((slcd_puntaje_compatibilidad IS NULL) OR ((slcd_puntaje_compatibilidad >= (0)::numeric) AND (slcd_puntaje_compatibilidad <= (100)::numeric))))
);


ALTER TABLE public.tbl_solicitud_candidato OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_candidato_slcd_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_solicitud_candidato ALTER COLUMN slcd_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_solicitud_candidato_slcd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_solicitud_habilidad; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_solicitud_habilidad (
    solhb_id integer NOT NULL,
    solhb_solicitud_id integer,
    solhb_habilidad_id integer,
    solhb_nivel_habilidad_id integer,
    solhb_anios_experiencia_req integer,
    solhb_es_excluyente boolean,
    CONSTRAINT chk_tbl_solicitud_habilidad_anios CHECK ((solhb_anios_experiencia_req >= 0))
);


ALTER TABLE public.tbl_solicitud_habilidad OWNER TO elitsoft_admin;

--
-- Name: tbl_solicitud_habilidad_solhb_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_solicitud_habilidad ALTER COLUMN solhb_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_solicitud_habilidad_solhb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_solicitud_sol_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_solicitud ALTER COLUMN sol_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_solicitud_sol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_tipo_contrato; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_contrato (
    tpct_id integer NOT NULL,
    tpct_nombre character varying(20),
    tpct_descripcion character varying(300),
    CONSTRAINT chk_tbl_tipo_contrato_descripcion_vacia CHECK (((tpct_descripcion IS NULL) OR (TRIM(BOTH FROM tpct_descripcion) <> ''::text))),
    CONSTRAINT chk_tbl_tipo_contrato_nombre_vacio CHECK ((TRIM(BOTH FROM tpct_nombre) <> ''::text))
);


ALTER TABLE public.tbl_tipo_contrato OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_contrato_tpct_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_tipo_contrato ALTER COLUMN tpct_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_tipo_contrato_tpct_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_tipo_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_entrevista (
    tpet_id integer NOT NULL,
    tpet_nombre character varying(40),
    tpet_descripcion character varying(300),
    CONSTRAINT chk_tbl_tipo_entrevista_nombre CHECK ((TRIM(BOTH FROM tpet_nombre) <> ''::text))
);


ALTER TABLE public.tbl_tipo_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_entrevista_tpet_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_tipo_entrevista ALTER COLUMN tpet_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_tipo_entrevista_tpet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_tipo_institucion; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_tipo_institucion (
    tint_id integer NOT NULL,
    tint_tipo_institucion character varying(40),
    CONSTRAINT chk_tbl_tipo_institucion_nombre_vacio CHECK ((TRIM(BOTH FROM tint_tipo_institucion) <> ''::text))
);


ALTER TABLE public.tbl_tipo_institucion OWNER TO elitsoft_admin;

--
-- Name: tbl_tipo_institucion_tint_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_tipo_institucion ALTER COLUMN tint_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_tipo_institucion_tint_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tbl_usuario; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_usuario (
    usr_id integer NOT NULL,
    usr_rol_id integer,
    usr_estado_usuario_id integer,
    usr_area_id integer,
    usr_nombres character varying(15),
    usr_apellido_paterno character varying(15),
    usr_apellido_materno character varying(15),
    usr_rut_sin_dv character varying(15),
    usr_dv character varying(1),
    usr_telefono character varying(15),
    usr_email character varying(30),
    usr_contrasena character varying(255),
    CONSTRAINT chk_tbl_usuario_apellido_paterno_vacio CHECK ((TRIM(BOTH FROM usr_apellido_paterno) <> ''::text)),
    CONSTRAINT chk_tbl_usuario_contrasena_vacia CHECK ((TRIM(BOTH FROM usr_contrasena) <> ''::text)),
    CONSTRAINT chk_tbl_usuario_email_formato CHECK (((usr_email)::text ~~ '%@%.%'::text)),
    CONSTRAINT chk_tbl_usuario_nombres_vacio CHECK ((TRIM(BOTH FROM usr_nombres) <> ''::text)),
    CONSTRAINT chk_tbl_usuario_rut_dv CHECK ((((usr_rut_sin_dv IS NULL) AND (usr_dv IS NULL)) OR ((usr_rut_sin_dv IS NOT NULL) AND (usr_dv IS NOT NULL)))),
    CONSTRAINT chk_tbl_usuario_telefono_vacio CHECK (((usr_telefono IS NULL) OR (TRIM(BOTH FROM usr_telefono) <> ''::text)))
);


ALTER TABLE public.tbl_usuario OWNER TO elitsoft_admin;

--
-- Name: tbl_usuario_cita_entrevista; Type: TABLE; Schema: public; Owner: elitsoft_admin
--

CREATE TABLE public.tbl_usuario_cita_entrevista (
    usrce_cita_entrevista_id integer NOT NULL,
    usrce_usuario_id integer NOT NULL,
    usrce_tipo_entrevista_id integer NOT NULL
);


ALTER TABLE public.tbl_usuario_cita_entrevista OWNER TO elitsoft_admin;

--
-- Name: tbl_usuario_usr_id_seq; Type: SEQUENCE; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE public.tbl_usuario ALTER COLUMN usr_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tbl_usuario_usr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: tbl_area; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_area (area_id, area_nombre, area_descripcion) FROM stdin;
1	Directorio	Organo responsable de definir la estrategia, el gobierno corporativo y la direccion general de la organizacion.
2	Gerencia General	Lidera la gestion integral de la empresa y supervisa el cumplimiento de los objetivos estrategicos.
3	Asistencia de Gerencia	Brinda apoyo administrativo y operativo a la Gerencia General en la coordinacion de sus actividades.
4	Asesoria Legal	Proporciona asesoramiento juridico y vela por el cumplimiento de la normativa vigente.
5	Control Interno	Supervisa los procesos internos para asegurar el cumplimiento de politicas, normas y controles.
6	Gerencia de Adm. y Finanzas	Administra los recursos financieros, contables y administrativos de la organizacion.
7	Gerencia de Operaciones	Gestiona y optimiza los procesos operativos para garantizar la eficiencia y continuidad del negocio.
8	Gerencia Comercial	Dirige las estrategias comerciales, ventas y desarrollo de clientes para impulsar el crecimiento de la organizacion.
9	Departamento de RR.HH.	Gestiona el talento humano, incluyendo reclutamiento, seleccion, desarrollo y bienestar de los colaboradores.
\.


--
-- Data for Name: tbl_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato (cand_id, cand_email, cand_password, cand_nombres, cand_apellido_paterno, cand_apellido_materno, cand_fecha_nacimiento, cand_telefono, cand_rut_sin_dv, cand_dv, cand_disponibilidad_id, cand_resumen_profesional, cand_fecha_creacion, cand_url_1, cand_titulo, cand_estado_usuario_id, cand_cv_urls) FROM stdin;
3	qa-m3-6324b046@sakura.cl	$2b$12$RUt7b4/5uTyLghseeTYbvOPU8jMXKVx5rgsuCEHvd4GpnrvXnSS.a	QA	ModuloTres	\N	\N	912345678	\N	\N	1	Candidato generado por QA LIVE 6324b046	2026-08-13 17:25:04.870339	https://linkedin.com/in/qa-sakura;https://github.com/qa-sakura	QA PATCH 6324b046	1	qa/6324b046/cv1.pdf;qa/6324b046/cv2.pdf
4	cv-m3-6324b046@sakura.cl	$2b$12$6Ny3fXYdCVX4Ffl2Zx55ReBAzcvb5XZIvBQ2rdMlm5BK1wUVoJSCi	QA	Candidato	\N	\N	912345678	\N	\N	\N	Profesional con experiencia suficiente para validar la importacion automatizada de CV del modulo tres Sakura.	2026-08-13 17:25:06.562541	\N	\N	4	storage/cv/7722c224d2ad4d19a210da24cc48481c.txt;storage/cv/f79e792556fa49bbb710352828cd5a56.txt
1	robmar@gmail.com	$2b$12$0c3dt93SG4mGDQRXA3qSo.bn/dtbpvG5S7kif.TOJTTXj1M5wXBsK	Roberto	Martinez	Olivares	1992-01-10	978611802	18002593	1	1	Profesional con solida experiencia y alto nivel de autonomia, orientado al logro de resultados, la resolucion de problemas y la mejora continua, con capacidad para liderar y aportar valor a la organizacion.	2026-07-02 00:00:00	www.github.com/rmartinez;www.linkedin.com/rmartinez	Titulo/Profesion obtenido. Usualmente en cabecera de CV.	1	\N
9	qa-m3-680ddf0e@sakura.cl	$2b$12$Z9uCReKJw7d/MFYV4kVEUet14ba/n3/bif3WfudWO7WXiClmqMpEi	QA	ModuloTres	\N	\N	912345678	\N	\N	1	Candidato generado por QA LIVE 680ddf0e	2026-08-14 21:17:31.573646	https://linkedin.com/in/qa-sakura;https://github.com/qa-sakura	QA PATCH 680ddf0e	1	qa/680ddf0e/cv1.pdf;qa/680ddf0e/cv2.pdf
5	qa-m3-17b5f4d2@sakura.cl	$2b$12$qM.0pmtp2jHwj6Iudcqb/.Lai7iwiSeHgaHn4tEWUM65Y0N3Aat0e	QA	ModuloTres	\N	\N	912345678	\N	\N	1	Candidato generado por QA LIVE 17b5f4d2	2026-08-13 19:50:02.401148	https://linkedin.com/in/qa-sakura;https://github.com/qa-sakura	QA PATCH 17b5f4d2	1	qa/17b5f4d2/cv1.pdf;qa/17b5f4d2/cv2.pdf
6	cv-m3-17b5f4d2@sakura.cl	$2b$12$4o.7zOniGTS6JwI.l9Dv/.FqTfSRz.elFoqY3HIl0EGm0lKsc/l96	QA	Candidato	\N	\N	912345678	\N	\N	\N	Profesional con experiencia suficiente para validar la importacion automatizada de CV del modulo tres Sakura.	2026-08-13 19:50:05.005107	\N	\N	4	storage/cv/e332aef9d892430a86671b232acb0726.txt;storage/cv/ef7fb64277ac4fabb00fd45893489dcd.txt
7	qa-m3-6c870a39@sakura.cl	$2b$12$5uwrrCC986l7N3zpav.A/uMWIsaozt9oM8FLN.Lzv9Gjhrh/rOapa	QA	ModuloTres	\N	\N	977776666	\N	\N	1	Candidato generado por QA LIVE 6c870a39	2026-08-13 20:16:28.205604	https://linkedin.com/in/self-live;https://github.com/self-live	QA PATCH 6c870a39	1	qa/6c870a39/cv1.pdf;qa/6c870a39/cv2.pdf
10	cv-m3-680ddf0e@sakura.cl	$2b$12$LB.tKp1rGth2Jz0kqsQl4.hdSpGZTK5KsVcLc/QO3H8jSmwSIvkVS	QA	Candidato	\N	\N	912345678	\N	\N	\N	Profesional con experiencia suficiente para validar la importacion automatizada de CV del modulo tres Sakura.	2026-08-14 21:17:34.1642	\N	\N	4	storage/cv/2ca651221b584ae39584dcb1ae2f44b0.txt;storage/cv/da3037905dd448fead1de8ac7a3e6d05.txt
8	cv-m3-6c870a39@sakura.cl	$2b$12$w7sKWG2Vb6ZIaLlXCSRz2uMwAWTmSzBbev.KcdsSEXlRRNoOGQDf6	QA	Candidato	\N	\N	912345678	\N	\N	\N	Profesional con experiencia suficiente para validar la importacion automatizada de CV del modulo tres Sakura.	2026-08-13 20:16:30.892933	\N	\N	4	storage/cv/251eaf69761c4a67a9a87a1bfddfac9e.txt;storage/cv/118fcf8abe87430a9756414370f6d5a4.txt
11	qa.cand1.m5@sakura.cl	$2a$12$kbK6g9xLeNplZNGb2wCh6.0YB6I4COm0vrZa3Le42.IZed627QjWG	Candidato	Uno	QA	1990-01-01	970000001	26000001	1	1	Candidato de prueba para QA LIVE Modulo 5.	2026-08-17 10:16:06.143597	\N	Ingeniero QA	1	\N
12	qa.cand2.m5@sakura.cl	$2a$12$IpDO1Rpz/BboenKcQ5nqXup.vleNJ0bnw4oQTqXB9TC9n3kql2blm	Candidato	Dos	QA	1991-01-01	970000002	26000002	2	1	Segundo candidato para QA LIVE Modulo 5.	2026-08-17 10:16:06.143597	\N	Ingeniero QA	1	\N
\.


--
-- Data for Name: tbl_candidato_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato_cuestionario (cdcu_id, cdcu_candidato_id, cdcu_cuestionario_id, cdcu_fecha_asignacion, cdcu_fecha_resolucion, cdcu_porcentaje_obtenido, cdcu_estado_cuestionario_candidato_id, cdcu_tiempo_utilizado, cdcu_permitir_reintento, cdcu_aprobado, cdcu_fecha_inicio, cdcu_fecha_vencimiento) FROM stdin;
1	1	1	2026-07-05 09:00:00	2026-07-05 09:28:00	90.00	3	28	f	t	\N	2026-08-04 09:00:00
2	1	4	2026-08-13 22:41:17.144593	2026-08-13 22:41:17.30245	100.00	3	0	f	t	2026-08-13 22:41:17.206266	2026-08-15 22:41:17.123697
3	1	5	2026-08-13 22:41:17.459531	\N	\N	1	\N	f	\N	\N	2026-08-15 22:41:17.44718
4	1	6	2026-08-13 22:41:17.543818	\N	\N	1	\N	f	\N	\N	2026-08-15 22:41:17.532535
5	1	8	2026-08-13 22:41:17.745332	2026-08-14 01:03:28.917412	0.00	3	1	t	f	2026-08-13 22:41:17.858904	2026-08-18 22:41:17.830961
6	1	9	2026-08-14 01:03:28.841698	2026-08-14 01:03:29.088709	100.00	3	0	f	t	2026-08-14 01:03:28.981291	2026-08-16 01:03:28.822637
7	1	10	2026-08-14 01:03:29.74794	\N	\N	1	\N	f	\N	\N	2026-08-16 01:03:29.729544
8	5	10	2026-08-14 01:03:29.74794	\N	\N	1	\N	f	\N	\N	2026-08-16 01:03:29.729544
9	1	11	2026-08-14 01:03:29.914175	\N	\N	1	\N	f	\N	\N	2026-08-16 01:03:29.887567
10	5	11	2026-08-14 01:03:29.939429	\N	\N	1	\N	f	\N	\N	2026-08-17 01:03:29.923521
11	1	13	2026-08-14 01:03:30.150816	2026-08-14 21:34:41.442301	0.00	3	1	t	f	2026-08-14 01:03:30.279704	2026-08-19 01:03:30.246696
12	1	14	2026-08-14 21:34:41.370086	2026-08-14 21:34:41.613839	100.00	3	0	f	t	2026-08-14 21:34:41.512048	2026-08-16 21:34:41.346692
13	1	15	2026-08-14 21:34:41.864924	\N	\N	1	\N	f	\N	\N	2026-08-16 21:34:41.841769
14	5	15	2026-08-14 21:34:41.864924	\N	\N	1	\N	f	\N	\N	2026-08-16 21:34:41.841769
15	1	16	2026-08-14 21:34:42.039735	\N	\N	1	\N	f	\N	\N	2026-08-16 21:34:42.020175
16	5	16	2026-08-14 21:34:42.077065	\N	\N	1	\N	f	\N	\N	2026-08-17 21:34:42.052732
17	1	18	2026-08-14 21:34:42.335999	\N	\N	2	\N	t	\N	2026-08-14 21:34:42.477139	2026-08-19 21:34:42.431258
\.


--
-- Data for Name: tbl_candidato_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato_habilidad (cdhb_id, cdhb_candidato_id, cdhb_habilidad_id, cdhb_nivel_habilidad_id, cdhb_anios_experiencia) FROM stdin;
1	1	7	4	9
2	1	13	4	7
3	1	1	4	9
4	1	27	3	6
5	1	28	2	3
6	1	33	2	3
7	1	45	3	7
8	1	29	4	9
9	1	30	3	6
10	1	23	3	4
11	1	21	3	6
12	1	22	3	4
13	1	40	4	8
14	1	43	3	5
15	1	44	3	5
16	3	1	2	6
17	4	7	\N	4
18	5	1	2	6
19	6	7	\N	4
20	7	1	2	6
21	8	7	\N	4
22	9	1	2	6
23	10	7	\N	4
\.


--
-- Data for Name: tbl_candidato_idioma; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_candidato_idioma (cdio_id, cdio_candidato_id, cdio_idioma_id, cdio_nivel_idioma_id) FROM stdin;
\.


--
-- Data for Name: tbl_cargo; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cargo (crgo_id, crgo_nombre, crgo_descripcion) FROM stdin;
1	Desarrollador Backend	Desarrolla la logica de negocio y los servicios del lado del servidor.
2	Desarrollador Frontend	Desarrolla la interfaz de usuario y la experiencia visual de las aplicaciones.
3	Desarrollador Full Stack	Desarrolla tanto el frontend como el backend de las aplicaciones.
4	Desarrollador Mobile	Desarrolla aplicaciones para dispositivos moviles Android e iOS.
5	Analista QA	Disena y ejecuta pruebas para asegurar la calidad del software.
6	Ingeniero QA Automation	Automatiza pruebas funcionales y de regresion.
7	Scrum Master	Facilita la metodologia Scrum y elimina impedimentos del equipo.
8	Product Owner	Gestiona el backlog del producto y prioriza los requerimientos del negocio.
9	Analista Funcional	Levanta, analiza y documenta requerimientos funcionales.
10	Analista de Sistemas	Analiza procesos y propone soluciones tecnologicas.
11	Arquitecto de Software	Define la arquitectura tecnica de las aplicaciones.
12	DevOps Engineer	Automatiza despliegues y administra la infraestructura de desarrollo.
13	Ingeniero de Datos	Disena y mantiene pipelines y plataformas de datos.
14	Cientifico de Datos	Analiza grandes volumenes de datos mediante modelos estadisticos y de inteligencia artificial.
15	Analista BI	Desarrolla indicadores, reportes y dashboards para apoyar la toma de decisiones.
16	Administrador de Base de Datos (DBA)	Administra, optimiza y asegura el correcto funcionamiento de las bases de datos.
17	Administrador de Sistemas	Gestiona servidores, sistemas operativos y plataformas tecnologicas.
18	Especialista en Ciberseguridad	Protege la infraestructura tecnologica y la informacion de la organizacion.
19	Soporte TI	Brinda soporte tecnico a usuarios y equipos tecnologicos.
20	Lider Tecnico	Coordina tecnicamente al equipo de desarrollo y promueve las buenas practicas.
21	Jefe de Proyecto TI	Planifica, coordina y controla la ejecucion de proyectos tecnologicos.
\.


--
-- Data for Name: tbl_carrera; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_carrera (crra_id, crra_nombre) FROM stdin;
1	Ingenieria Civil Informatica
2	Ingenieria en Informatica
3	Ingenieria Civil en Computacion
4	Ingenieria Civil en Ciencia de Datos
5	Ingenieria en Ciencia de Datos
6	Ingenieria Civil Industrial
7	Ingenieria Industrial
8	Ingenieria en Automatizacion
9	Ingenieria en Telecomunicaciones
10	Ingenieria en Redes y Comunicaciones
11	Ingenieria en Ciberseguridad
12	Ingenieria en Inteligencia Artificial
13	Ingenieria en Software
14	Ingenieria en Sistemas
15	Ingenieria en Computacion
16	Ingenieria Electronica
17	Ingenieria Electrica
18	Ingenieria Mecatronica
19	Ingenieria Matematica
20	Licenciatura en Ciencias de la Computacion
21	Licenciatura en Informatica
22	Analisis de Sistemas
23	Tecnico en Programacion
24	Tecnico en Informatica
25	Tecnico en Analisis de Sistemas
26	Tecnico en Desarrollo de Software
27	Tecnico en Desarrollo Web
28	Tecnico en Ciberseguridad
29	Tecnico en Redes
30	Tecnico en Administracion de Redes
31	Tecnico en Soporte TI
32	Tecnico en Base de Datos
33	Tecnico en Telecomunicaciones
34	Tecnico en Automatizacion y Robotica
35	Tecnico en Ciencia de Datos
36	Tecnico en QA
37	Tecnico en Infraestructura TI
38	Administracion de Empresas
39	Ingenieria Comercial
40	Contador Auditor
41	Psicologia
42	Diseno Grafico
43	Diseno UX/UI
44	Periodismo
45	Marketing Digital
46	Recursos Humanos
47	Administracion Publica
\.


--
-- Data for Name: tbl_categoria_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_categoria_habilidad (cthb_id, cthb_nombre, cthb_descripcion) FROM stdin;
1	Lenguajes	Lenguajes de programaci├│n
2	Frameworks / Librer├¡as	Frameworks y librer├¡as de desarrollo
3	Bases de Datos	Motores, tecnolog├¡as y herramientas de datos
4	Cloud / DevOps	Cloud, contenedores, CI/CD y automatizaci├│n
5	Herramientas	Herramientas t├®cnicas generales
6	Metodolog├¡as	Metodolog├¡as, pr├ícticas y marcos de trabajo
7	Otros	Conocimientos sin categor├¡a espec├¡fica
\.


--
-- Data for Name: tbl_cita_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cita_entrevista (ctev_id, ctev_solicitud_candidato_id, ctev_tipo_entrevista_id, ctev_estado_entrevista_id, ctev_fecha_hora_inicio, ctev_fecha_hora_fin, ctev_fecha_creacion, ctev_enlace_reunion, ctev_comentarios_convocatoria, ctev_titulo_evento, ctev_usuario_creador_id, ctev_fecha_actualizacion, ctev_motivo_estado) FROM stdin;
1	1	2	3	2026-07-08 10:00:00	2026-07-08 11:00:00	2026-07-07 14:00:00	https://meet.google.com/abc-defg-hij	Por favor, asiste con tu entorno de Python y Docker listo para una breve prueba de desarrollo.	Entrevista Tecnica Backend Senior - Roberto Martinez	\N	2026-07-07 14:00:00	\N
2	8	1	3	2026-09-13 15:08:38.816996	2026-09-13 16:08:38.816996	2026-08-17 14:37:38.275321	https://meet.example/d3aa333f-1	QA LIVE M5 d3aa333f	QA PATCH d3aa333f	12	2026-08-17 14:37:38.889036	\N
4	8	1	3	2026-09-13 15:11:54.062441	2026-09-13 16:11:54.062441	2026-08-17 14:41:53.487823	https://meet.example/4b089c4f-1	QA LIVE M5 4b089c4f	QA PATCH 4b089c4f	12	2026-08-17 14:41:54.133911	\N
6	8	1	5	2026-09-15 15:11:54.620326	2026-09-15 16:11:54.620326	2026-08-17 14:41:54.637535	https://meet.example/4b089c4f-9	QA LIVE M5 4b089c4f	QA CANCEL 4b089c4f	12	2026-08-17 14:41:54.686248	QA cancel
7	8	1	6	2026-09-16 15:11:54.727955	2026-09-16 16:11:54.727955	2026-08-17 14:41:54.746899	https://meet.example/4b089c4f-10	QA LIVE M5 4b089c4f	QA NOSHOW 4b089c4f	12	2026-08-17 14:41:54.819821	QA ausencia
8	8	1	1	2026-09-18 15:11:54.8401	2026-09-18 16:11:54.8401	2026-08-17 14:41:54.870124	\N	QA mass	QA MASS 4b089c4f	12	2026-08-17 14:41:54.870132	\N
9	9	1	1	2026-09-18 15:11:54.8401	2026-09-18 16:11:54.8401	2026-08-17 14:41:54.874474	\N	QA mass	QA MASS 4b089c4f	12	2026-08-17 14:41:54.87448	\N
11	8	1	3	2026-09-13 17:17:52.502315	2026-09-13 18:17:52.502315	2026-08-17 17:17:51.995588	https://meet.example/2dee5d87-1	QA LIVE M5 2dee5d87	QA PATCH 2dee5d87	12	2026-08-17 17:17:52.548461	\N
13	8	1	5	2026-09-15 17:17:52.838025	2026-09-15 18:17:52.838025	2026-08-17 17:17:52.850661	https://meet.example/2dee5d87-9	QA LIVE M5 2dee5d87	QA CANCEL 2dee5d87	12	2026-08-17 17:17:52.880039	QA cancel
14	8	1	6	2026-09-16 17:17:52.910526	2026-09-16 18:17:52.910526	2026-08-17 17:17:52.923173	https://meet.example/2dee5d87-10	QA LIVE M5 2dee5d87	QA NOSHOW 2dee5d87	12	2026-08-17 17:17:52.951063	QA ausencia
15	8	1	1	2026-09-18 17:17:52.96486	2026-09-18 18:17:52.96486	2026-08-17 17:17:52.978035	\N	QA mass	QA MASS 2dee5d87	12	2026-08-17 17:17:52.978039	\N
16	9	1	1	2026-09-18 17:17:52.96486	2026-09-18 18:17:52.96486	2026-08-17 17:17:52.980604	\N	QA mass	QA MASS 2dee5d87	12	2026-08-17 17:17:52.980609	\N
\.


--
-- Data for Name: tbl_cita_tipo_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cita_tipo_entrevista (cten_tipo_entrevista_id, cten_cita_entrevista_id) FROM stdin;
2	1
1	2
2	2
1	4
2	4
1	6
2	6
1	7
2	7
1	8
1	9
1	11
2	11
1	13
2	13
1	14
2	14
1	15
1	16
\.


--
-- Data for Name: tbl_cliente; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cliente (cli_id, cli_nombre, cli_cargo_empresa_id, cli_area_empresa_id, cli_email, cli_email2, cli_telefono1, cli_telefono2, cli_empresa_id) FROM stdin;
1	Jade Garcia	20	7	jade@bcochile.cl	jade2@bcochile.cl	998765432	998765431	1
2	Carol Urquieta	7	7	carol@bcochile.cl	carol2@bcochile.cl	987654321	987654320	1
3	Oriana Hurtado	5	7	oriana@bcochile.cl	oriana2@bcochile.cl	976543210	976543219	1
4	Sheila Valdes	21	7	sheila@latam.cl	sheila2@latam.cl	965432109	965432108	3
5	Rodrigo Riquelme	20	7	rodrigo@elitsoft.cl	rodrigo2@elitsoft.cl	954321098	954321097	4
\.


--
-- Data for Name: tbl_comuna; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_comuna (com_id, com_region_id, com_nombre) FROM stdin;
1	1	Arica
2	1	Camarones
3	1	Putre
4	1	General Lagos
5	2	Iquique
6	2	Alto Hospicio
7	2	Pozo Almonte
8	2	Camina
9	2	Colchane
10	2	Huara
11	2	Pica
12	3	Antofagasta
13	3	Mejillones
14	3	Sierra Gorda
15	3	Taltal
16	3	Calama
17	3	Ollague
18	3	San Pedro de Atacama
19	3	Maria Elena
20	3	Tocopilla
21	4	Copiapo
22	4	Caldera
23	4	Tierra Amarilla
24	4	Chanaral
25	4	Diego de Almagro
26	4	Vallenar
27	4	Alto del Carmen
28	4	Freirina
29	4	Huasco
30	5	La Serena
31	5	Coquimbo
32	5	Andacollo
33	5	La Higuera
34	5	Paihuano
35	5	Vicuna
36	5	Illapel
37	5	Canela
38	5	Los Vilos
39	5	Salamanca
40	5	Ovalle
41	5	Combarbala
42	5	Monte Patria
43	5	Punitaqui
44	5	Rio Hurtado
45	6	Valparaiso
46	6	Vina del Mar
47	6	Concon
48	6	Quilpue
49	6	Villa Alemana
50	6	Casablanca
51	6	Juan Fernandez
52	6	Isla de Pascua
53	6	Quintero
54	6	Puchuncavi
55	6	Zapallar
56	6	Papudo
57	6	La Ligua
58	6	Cabildo
59	6	Petorca
60	6	Hijuelas
61	6	La Calera
62	6	Nogales
63	6	Quillota
64	6	La Cruz
65	6	Limache
66	6	Olmue
67	6	Los Andes
68	6	Calle Larga
69	6	Rinconada
70	6	San Esteban
71	6	San Felipe
72	6	Catemu
73	6	Llaillay
74	6	Panquehue
75	6	Putaendo
76	6	Santa Maria
77	6	Algarrobo
78	6	Cartagena
79	6	El Quisco
80	6	El Tabo
81	6	San Antonio
82	6	Santo Domingo
83	7	Cerrillos
84	7	Cerro Navia
85	7	Conchali
86	7	El Bosque
87	7	Estacion Central
88	7	Huechuraba
89	7	Independencia
90	7	La Cisterna
91	7	La Florida
92	7	La Granja
93	7	La Pintana
94	7	La Reina
95	7	Las Condes
96	7	Lo Barnechea
97	7	Lo Espejo
98	7	Lo Prado
99	7	Macul
100	7	Maipu
101	7	Nunoa
102	7	Pedro Aguirre Cerda
103	7	Penalolen
104	7	Providencia
105	7	Pudahuel
106	7	Quilicura
107	7	Quinta Normal
108	7	Recoleta
109	7	Renca
110	7	San Joaquin
111	7	San Miguel
112	7	San Ramon
113	7	Santiago
114	7	Vitacura
115	7	Buin
116	7	Calera de Tango
117	7	Colina
118	7	Curacavi
119	7	El Monte
120	7	Isla de Maipo
121	7	Lampa
122	7	Maria Pinto
123	7	Melipilla
124	7	Padre Hurtado
125	7	Paine
126	7	Penaflor
127	7	Pirque
128	7	Puente Alto
129	7	San Bernardo
130	7	San Jose de Maipo
131	7	San Pedro
132	7	Talagante
133	7	Tiltil
134	7	Alhue
135	8	Rancagua
136	8	Codegua
137	8	Coinco
138	8	Coltauco
139	8	Donihue
140	8	Graneros
141	8	Machali
142	8	Malloa
143	8	Mostazal
144	8	Olivar
145	8	Peumo
146	8	Pichidegua
147	8	Quinta de Tilcoco
148	8	Rengo
149	8	Requinoa
150	8	San Vicente
151	8	Las Cabras
152	8	La Estrella
153	8	Litueche
154	8	Marchigue
155	8	Navidad
156	8	Paredones
157	8	Pichilemu
158	8	Chepica
159	8	Chimbarongo
160	8	Lolol
161	8	Nancagua
162	8	Palmilla
163	8	Peralillo
164	8	Placilla
165	8	Pumanque
166	8	San Fernando
167	8	Santa Cruz
168	9	Talca
169	9	Constitucion
170	9	Curepto
171	9	Empedrado
172	9	Maule
173	9	Pelarco
174	9	Pencahue
175	9	Rio Claro
176	9	San Clemente
177	9	San Rafael
178	9	Curico
179	9	Hualane
180	9	Licanten
181	9	Molina
182	9	Rauco
183	9	Romeral
184	9	Sagrada Familia
185	9	Teno
186	9	Vichuquen
187	9	Linares
188	9	Colbun
189	9	Longavi
190	9	Parral
191	9	Retiro
192	9	San Javier
193	9	Villa Alegre
194	9	Yerbas Buenas
195	9	Cauquenes
196	9	Chanco
197	9	Pelluhue
198	10	Chillan
199	10	Chillan Viejo
200	10	Bulnes
201	10	Cobquecura
202	10	Coelemu
203	10	Coihueco
204	10	El Carmen
205	10	Ninhue
206	10	Pemuco
207	10	Pinto
208	10	Portezuelo
209	10	Quillon
210	10	Quirihue
211	10	Ranquil
212	10	San Carlos
213	10	San Fabian
214	10	San Ignacio
215	10	San Nicolas
216	10	Trehuaco
217	10	Yungay
218	10	Niquen
219	11	Concepcion
220	11	Coronel
221	11	Chiguayante
222	11	Florida
223	11	Hualqui
224	11	Lota
225	11	Penco
226	11	San Pedro de la Paz
227	11	Santa Juana
228	11	Talcahuano
229	11	Tome
230	11	Hualpen
231	11	Lebu
232	11	Arauco
233	11	Canete
234	11	Contulmo
235	11	Curanilahue
236	11	Los Alamos
237	11	Tirua
238	11	Los Angeles
239	11	Antuco
240	11	Cabrero
241	11	Laja
242	11	Mulchen
243	11	Nacimiento
244	11	Negrete
245	11	Quilaco
246	11	Quilleco
247	11	San Rosendo
248	11	Santa Barbara
249	11	Tucapel
250	11	Yumbel
251	11	Alto Biobio
252	12	Temuco
253	12	Carahue
254	12	Cunco
255	12	Curarrehue
256	12	Freire
257	12	Galvarino
258	12	Gorbea
259	12	Lautaro
260	12	Loncoche
261	12	Melipeuco
262	12	Nueva Imperial
263	12	Padre Las Casas
264	12	Perquenco
265	12	Pitrufquen
266	12	Pucon
267	12	Saavedra
268	12	Teodoro Schmidt
269	12	Tolten
270	12	Vilcun
271	12	Villarrica
272	12	Cholchol
273	12	Angol
274	12	Collipulli
275	12	Curacautin
276	12	Ercilla
277	12	Lonquimay
278	12	Los Sauces
279	12	Lumaco
280	12	Puren
281	12	Renaico
282	12	Traiguen
283	12	Victoria
284	13	Valdivia
285	13	Corral
286	13	Lanco
287	13	Los Lagos
288	13	Mariquina
289	13	Mafil
290	13	Paillaco
291	13	Panguipulli
292	13	La Union
293	13	Futrono
294	13	Lago Ranco
295	13	Rio Bueno
296	14	Puerto Montt
297	14	Calbuco
298	14	Cochamo
299	14	Fresia
300	14	Frutillar
301	14	Los Muermos
302	14	Llanquihue
303	14	Maullin
304	14	Puerto Varas
305	14	Ancud
306	14	Castro
307	14	Chonchi
308	14	Curaco de Velez
309	14	Dalcahue
310	14	Puqueldon
311	14	Queilen
312	14	Quellon
313	14	Quemchi
314	14	Quinchao
315	14	Osorno
316	14	Puerto Octay
317	14	Purranque
318	14	Puyehue
319	14	Rio Negro
320	14	San Juan de la Costa
321	14	San Pablo
322	14	Chaiten
323	14	Futaleufu
324	14	Hualaihue
325	14	Palena
326	15	Coyhaique
327	15	Lago Verde
328	15	Aysen
329	15	Cisnes
330	15	Guaitecas
331	15	Cochrane
332	15	OHiggins
333	15	Tortel
334	15	Chile Chico
335	15	Rio Ibanez
336	16	Punta Arenas
337	16	Laguna Blanca
338	16	Rio Verde
339	16	San Gregorio
340	16	Cabo de Hornos
341	16	Antartica
342	16	Porvenir
343	16	Primavera
344	16	Timaukel
345	16	Natales
346	16	Torres del Paine
\.


--
-- Data for Name: tbl_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_cuestionario (cues_id, cues_nombre, cues_descripcion, cues_porcentaje_aprobacion, cues_solicitud_id) FROM stdin;
1	Cuestionario Tecnico Backend Python Senior	Evaluacion tecnica orientada a validar conocimientos de Python, FastAPI, PostgreSQL, Docker, Git, Kubernetes y buenas practicas de desarrollo para la vacante de Desarrollador Backend Senior.	70.00	1
2	QA LIVE M4 IND-20260813-183216	QA automatizado IND-20260813-183216	50.00	10
3	QA LIVE M4 IND-20260813-183803	QA automatizado IND-20260813-183803	50.00	10
4	QA LIVE M4 IND-20260813-184117	QA automatizado IND-20260813-184117	50.00	1
5	QA LIVE M4 MASS-20260813-184117	QA automatizado MASS-20260813-184117	50.00	1
6	QA LIVE M4 ALL-20260813-184117	QA automatizado ALL-20260813-184117	50.00	1
7	QA LIVE M4 ALL-PAST-20260813-184117	QA automatizado ALL-PAST-20260813-184117	50.00	1
8	QA LIVE M4 TECH-20260813-184117	QA automatizado TECH-20260813-184117	50.00	1
9	QA LIVE M4 IND-20260813-210328	QA automatizado IND-20260813-210328	50.00	1
10	QA LIVE M4 MASS-20260813-210328	QA automatizado MASS-20260813-210328	50.00	1
11	QA LIVE M4 ALL-20260813-210328	QA automatizado ALL-20260813-210328	50.00	1
12	QA LIVE M4 ALL-PAST-20260813-210328	QA automatizado ALL-PAST-20260813-210328	50.00	1
13	QA LIVE M4 TECH-20260813-210328	QA automatizado TECH-20260813-210328	50.00	1
14	QA LIVE M4 IND-20260814-173441	QA automatizado IND-20260814-173441	50.00	1
15	QA LIVE M4 MASS-20260814-173441	QA automatizado MASS-20260814-173441	50.00	1
16	QA LIVE M4 ALL-20260814-173441	QA automatizado ALL-20260814-173441	50.00	1
17	QA LIVE M4 ALL-PAST-20260814-173441	QA automatizado ALL-PAST-20260814-173441	50.00	1
18	QA LIVE M4 TECH-20260814-173441	QA automatizado TECH-20260814-173441	50.00	1
\.


--
-- Data for Name: tbl_curso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_curso (curs_id, curs_candidato_id, curs_nombre_curso, curs_institucion_id, curs_es_certificado, curs_anio_curso) FROM stdin;
1	1	Python Avanzado	29	t	2022
2	1	Docker y Kubernetes	29	t	2023
3	1	AWS Cloud Practitioner	33	t	2024
4	1	Scrum Fundamentals	36	t	2023
5	1	SQL para Analisis de Datos	29	f	2022
6	1	Git y GitHub Profesional	28	f	2021
7	1	Desarrollo Backend con FastAPI	26	t	2025
8	1	Azure Fundamentals AZ-900	32	t	2024
9	1	Google Cloud Fundamentals	34	f	2023
10	1	JavaScript Moderno	28	f	2022
\.


--
-- Data for Name: tbl_direccion_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_direccion_candidato (drcd_id, drcd_candidato_id, drcd_comuna_id, drcd_calle, drcd_numero, drcd_dpto_oficina) FROM stdin;
1	1	104	Avenida Providencia	1875	1204
\.


--
-- Data for Name: tbl_disponibilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_disponibilidad (disp_id, disp_nombre) FROM stdin;
1	Inmediata
2	1 semana
3	2 semanas
4	3 semanas
5	4 semanas
\.


--
-- Data for Name: tbl_documento_reporte_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_documento_reporte_candidato (drcp_id, drcp_solicitud_candidato_id, drcp_tipo_documento, drcp_nombre_archivo, drcp_ruta_archivo, drcp_fecha_generacion, drcp_usuario_generador_id, drcp_hash_sha256, drcp_snapshot_json) FROM stdin;
1	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:15:52.636064	12	13b74c964025caa7f4124bb97c3efbb497354be626728f8b62c7189039a48006	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
2	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:15:52.81382	12	107b8d8e12acbffd1d692f09029d96696a15c8dfef6a494acac37bb06f783502	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "QA LIVE d5cb0028", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
3	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:15:52.961136	12	5f94b0d77b2f642c5f84d3c63df1c11bc7aed6cd02a185c9a700f832047db1e4	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
4	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-17 22:15:53.020719	12	9307ca242b5a95babc5dfbe03f407010b674f2625770ea582c3618a439c1c930	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
5	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:15:53.478449	12	e94f9dadbd7ac4eeb05b0853226e284d05005464bbfa9014c829015770e050f6	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
6	8	RESUMEN	RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	2026-08-17 22:15:53.513563	12	ca1300965da9ca23e426891fcd1abc53d37e35e0b0ae7aafe5451575c3c77d01	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [{"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 2, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 4, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 11, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}], "tecnologias": [], "candidato_id": 11, "solicitud_id": 1, "clasificacion": "NO_APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand1.m5@sakura.cl", "candidato_nombre": "Candidato Uno QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000001", "estado_postulacion": "Descartado", "motivo_clasificacion": ["Estado de postulaci├│n: Descartado"], "puede_enviar_rechazo": true, "clasificacion_sugerida": false, "solicitud_candidato_id": 8, "puede_enviar_directivos": false}
7	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:15:53.611609	12	7b899512f3c2073efed424231a3e45e5982a821352dc5d934cccbf0e11fc2b10	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
8	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-17 22:15:53.663805	12	c8f3f921605dadcafdf0c2d52f62134f1a965ee8b99c246865fbc23d16618521	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
9	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:18:34.484777	12	c1b386569417360a09ee324d66fa04b1fc0601d54d88497476b8c1a8e21e73d7	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
10	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:18:34.640008	12	c76136abb8ea55e3533149e2124fc969a0373f5190154333c7450e188fbbdce1	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "QA LIVE 6b10b963", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
11	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:18:34.813975	12	805ad5c12aee3141248674c60c8b0440489e858638326ba71d2e73b188cb165d	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
12	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-17 22:18:34.899853	12	da5f9141ae48cbb10bfee08f8daa7cbba0537bde99d1f03125da3e03da3710c8	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
13	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:18:35.038644	12	30ab48598e43ac0beabe40f63aaa494b938e3e95256203c6d0fe29371e844020	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
14	8	RESUMEN	RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	2026-08-17 22:18:35.100839	12	ceabe5b5c0bd216a7f4bbe6f9882722f24b0353541e46ddaa48b277c0d005008	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [{"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 2, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 4, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 11, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}], "tecnologias": [], "candidato_id": 11, "solicitud_id": 1, "clasificacion": "NO_APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand1.m5@sakura.cl", "candidato_nombre": "Candidato Uno QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000001", "estado_postulacion": "Descartado", "motivo_clasificacion": ["Estado de postulaci├│n: Descartado"], "puede_enviar_rechazo": true, "clasificacion_sugerida": false, "solicitud_candidato_id": 8, "puede_enviar_directivos": false}
15	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:18:35.239621	12	b983a02bd451bf5496c2f831cbe3a26f837969daa50a51da4998cd4743e1eac0	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
16	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-17 22:18:35.328795	12	98a2766fc2007d6dd9e566925dcb621a18bf9953fa2bb6793f506feafab088e2	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
17	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:18:35.506069	12	2bd7235ab1224a99ed383d8d96ab3ed1d277a32360af4bf9d4687c79f2dcd987	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
18	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:33:34.032608	12	c3ac066054331afd490155051d0ba6fe7bab5595057aa148cfbbff748e673e0d	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
19	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:33:34.472123	12	8936f04801fe840ca68cae74469040b4d9ae95ef6fdfc8be92c0436bc7135b4b	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "QA LIVE 279b039e", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
20	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:33:34.67459	12	3e608d7564c08e19a399f0b5d9ce195422c4e6eca83d5e5bd6c0a45029b4da26	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
21	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-17 22:33:34.764705	12	0f029eb85247350ef2cc98e070ff23c12da06d2a91ffd957397c288ab4153c92	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
22	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:33:34.975597	12	adcad9bc01b225ad8b938394b072233d8951098352c1c681a6547c282dd6ff14	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
23	8	RESUMEN	RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	2026-08-17 22:33:35.033604	12	195e2d424cd9ca2ca5c5552e87909794bffb31b76c10e0e137462dd399b72a30	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [{"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 2, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 4, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 11, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}], "tecnologias": [], "candidato_id": 11, "solicitud_id": 1, "clasificacion": "NO_APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand1.m5@sakura.cl", "candidato_nombre": "Candidato Uno QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000001", "estado_postulacion": "Descartado", "motivo_clasificacion": ["Estado de postulaci├│n: Descartado"], "puede_enviar_rechazo": true, "clasificacion_sugerida": false, "solicitud_candidato_id": 8, "puede_enviar_directivos": false}
24	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:33:35.14926	12	36ab857658f9d025fc25379956940b4232044e64327572a1a72adab7fcabfb3e	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
25	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-17 22:33:35.206696	12	a504ad6ba874fdf6cc78a93c20f024eeafec29a6bd7325df2678e2ff5a60bc1d	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
26	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-17 22:33:35.392906	12	7ae8d3966f0d8259ebf8723dadcf142b575cb146f2ec06d28d15eb2f57e2b53f	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
27	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:29.311409	12	fe99eadc815b999c713ec70dccf16c74fc116b0404de4ac493c0dec9cc1cf47a	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
28	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:46.990252	12	b07026d707ebc9058a39df9023fc45974fdf417faa4ccd7c2e5a8a938e90ec96	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
29	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:47.104485	12	d5df753d03c31ba02ab7e84813aab5e369457d445fa704c10029eece76bbee68	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "QA LIVE 2de3c7ea", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
30	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:47.324055	12	798aca25bd06bfccdc0fe0e4a68d8c934ee5797ad59f69c6830f6045f552834b	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
31	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-18 21:51:47.377595	12	9ec923ccb23d9a80253233a846f0f2b56f42c7d002db7507a0be26b6ed031813	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
32	9	RESUMEN	RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:47.576048	12	e2e9c763ec8ed6cf3939c8571c895e57ea967331a4f6385d85fd9a3584eeb677	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [], "tecnologias": [], "candidato_id": 12, "solicitud_id": 1, "clasificacion": "APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand2.m5@sakura.cl", "candidato_nombre": "Candidato Dos QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000002", "estado_postulacion": "Seleccionado", "motivo_clasificacion": ["Estado de postulaci├│n: Seleccionado"], "puede_enviar_rechazo": false, "clasificacion_sugerida": false, "solicitud_candidato_id": 9, "puede_enviar_directivos": true}
33	8	RESUMEN	RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	/app/storage/informes/resumen/RESUMEN_Candidato_Uno_QA_SOL_000001.pdf	2026-08-18 21:51:47.63378	12	a6161ecc10f290f2927f279ceca1ab9515c48f6548981a4c0a4ebd8de6eab87f	{"cargo": "Desarrollador Backend", "match": 90.0, "cargo_id": 1, "tecnicas": [{"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "Cuestionario Tecnico Backend Python Senior", "cuestionario_id": 1}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-184117", "cuestionario_id": 4}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-184117", "cuestionario_id": 5}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-184117", "cuestionario_id": 6}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-184117", "cuestionario_id": 7}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-184117", "cuestionario_id": 8}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260813-210328", "cuestionario_id": 9}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260813-210328", "cuestionario_id": 10}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260813-210328", "cuestionario_id": 11}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260813-210328", "cuestionario_id": 12}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260813-210328", "cuestionario_id": 13}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 IND-20260814-173441", "cuestionario_id": 14}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 MASS-20260814-173441", "cuestionario_id": 15}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-20260814-173441", "cuestionario_id": 16}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 ALL-PAST-20260814-173441", "cuestionario_id": 17}, {"estado": null, "aprobado": null, "porcentaje": null, "cuestionario": "QA LIVE M4 TECH-20260814-173441", "cuestionario_id": 18}], "entrevistas": [{"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 2, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 2, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 4, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 4, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado", "observacion": "QA editada", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}, {"tipo": "RRHH", "tipo_id": 1, "resultado": "Aprobado con Observaciones", "observacion": "QA segundo", "entrevista_id": 11, "entrevistador": "Recruiter QA M5", "entrevistador_id": 13}, {"tipo": "Tecnica", "tipo_id": 2, "resultado": "Aprobado", "observacion": "QA segundo tipo", "entrevista_id": 11, "entrevistador": "Admin QA M5", "entrevistador_id": 12}], "tecnologias": [], "candidato_id": 11, "solicitud_id": 1, "clasificacion": "NO_APROBADO", "disponibilidad": "Inmediata", "candidato_email": "qa.cand1.m5@sakura.cl", "candidato_nombre": "Candidato Uno QA", "solicitud_codigo": "SOL-000001", "solicitud_titulo": "Desarrollador Senior Backend Python (Presencial)", "disponibilidad_id": 1, "candidato_telefono": "970000001", "estado_postulacion": "Descartado", "motivo_clasificacion": ["Estado de postulaci├│n: Descartado"], "puede_enviar_rechazo": true, "clasificacion_sugerida": false, "solicitud_candidato_id": 8, "puede_enviar_directivos": false}
34	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:47.754079	12	9f62f4e31a4d2208d7e65e5d7985390963647f3cedd7fd17df9ff77305e1432b	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
35	4	CV_CORPORATIVO	CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_QA_ModuloTres_SOL_000014.pdf	2026-08-18 21:51:47.810073	12	f0224eeb58154ecdf3fef9d0eac42384c9835ba44edde72471624bdedbd10ac8	{"pais": null, "nombre": "QA ModuloTres", "titulo": "QA PATCH 6c870a39", "idiomas": [], "educacion": [], "fortalezas": ["Conocimientos t├®cnicos destacados en PostgreSQL.", "Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Candidato generado por QA LIVE 6c870a39", "perfil_profesional": "Candidato generado por QA LIVE 6c870a39", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {"Bases de Datos": [{"anios": 6, "nivel": "Trainee", "categoria": "Bases de Datos", "habilidad": "PostgreSQL"}]}}
36	9	CV_CORPORATIVO	CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	/app/storage/informes/cv_corporativo/CV_ELITSOFT_Candidato_Dos_QA_SOL_000001.pdf	2026-08-18 21:51:47.987479	12	59ef63556f86ff4e22bdaed8527da144b20dae3a2a6bc5baf53da9db0bdbcc33	{"pais": null, "nombre": "Candidato Dos QA", "titulo": "Ingeniero QA", "idiomas": [], "educacion": [], "fortalezas": ["Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato."], "experiencia": [], "certificaciones": [], "resumen_ejecutivo": "Segundo candidato para QA LIVE Modulo 5.", "perfil_profesional": "Segundo candidato para QA LIVE Modulo 5.", "roles_recomendados": ["Desarrollador Backend ÔÇô por su alineaci├│n con la solicitud y experiencia declarada."], "habilidades_por_categoria": {}}
\.


--
-- Data for Name: tbl_empresa; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_empresa (emp_id, emp_nombre, emp_identificacion) FROM stdin;
1	Banco de Chile	97004000-5
2	Sparta	76074938-9
3	LATAM	89862200-2
4	Elitsoft	76876845-5
\.


--
-- Data for Name: tbl_estado_cuestionario_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_cuestionario_candidato (escc_id, escc_nombre) FROM stdin;
1	Asignado
2	En Progreso
3	Finalizado
4	Vencido
5	Cancelado
6	Error Tecnico
\.


--
-- Data for Name: tbl_estado_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_entrevista (esev_id, esev_nombre, esev_descripcion) FROM stdin;
1	Pendiente	La entrevista fue agendada y se enviaron las invitaciones correspondientes.
2	Confirmada	Todos los participantes confirmaron su asistencia y la entrevista se mantiene programada.
3	Realizada	La entrevista se llevo a cabo exitosamente.
4	Reprogramada	La entrevista fue reagendada para una nueva fecha y hora.
5	Cancelada	La entrevista fue cancelada por el postulante, entrevistador o empresa.
6	No Asistio	El postulante o uno de los participantes no asistio a la entrevista programada.
\.


--
-- Data for Name: tbl_estado_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_solicitud (essl_id, essl_nombre, essl_descripcion) FROM stdin;
1	Pendiente	La solicitud fue creada por un administrador y esta pendiente de ser tomada por un reclutador.
2	En Curso	La vacante esta activa, publicada y recibiendo postulaciones. Es administrada por el reclutador asignado.
3	En Entrevistas	La recepcion de postulaciones finalizo y los candidatos seleccionados se encuentran en proceso de entrevistas y evaluacion.
4	Cancelado	El proceso de seleccion fue cancelado por decision del cliente, cambios presupuestarios u otras razones.
5	Cerrado	La vacante fue cubierta exitosamente mediante la contratacion de un candidato.
6	Pausado	El proceso de seleccion se encuentra suspendido temporalmente y podra reanudarse posteriormente.
\.


--
-- Data for Name: tbl_estado_solicitud_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_solicitud_candidato (essc_id, essc_nombre, essc_descripcion) FROM stdin;
1	En revision	El CV fue recibido y el reclutador evalua si cumple los requisitos minimos.
2	En entrevista	El candidato avanzo y se encuentra en etapa de evaluaciones o entrevistas.
3	Inhabilitado	No cumple con las politicas basicas o fallo filtros criticos del sistema. Requiere asociar un motivo de rechazo.
4	Seleccionado	El candidato supero todas las etapas y es el elegido para la oferta final.
5	Descartado	La postulacion finalizo sin exito. Requiere asociar un motivo de rechazo.
6	Contratado	El candidato acepto la oferta y se cerro formalmente su flujo.
\.


--
-- Data for Name: tbl_estado_usuario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estado_usuario (esusr_id, esusr_nombre, esusr_descripcion) FROM stdin;
1	Activo	Usuario habilitado para operar plenamente en la plataforma.
2	Inactivo	Usuario deshabilitado temporalmente; no puede iniciar sesion.
3	Bloqueado	Cuenta suspendida automaticamente por exceso de intentos fallidos de inicio de sesion.
4	Eliminado	Usuario eliminado de forma logica para conservar la informacion y la auditoria historica.
\.


--
-- Data for Name: tbl_estudio_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_estudio_candidato (etcd_id, etcd_candidato_id, etcd_nivel_educacional_id, etcd_institucion_id, etcd_carrera_id, etcd_fecha_inicio, etcd_fecha_fin) FROM stdin;
1	1	5	3	2	2010-03-01	2015-12-15
2	1	6	29	2	2021-04-01	2021-09-30
3	1	8	1	20	2022-03-01	2023-12-20
4	1	6	34	2	2024-05-01	2024-08-31
\.


--
-- Data for Name: tbl_evaluacion_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_evaluacion_entrevista (even_id, even_nombre_resultado_id, even_observacion, even_cita_entrevista_id, even_usuario_id, even_tipo_entrevista_id, even_fecha_creacion, even_fecha_actualizacion) FROM stdin;
1	1	Candidato ha aprobado la entrevista.	1	2	2	2026-08-14 17:38:29.069795	2026-08-14 17:38:29.069795
3	2	QA segundo	2	13	1	2026-08-17 14:37:39.033598	2026-08-17 14:37:39.033604
4	1	QA segundo tipo	2	12	2	2026-08-17 14:37:39.095923	2026-08-17 14:37:39.095933
2	1	QA editada	2	12	1	2026-08-17 14:37:38.935438	2026-08-17 14:37:39.168196
6	2	QA segundo	4	13	1	2026-08-17 14:41:54.308737	2026-08-17 14:41:54.308745
7	1	QA segundo tipo	4	12	2	2026-08-17 14:41:54.398085	2026-08-17 14:41:54.398094
5	1	QA editada	4	12	1	2026-08-17 14:41:54.185305	2026-08-17 14:41:54.437005
9	2	QA segundo	11	13	1	2026-08-17 17:17:52.616044	2026-08-17 17:17:52.61605
10	1	QA segundo tipo	11	12	2	2026-08-17 17:17:52.657491	2026-08-17 17:17:52.657496
8	1	QA editada	11	12	1	2026-08-17 17:17:52.588266	2026-08-17 17:17:52.681368
\.


--
-- Data for Name: tbl_experiencia_laboral; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_experiencia_laboral (expl_id, expl_candidato_id, expl_empresa_id, expl_cargo_id, expl_descripcion_funciones, expl_fecha_inicio, expl_fecha_fin) FROM stdin;
1	1	2	1	Desarrollo y mantencion de APIs REST en Python, consultas PostgreSQL y soporte de aplicaciones internas.	2016-01-04	2018-06-30
2	1	1	3	Desarrollo de aplicaciones Full Stack utilizando FastAPI, Angular, Docker y PostgreSQL bajo metodologia Scrum.	2018-07-02	2021-12-31
3	1	3	1	Diseno de microservicios, integraciones con servicios cloud y optimizacion de procesos backend para plataformas corporativas.	2022-01-03	2024-08-31
4	1	4	20	Liderazgo tecnico del equipo backend, definicion de arquitectura, revision de codigo y apoyo en decisiones tecnicas del proyecto.	2024-09-02	\N
\.


--
-- Data for Name: tbl_experiencia_laboral_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_experiencia_laboral_habilidad (exph_experiencia_laboral_id, exph_habilidad_id) FROM stdin;
1	7
1	1
1	29
2	7
2	13
2	21
2	23
2	27
2	1
2	29
2	40
3	7
3	13
3	27
3	28
3	33
3	45
3	1
3	29
4	7
4	13
4	27
4	28
4	33
4	29
4	30
4	43
4	44
4	40
\.


--
-- Data for Name: tbl_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_habilidad (hab_id, hab_nombre, hab_descripcion, hab_categoria_habilidad_id) FROM stdin;
27	Docker	Creacion de imagenes optimizadas y orquestacion de entornos con Docker Compose.	4
28	Kubernetes	Orquestacion y administracion de contenedores.	4
1	PostgreSQL	Modelamiento fisico de bases de datos, optimizacion de consultas, indices y triggers.	3
2	MySQL	Administracion y desarrollo de bases de datos MySQL.	3
3	SQL Server	Desarrollo y administracion de bases de datos Microsoft SQL Server.	3
4	Oracle Database	Desarrollo y administracion de bases de datos Oracle.	3
5	MongoDB	Base de datos NoSQL orientada a documentos.	3
6	Redis	Base de datos en memoria para cache y alto rendimiento.	3
7	Python	Desarrollo de aplicaciones y automatizaciones utilizando Python.	1
8	Java	Desarrollo de aplicaciones empresariales utilizando Java.	1
9	C#	Desarrollo de aplicaciones sobre la plataforma .NET.	1
10	Node.js	Desarrollo de aplicaciones backend con JavaScript.	1
11	PHP	Desarrollo de aplicaciones web con PHP.	1
12	Go	Desarrollo de servicios de alto rendimiento con Go.	1
19	HTML	Desarrollo de interfaces web mediante HTML5.	1
20	CSS	Diseno de interfaces mediante hojas de estilo CSS3.	1
21	JavaScript	Desarrollo de aplicaciones web con JavaScript.	1
22	TypeScript	Desarrollo de aplicaciones tipadas sobre JavaScript.	1
13	FastAPI	Desarrollo de APIs REST de alto rendimiento con Python.	2
14	Django	Desarrollo de aplicaciones web utilizando Django.	2
15	Flask	Desarrollo de APIs y aplicaciones ligeras con Flask.	2
16	Spring Boot	Desarrollo de aplicaciones Java empresariales.	2
17	ASP.NET Core	Desarrollo de aplicaciones web con .NET.	2
18	Express.js	Desarrollo de APIs REST con Node.js.	2
23	Angular	Desarrollo de aplicaciones SPA con Angular.	2
24	React	Desarrollo de interfaces de usuario con React.	2
25	Vue.js	Desarrollo de aplicaciones web con Vue.js.	2
26	Bootstrap	Desarrollo de interfaces responsivas utilizando Bootstrap.	2
29	Git	Control de versiones mediante Git.	4
30	GitHub	Gestion de repositorios y colaboracion mediante GitHub.	4
31	GitLab	Administracion de repositorios y pipelines CI/CD.	4
32	Jenkins	Automatizacion de integracion y despliegue continuo.	4
33	Amazon Web Services (AWS)	Desarrollo e implementacion de soluciones en AWS.	4
34	Microsoft Azure	Desarrollo e implementacion de soluciones en Azure.	4
35	Google Cloud Platform (GCP)	Desarrollo e implementacion de soluciones en Google Cloud.	4
36	Selenium	Automatizacion de pruebas funcionales.	5
37	Cypress	Automatizacion de pruebas end-to-end para aplicaciones web.	5
38	Postman	Pruebas y documentacion de APIs REST.	5
39	JMeter	Pruebas de carga y rendimiento.	5
43	Jira	Gestion de proyectos y seguimiento de incidencias.	5
44	Confluence	Documentacion colaborativa de proyectos.	5
45	Linux	Administracion de sistemas operativos Linux.	5
46	Windows Server	Administracion de servidores Windows.	5
47	Power BI	Desarrollo de dashboards e indicadores de negocio.	5
48	Excel Avanzado	Analisis y manipulacion avanzada de datos en Microsoft Excel.	5
49	Ciberseguridad	Implementacion de controles y buenas practicas de seguridad informatica.	5
50	OWASP	Aplicacion de buenas practicas de desarrollo seguro.	5
51	OAuth 2.0	Implementacion de autenticacion y autorizacion segura.	5
52	JWT	Implementacion de autenticacion mediante JSON Web Token.	5
40	Scrum	Trabajo bajo metodologia agil Scrum.	6
41	Kanban	Gestion visual del trabajo mediante Kanban.	6
42	Agile	Aplicacion de metodologias agiles de desarrollo.	6
\.


--
-- Data for Name: tbl_historial_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_historial_solicitud (hsol_id, hsol_solicitud_id, hsol_estado_anterior_id, hsol_estado_actual_id, hsol_fecha_cambio, hsol_usuario_id, hsol_comentario) FROM stdin;
1	1	\N	1	2026-07-06 09:00:00	1	Creacion de la solicitud de personal enviada por el cliente.
2	1	1	2	2026-07-07 09:00:00	2	Vacante tomada por el reclutador y publicada oficialmente en plataformas de empleo.
3	7	\N	1	2026-08-07 16:55:58.659469	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
4	7	1	2	2026-08-07 16:58:38.949957	2	Aprobaci├│n de la vacante e inicio formal del proceso de reclutamiento para SOL-005
5	7	2	1	2026-08-07 17:15:30.257059	1	test historial SOL-005
6	7	1	2	2026-08-07 17:20:02.506268	1	test 2 historial SOL-005
7	7	2	1	2026-08-07 13:24:00.557267	1	test 3 historial SOL-005
8	8	\N	1	2026-08-07 13:37:18.284816	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
9	9	\N	1	2026-08-07 13:38:36.238714	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
10	7	1	4	2026-08-07 15:50:13.926865	1	test 6 historial SOL-005
11	7	4	5	2026-08-07 16:15:25.998341	1	test 7 historial SOL-005
12	4	2	5	2026-08-10 12:05:18.280043	1	test 4 historial 
13	4	5	4	2026-08-10 12:05:49.086232	1	Desactivaci├│n (Borrado L├│gico) de la solicitud
14	10	\N	1	2026-08-12 16:17:07.899479	1	QA LIVE RUN a0837ee5
15	10	1	2	2026-08-12 16:17:08.184114	1	Cambio de estado: Pendiente -> En Curso
16	10	2	6	2026-08-12 16:17:08.350753	1	Pausa QA a0837ee5
17	10	6	2	2026-08-12 16:17:08.389008	1	Cambio de estado: Pausado -> En Curso
18	10	2	4	2026-08-12 16:17:08.465958	1	Cierre QA LIVE a0837ee5
19	11	\N	1	2026-08-12 17:40:21.902355	1	QA LIVE RUN 056e0077
20	11	1	2	2026-08-12 17:40:22.171434	1	Cambio de estado: Pendiente -> En Curso
21	11	2	6	2026-08-12 17:40:22.301638	1	Pausa QA 056e0077
22	11	6	2	2026-08-12 17:40:22.344446	1	Cambio de estado: Pausado -> En Curso
23	11	2	4	2026-08-12 17:40:22.401155	1	Cierre QA LIVE 056e0077
24	12	\N	1	2026-08-13 13:25:06.928864	1	RUN 6324b046
25	12	1	2	2026-08-13 13:25:06.998498	1	Cambio de estado: Pendiente -> En Curso
26	12	2	3	2026-08-13 13:25:07.040181	1	Cambio de estado: En Curso -> En Entrevistas
27	12	3	5	2026-08-13 13:25:07.277554	1	Cambio de estado: En Entrevistas -> Cerrado
28	13	\N	1	2026-08-13 15:50:05.99666	1	RUN 17b5f4d2
29	13	1	2	2026-08-13 15:50:06.138641	1	Cambio de estado: Pendiente -> En Curso
30	13	2	3	2026-08-13 15:50:06.222799	1	Cambio de estado: En Curso -> En Entrevistas
31	13	3	5	2026-08-13 15:50:06.644415	1	Cambio de estado: En Entrevistas -> Cerrado
32	14	\N	1	2026-08-13 16:16:31.376312	1	RUN 6c870a39
33	14	1	2	2026-08-13 16:16:31.476917	1	Cambio de estado: Pendiente -> En Curso
34	14	2	3	2026-08-13 16:16:31.760554	1	Cambio de estado: En Curso -> En Entrevistas
35	14	3	5	2026-08-13 16:16:32.216464	1	Cambio de estado: En Entrevistas -> Cerrado
36	15	\N	1	2026-08-14 17:13:03.824363	1	QA LIVE RUN 2d283271
37	15	1	2	2026-08-14 17:13:04.228332	1	Cambio de estado: Pendiente -> En Curso
38	15	2	6	2026-08-14 17:13:04.303978	1	Pausa QA 2d283271
39	15	6	2	2026-08-14 17:13:04.356326	1	Cambio de estado: Pausado -> En Curso
40	15	2	4	2026-08-14 17:13:04.433235	1	Cierre QA LIVE 2d283271
41	16	\N	1	2026-08-14 17:17:34.694005	1	RUN 680ddf0e
42	16	1	2	2026-08-14 17:17:34.7372	1	Cambio de estado: Pendiente -> En Curso
43	16	2	3	2026-08-14 17:17:34.788027	1	Cambio de estado: En Curso -> En Entrevistas
44	16	3	5	2026-08-14 17:17:35.158334	1	Cambio de estado: En Entrevistas -> Cerrado
45	1	3	4	2026-08-17 19:54:57.039641	1	Solicitud cancelada por confirmaci├│n del usuario.
\.


--
-- Data for Name: tbl_idioma; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_idioma (idio_id, idio_nombre) FROM stdin;
1	Espa├▒ol
2	Ingl├®s
3	Portugu├®s
4	Franc├®s
5	Alem├ín
6	Italiano
7	Otro
\.


--
-- Data for Name: tbl_institucion; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_institucion (inst_id, inst_nombre, inst_tipo_institucion_id) FROM stdin;
1	Universidad de Chile	1
2	Pontificia Universidad Catolica de Chile	1
3	Universidad de Santiago de Chile	1
4	Universidad de Concepcion	1
5	Universidad Tecnica Federico Santa Maria	1
6	Universidad Adolfo Ibanez	1
7	Universidad Diego Portales	1
8	Universidad Andres Bello	1
9	Universidad Mayor	1
10	Universidad San Sebastian	1
11	Universidad Catolica del Norte	1
12	Universidad de Valparaiso	1
13	Universidad Austral de Chile	1
14	Universidad de La Serena	1
15	Universidad del Desarrollo	1
16	INACAP	2
17	Duoc UC	2
18	AIEP	2
19	Santo Tomas	2
20	IP Chile	2
21	IPLACEX	2
22	Instituto Profesional Providencia (IPP)	2
23	CFT Santo Tomas	3
24	CFT Estatal de Santiago	3
25	CFT ENAC	3
26	Desafio Latam	6
27	Talento Digital para Chile	6
28	Coderhouse	6
29	Platzi	6
30	Henry	6
31	Cisco Networking Academy	5
32	Microsoft Learn	5
33	Amazon Web Services (AWS)	5
34	Google Cloud Skills Boost	5
35	Oracle University	5
36	Scrum.org	5
37	Project Management Institute (PMI)	5
\.


--
-- Data for Name: tbl_modalidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_modalidad (mdld_id, mdld_nombre, mdld_descripcion) FROM stdin;
1	Presencial	Trabajo obligatorio en las oficinas del cliente de lunes a viernes.
2	Remoto	Trabajo completamente desde el hogar, mediante teletrabajo nacional o internacional.
3	Hibrido	Esquema flexible de trabajo que combina dÔö£┬ías presenciales y remotos (por ejemplo, 3 dÔö£┬ías en casa y 2 dÔö£┬ías en la oficina).
\.


--
-- Data for Name: tbl_motivo_rechazo; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_motivo_rechazo (mtrc_id, mtrc_nombre, mtrc_descripcion) FROM stdin;
1	Renta fuera de rango	La pretension salarial del candidato supera el presupuesto de la vacante.
2	No cumple perfil tecnico	No cuenta con los anos de experiencia o el nivel requerido en las habilidades obligatorias.
3	No asistio a evaluacion	El candidato no asistio a la entrevista o no rindio los cuestionarios dentro del plazo establecido.
4	Decision propia del candidato	El postulante decidio retirarse del proceso por motivos personales o porque acepto otra oferta laboral.
5	Disponibilidad incompatible	La fecha de incorporacion del candidato no se ajusta a las necesidades de la vacante.
6	Documentacion incompleta	No presento la documentacion requerida para continuar el proceso.
7	Resultado insuficiente en evaluacion	No alcanzo el puntaje minimo en cuestionarios tecnicos o pruebas practicas.
8	Referencias laborales desfavorables	Las referencias obtenidas no respaldan el perfil del candidato.
9	Perfil no alineado con la cultura	El candidato no demostro un ajuste adecuado con la cultura o valores de la organizacion.
10	Vacante cancelada	El proceso fue cancelado por el cliente o la empresa antes de finalizar la seleccion.
11	Candidato no interesado	El candidato informo que ya no desea continuar en el proceso.
12	Otro	Motivo no contemplado en las categorias anteriores.
\.


--
-- Data for Name: tbl_nivel_educacional; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nivel_educacional (nved_id, nved_nombre) FROM stdin;
1	Ense├▒anza Media
2	Tenico Nivel Medio
3	Tecnico Profesional Nivel Superior
4	Universitario Incompleto
5	Universitario Completo
6	Diplomado
7	Magister
8	Doctorado
\.


--
-- Data for Name: tbl_nivel_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nivel_habilidad (nvhb_id, nvhb_nombre, nvhb_descripcion, nvhb_puntaje_base, nvhb_duracion) FROM stdin;
3	Junior	Posee conocimientos practicos iniciales y requiere supervision para desarrollar tareas.	15	1
4	Semi Senior	Trabaja de forma independiente, resuelve problemas complejos y aplica buenas practicas.	30	3
5	Senior	Profesional con amplia experiencia, lidera iniciativas, toma decisiones tecnicas y asesora a otros integrantes del equipo.	50	5
2	Trainee	Posee conocimientos fundamentales adquiridos mediante cursos, proyectos personales o formacion academica.	5	1
\.


--
-- Data for Name: tbl_nivel_idioma; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nivel_idioma (nvid_id, nvid_codigo, nvid_nombre, nvid_grupo, nvid_es_generico, nvid_orden, nvid_descripcion, nvid_activo) FROM stdin;
1	BAS	B├ísico	Basico	t	10	Nivel b├ísico gen├®rico. Utilizado cuando la fuente no permite determinar A1 o A2.	t
2	A1	B├ísico A1	Basico	f	11	CEFR A1 - Usuario b├ísico inicial.	t
3	A2	B├ísico A2	Basico	f	12	CEFR A2 - Usuario b├ísico.	t
4	INT	Intermedio	Intermedio	t	20	Nivel intermedio gen├®rico. Utilizado cuando la fuente no permite determinar B1 o B2.	t
5	B1	Intermedio B1	Intermedio	f	21	CEFR B1 - Usuario independiente intermedio.	t
6	B2	Intermedio B2	Intermedio	f	22	CEFR B2 - Usuario independiente intermedio alto.	t
7	AVA	Avanzado	Avanzado	t	30	Nivel avanzado gen├®rico. Utilizado cuando la fuente no permite determinar C1 o C2.	t
8	C1	Avanzado C1	Avanzado	f	31	CEFR C1 - Usuario competente avanzado.	t
9	C2	Avanzado C2	Avanzado	f	32	CEFR C2 - Usuario competente con dominio pleno.	t
10	NAT	Nativo	Nativo	f	40	Idioma nativo o de dominio equivalente a lengua materna.	t
\.


--
-- Data for Name: tbl_nombre_resultado; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_nombre_resultado (nore_id, nore_nombre) FROM stdin;
1	Aprobado
2	Aprobado con Observaciones
3	No Aprobado
4	En Espera
5	Requiere Segunda Entrevista
\.


--
-- Data for Name: tbl_notificacion_reclutamiento; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_notificacion_reclutamiento (ntfr_id, ntfr_solicitud_candidato_id, ntfr_tipo, ntfr_destinatario, ntfr_cc, ntfr_asunto, ntfr_cuerpo, ntfr_estado, ntfr_usuario_id, ntfr_fecha_creacion, ntfr_fecha_envio, ntfr_error) FROM stdin;
1	9	DIRECTIVOS	noelidch@gmail.com	\N	QA M6 6b10b963	Correo QA LIVE	ERROR	12	2026-08-17 22:18:35.513412	\N	La variable de entorno SMTP_USERNAME no est├í configurada
2	9	DIRECTIVOS	noelidch@gmail.com	\N	QA M6 279b039e	Correo QA LIVE	ERROR	12	2026-08-17 22:33:37.999315	\N	No fue posible enviar el correo
3	9	DIRECTIVOS	noelidch@gmail.com	\N	QA M6 2de3c7ea	Correo QA LIVE	ERROR	12	2026-08-18 21:51:50.077128	\N	No fue posible enviar el correo
\.


--
-- Data for Name: tbl_opcion_respuesta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_opcion_respuesta (opcr_id, opcr_pregunta_id, opcr_texto_opcion, opcr_es_correcta) FROM stdin;
1	1	FastAPI ofrece alto rendimiento gracias a Starlette y Pydantic, con soporte nativo para documentacion OpenAPI.	t
2	1	FastAPI solo puede utilizar bases de datos MySQL.	f
3	1	FastAPI reemplaza completamente el uso de Docker.	f
4	2	Analizar el plan de ejecucion, crear indices adecuados y optimizar la consulta.	t
5	2	Eliminar todos los indices existentes.	f
6	2	Aumentar la memoria RAM siempre soluciona el problema.	f
7	3	B-Tree se utiliza para igualdad y rangos; GIN para busquedas complejas como JSONB o arrays.	t
8	3	GIN reemplaza completamente a B-Tree en cualquier escenario.	f
9	3	Los indices solo mejoran consultas INSERT.	f
10	4	Separar el proyecto en capas como routers, servicios, modelos y repositorios.	t
11	4	Colocar toda la logica dentro de un unico archivo main.py.	f
12	4	Evitar el uso de modulos para simplificar el codigo.	f
13	5	Una imagen es una plantilla y un contenedor es una instancia en ejecucion.	t
14	5	Una imagen solo existe mientras el contenedor esta activo.	f
15	5	Los contenedores no requieren una imagen para ejecutarse.	f
16	6	Resolver manualmente el conflicto, validar los cambios y realizar el commit.	t
17	6	Eliminar la rama remota para evitar conflictos.	f
18	6	Forzar siempre un git push.	f
19	7	Generando un token firmado que es validado en cada solicitud protegida.	t
20	7	Guardando la contrasena del usuario en texto plano.	f
21	7	Utilizando solamente sesiones HTTP sin autenticacion.	f
22	8	Kubernetes automatiza escalamiento, disponibilidad y administracion de contenedores.	t
23	8	Kubernetes reemplaza completamente el uso de Git.	f
24	8	Docker Compose es obligatorio para ejecutar Kubernetes.	f
25	9	Dividir funcionalidades en servicios independientes con comunicacion mediante APIs.	t
26	9	Mantener toda la aplicacion dentro de un unico archivo.	f
27	9	Eliminar completamente las bases de datos relacionales.	f
28	10	Analizar impacto, informar al Product Owner y priorizar la incidencia dentro del Sprint.	t
29	10	Esperar al siguiente Sprint para revisar cualquier problema.	f
30	10	Cancelar automaticamente el Sprint.	f
\.


--
-- Data for Name: tbl_pais; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pais (pais_id, pais_nombre) FROM stdin;
1	Chile
\.


--
-- Data for Name: tbl_password_reset_token; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_password_reset_token (prst_id, prst_usuario_id, prst_token_hash, prst_fecha_creacion, prst_fecha_expiracion, prst_fecha_uso, prst_fecha_revocacion) FROM stdin;
\.


--
-- Data for Name: tbl_permiso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_permiso (per_id, per_nombre, per_descripcion) FROM stdin;
1	USR_CREATE	Crear usuarios internos
2	USR_VIEW	Consultar usuarios
3	USR_UPDATE	Modificar usuarios
4	USR_DELETE	Desactivar usuarios
5	SOL_CREATE	Crear solicitudes de personal
6	SOL_VIEW	Consultar solicitudes
7	SOL_UPDATE	Modificar solicitudes
8	SOL_DELETE	Cerrar o eliminar solicitudes
9	CAN_VIEW	Ver candidatos
10	CAN_UPDATE	Actualizar informacion o estado del candidato
11	CAN_DELETE	Eliminar o desactivar candidato
12	CUEST_CREATE	Crear cuestionarios
13	CUEST_ASSIGN	Asignar cuestionarios
14	CUEST_VIEW	Ver resultados de cuestionarios
15	INT_CREATE	Agendar entrevistas
16	INT_VIEW	Ver entrevistas
17	INT_UPDATE	Modificar entrevistas
18	INT_EVALUATE	Registrar evaluacion de entrevista
19	CAT_ADMIN	Administrar catalogos maestros
20	REP_VIEW	Consultar reportes y metricas
\.


--
-- Data for Name: tbl_plantilla_notificacion; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_plantilla_notificacion (plnt_id, plnt_tipo, plnt_nombre, plnt_asunto, plnt_cuerpo, plnt_activa, plnt_fecha_actualizacion, plnt_usuario_actualizacion_id) FROM stdin;
2	AGRADECIMIENTO	Agradecimiento de participaci├│n	Gracias por participar - {cargo}	Estimado/a {nombre},\n\nAgradecemos tu participaci├│n en el proceso {codigo_solicitud} para el cargo {cargo}.\n\nSaludos cordiales,\nEquipo de Reclutamiento ELITSOFT	t	\N	\N
3	DIRECTIVOS	Presentaci├│n de candidatos aprobados	Candidatos aprobados - {cargo} - {codigo_solicitud}	Estimados/as,\n\nAdjuntamos los CVs corporativos de los candidatos aprobados para el proceso {codigo_solicitud}, cargo {cargo}, para su revisi├│n y decisi├│n final.\n\nSaludos cordiales,\nEquipo de Reclutamiento ELITSOFT	t	\N	\N
1	RECHAZO	Cierre de proceso - rechazo	Cierre proceso de selecci├│n - {cargo}	Estimado/a {nombre},\n\nAgradecemos sinceramente tu participaci├│n en el proceso de selecci├│n para el cargo {cargo}, asociado a la solicitud {codigo_solicitud}.\n\nEn esta oportunidad el proceso ha finalizado y no continuaremos con tu postulaci├│n. Valoramos el tiempo y disposici├│n demostrados durante las distintas etapas.\n\nEsperamos poder considerarte en futuras oportunidades que se ajusten a tu perfil.\n\nSaludos cordiales,\nEquipo de Reclutamiento ELITSOFT	t	2026-08-18 21:51:47.918514	12
\.


--
-- Data for Name: tbl_pregunta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pregunta (preg_id, preg_texto_pregunta, preg_habilidad_id, preg_nivel_habilidad_id, preg_fecha_creacion) FROM stdin;
1	Explique la diferencia entre una API REST tradicional y una desarrollada con FastAPI. Mencione sus principales ventajas.	13	4	2026-07-23 15:58:22.771352
2	Describa como optimizaria una consulta PostgreSQL que presenta tiempos elevados de respuesta.	1	4	2026-07-23 15:58:22.771352
3	Explique cuando utilizaria un indice B-Tree y cuando un indice GIN en PostgreSQL.	1	4	2026-07-23 15:58:22.771352
4	Describa como estructuraria un proyecto backend en Python siguiendo buenas practicas de arquitectura.	7	4	2026-07-23 15:58:22.771352
5	Explique la diferencia entre una imagen Docker y un contenedor Docker, indicando un caso de uso para cada uno.	27	3	2026-07-23 15:58:22.771352
6	Explique como resolveria un conflicto durante un proceso de merge utilizando Git.	29	3	2026-07-23 15:58:22.771352
7	Describa como implementaria autenticacion mediante JWT en una API REST.	7	4	2026-07-23 15:58:22.771352
8	Explique que ventajas ofrece Kubernetes frente al uso exclusivo de Docker Compose en ambientes productivos.	28	2	2026-07-23 15:58:22.771352
9	Describa una arquitectura de microservicios implementada por usted y los principales desafios encontrados.	13	4	2026-07-23 15:58:22.771352
10	Explique como priorizaria una incidencia critica durante un Sprint trabajando bajo metodologia Scrum.	40	3	2026-07-23 15:58:22.771352
\.


--
-- Data for Name: tbl_pregunta_cuestionario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_pregunta_cuestionario (prcu_pregunta_id, prcu_cuestionario_id, prcu_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	1	10
10	2	11
10	3	12
10	4	13
10	5	14
10	6	15
10	7	16
10	8	17
10	9	18
10	10	19
10	11	20
10	12	21
10	13	22
10	14	23
10	15	24
10	16	25
10	17	26
10	18	27
\.


--
-- Data for Name: tbl_prioridad_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_prioridad_solicitud (prsol_id, prsol_nombre, prsol_descripcion) FROM stdin;
1	Alta	Vacantes criticas que requieren cobertura en menos de 15 dias
2	Media	Procesos estandar con un tiempo estimado de cobertura de 30 dias
3	Baja	Busquedas preventivas o planes de expansion sin fecha limite estricta
\.


--
-- Data for Name: tbl_region; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_region (reg_id, reg_pais_id, reg_nombre) FROM stdin;
1	1	Arica y Parinacota
2	1	Tarapaca
3	1	Antofagasta
4	1	Atacama
5	1	Coquimbo
6	1	Valparaiso
7	1	Metropolitana de Santiago
8	1	Libertador General Bernardo OHiggins
9	1	Maule
10	1	Nuble
11	1	Biobio
12	1	La Araucania
13	1	Los Rios
14	1	Los Lagos
15	1	Aysen del General Carlos Ibanez del Campo
16	1	Magallanes y de la Antartica Chilena
\.


--
-- Data for Name: tbl_respuesta_pregunta; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_respuesta_pregunta (rspr_id, rspr_candidato_cuestionario_id, rspr_es_correcta, rspr_puntaje_obtenido, rspr_opcion_respuesta_id, rspr_pregunta_cuestionario_id) FROM stdin;
1	1	t	10	1	1
2	1	t	10	4	2
3	1	t	10	7	3
4	1	t	10	10	4
5	1	t	10	13	5
6	1	t	10	16	6
7	1	t	10	19	7
8	1	f	0	24	8
9	1	t	10	25	9
10	1	t	10	28	10
11	2	t	15	28	13
13	6	t	15	28	18
15	12	t	15	28	23
\.


--
-- Data for Name: tbl_rol; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_rol (rol_id, rol_nombre, rol_descripcion) FROM stdin;
1	Administrador	Administrador total del sistema con acceso global a todos los modulos.
2	Reclutador	Usuario que realiza el proceso de reclutamiento.
3	Candidato	Postulante externo que aplica a las ofertas laborales y responde cuestionarios.
4	Entrevistador	Colaborador tecnico o lider de area encargado de realizar entrevistas a los candidatos.
\.


--
-- Data for Name: tbl_rol_permiso; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_rol_permiso (rlpm_rol_id, rlpm_permiso_id) FROM stdin;
1	1
1	2
1	3
1	4
1	5
1	6
1	7
1	8
1	9
1	10
1	11
1	12
1	13
1	14
1	15
1	16
1	17
1	18
1	19
1	20
2	6
2	7
2	9
2	10
2	13
2	14
2	15
2	16
2	17
2	20
4	9
4	14
4	16
4	18
2	12
2	18
\.


--
-- Data for Name: tbl_solicitud; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud (sol_id, sol_codigo, sol_titulo, sol_cargo_id, sol_descripcion, sol_prioridad_id, sol_cantidad_vacantes, sol_cliente_id, sol_usuario_creador_id, sol_usuario_asignado_id, sol_modalidad_id, sol_salario_min, sol_salario_max, sol_fecha_creacion, sol_fecha_inicio_busqueda, sol_fecha_cierre_busqueda, sol_fecha_inicio_cliente, sol_estado_solicitud_id, sol_hora_inicio_jornada, sol_hora_fin_jornada, sol_tipo_contrato_id, sol_observacion) FROM stdin;
2	SOL-000002	Desarrollador Python Senior	\N	B├║squeda actualizada con aumento salarial.	\N	\N	1	1	\N	\N	2500000	3500000	\N	\N	\N	\N	4	\N	\N	\N	\N
8	SOL-000008	L├¡der T├®cnico Fullstack Python & React	1	B├║squeda activa para la c├®lula de innovaci├│n. Se requiere profesional con experiencia s├│lida en arquitectura de microservicios, liderazgo t├®cnico de equipos distribuidos y dise├▒o de APIs REST seguras.	1	3	1	1	2	1	3500000	4500000	\N	2026-08-10 09:00:00	2026-09-15 18:00:00	2026-10-01 09:00:00	1	09:00:00	18:00:00	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
9	SOL-000009	L├¡der T├®cnico Fullstack Python & React	1	B├║squeda activa para la c├®lula de innovaci├│n. Se requiere profesional con experiencia s├│lida en arquitectura de microservicios, liderazgo t├®cnico de equipos distribuidos y dise├▒o de APIs REST seguras.	1	3	1	1	2	1	3500000	4500000	2026-08-07 13:38:36.183106	2026-08-10 09:00:00	2026-09-15 18:00:00	2026-10-01 09:00:00	1	09:00:00	18:00:00	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
4	SOL-000004	L├¡der T├®cnico Fullstack Python & React	1	B├║squeda activa para la c├®lula de innovaci├│n. Se requiere profesional con experiencia s├│lida en arquitectura de microservicios, liderazgo t├®cnico de equipos distribuidos y dise├▒o de APIs REST seguras.	1	3	1	1	2	1	3500000	4500000	\N	2026-08-10 09:00:00	2026-09-15 18:00:00	2026-10-01 09:00:00	4	09:00:00	18:00:00	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
7	SOL-000007	L├¡der T├®cnico Fullstack Python & React	1	B├║squeda actualizada con aumento salarial.	1	3	1	1	2	1	3500000	5000000	\N	2026-08-10 09:00:00	2026-09-15 18:00:00	2026-10-01 09:00:00	5	09:00:00	18:00:00	1	Requerimiento urgente asignado al equipo de reclutamiento Q3.
10	SOL-000010	QA LIVE PATCH a0837ee5	1	Solicitud generada por QA LIVE M├│dulo 2	1	1	1	1	3	1	1000	2000	2026-08-12 16:17:07.887267	\N	\N	\N	4	\N	\N	1	QA LIVE RUN a0837ee5
11	SOL-000011	QA LIVE PATCH 056e0077	1	Solicitud generada por QA LIVE M├│dulo 2	1	1	1	1	3	1	1000	2000	2026-08-12 17:40:21.89793	\N	\N	\N	4	\N	\N	1	QA LIVE RUN 056e0077
12	SOL-000012	QA M3 cierre parcial 6324b046	1	Solicitud creada por QA LIVE M├│dulo 3	1	2	1	1	3	1	1000	2000	2026-08-13 13:25:06.92056	\N	\N	\N	5	\N	\N	1	RUN 6324b046
13	SOL-000013	QA M3 cierre parcial 17b5f4d2	1	Solicitud creada por QA LIVE M├│dulo 3	1	2	1	1	3	1	1000	2000	2026-08-13 15:50:05.990295	\N	\N	\N	5	\N	\N	1	RUN 17b5f4d2
14	SOL-000014	QA M3 cierre parcial 6c870a39	1	Solicitud creada por QA LIVE M├│dulo 3	1	2	1	1	3	1	1000	2000	2026-08-13 16:16:31.364526	\N	\N	\N	5	\N	\N	1	RUN 6c870a39
15	SOL-000015	QA LIVE PATCH 2d283271	1	Solicitud generada por QA LIVE M├│dulo 2	1	1	1	1	3	1	1000	2000	2026-08-14 17:13:03.812591	\N	\N	\N	4	\N	\N	1	QA LIVE RUN 2d283271
16	SOL-000016	QA M3 cierre parcial 680ddf0e	1	Solicitud creada por QA LIVE M├│dulo 3	1	2	1	1	3	1	1000	2000	2026-08-14 17:17:34.691519	\N	\N	\N	5	\N	\N	1	RUN 680ddf0e
1	SOL-000001	Desarrollador Senior Backend Python (Presencial)	1	Buscamos un Ingeniero Full Stack o Backend con mas de 5 anos de experiencia disenando arquitecturas basadas en microservicios, APIs REST con FastAPI y optimizacion de consultas SQL nativas en PostgreSQL bajo entornos Docker.	2	2	1	1	3	2	2500000	3000000	2026-07-21 11:00:00	2026-07-21 11:00:00	2026-07-21 18:00:00	2026-07-21 11:00:00	4	09:00:00	18:00:00	2	Solicitud de prueba.
\.


--
-- Data for Name: tbl_solicitud_candidato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud_candidato (slcd_id, slcd_candidato_id, slcd_solicitud_id, slcd_pretension_renta, slcd_puntaje_compatibilidad, slcd_estado_solicitud_candidato_id, slcd_fecha_postulacion, slcd_observaciones, slcd_motivo_rechazo_id) FROM stdin;
1	1	1	2800000	92.50	2	2026-07-02 09:30:00	Excelente experiencia en Python, FastAPI y Docker. Cumple con la mayoria de los requisitos solicitados.	\N
2	3	12	1500000	95.00	6	2026-08-13 17:25:07.103508	QA PATCH	\N
3	5	13	1500000	95.00	6	2026-08-13 19:50:06.339554	QA PATCH	\N
4	7	14	1500000	95.00	6	2026-08-13 20:16:31.882178	QA PATCH	\N
6	5	1	\N	\N	1	\N	\N	\N
7	9	16	1500000	95.00	6	2026-08-14 21:17:34.869922	QA PATCH	\N
8	11	1	2000000	90.00	5	2026-08-17 10:20:42.104393	Postulacion QA LIVE M5	\N
9	12	1	2000000	90.00	4	2026-08-17 10:20:42.104393	Postulacion QA LIVE M5	\N
\.


--
-- Data for Name: tbl_solicitud_habilidad; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_solicitud_habilidad (solhb_id, solhb_solicitud_id, solhb_habilidad_id, solhb_nivel_habilidad_id, solhb_anios_experiencia_req, solhb_es_excluyente) FROM stdin;
1	1	7	4	5	t
2	1	1	3	3	t
3	1	13	4	4	t
4	1	27	3	3	t
5	1	29	3	3	t
6	1	45	2	2	f
7	1	33	2	2	f
8	1	28	2	1	f
9	1	30	2	2	f
10	1	40	2	1	f
11	2	7	3	3	t
12	2	13	2	1	f
16	2	26	2	2	f
20	4	1	5	5	t
21	4	2	4	3	t
22	4	3	3	2	f
23	7	1	5	5	t
24	7	2	4	3	t
25	7	3	3	2	f
26	8	1	2	1	t
27	9	1	2	1	t
28	7	26	2	2	f
29	10	1	2	1	t
30	11	1	2	1	t
31	12	1	2	1	t
32	13	1	2	1	t
33	14	1	2	1	t
34	15	1	2	1	t
35	16	1	2	1	t
\.


--
-- Data for Name: tbl_tipo_contrato; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_contrato (tpct_id, tpct_nombre, tpct_descripcion) FROM stdin;
1	Indefinido	Contrato laboral sin fecha de termino, vigente hasta que una de las partes lo finalice conforme a la legislacion.
2	Plazo Fijo	Contrato laboral con una fecha de inicio y una fecha de termino previamente establecidas.
3	Por Proyecto	Contrato cuya duracion esta vinculada a la ejecucion de un proyecto o una tarea especifica. Finaliza una vez concluido el proyecto.
4	Practica Profesional	Acuerdo destinado a estudiantes o egresados para desarrollar experiencia practica relacionada con su formacion academica.
5	Honorarios	Prestacion de servicios independiente, sin vinculo laboral directo, regulada mediante la emision de boletas de honorarios.
\.


--
-- Data for Name: tbl_tipo_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_entrevista (tpet_id, tpet_nombre, tpet_descripcion) FROM stdin;
1	RRHH	Entrevista inicial de filtro de competencias blandas, expectativas salariales y de cultura.
2	Tecnica	Evaluacion de habilidades duras, arquitectura de software y codigo en vivo.
3	Cliente	Entrevista realizada por el cliente o lider del area para validar el ajuste al equipo y aprobar la contratacion.
4	Psicolaboral	Evaluacion psicolaboral realizada por un psicologo para analizar competencias, personalidad y adecuacion al cargo.
5	Gerencial	Entrevista realizada por gerencias o directivos para cargos estrategicos o de liderazgo.
6	Ingles	Evaluacion del nivel de comunicacion oral y escrita en idioma ingles.
\.


--
-- Data for Name: tbl_tipo_institucion; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_tipo_institucion (tint_id, tint_tipo_institucion) FROM stdin;
1	Universidad
2	Instituto Profesional
3	Centro de Formacion Tecnica
4	Colegio
5	Organismo Certificador
6	Academia / Bootcamp
7	Otro
\.


--
-- Data for Name: tbl_usuario; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_usuario (usr_id, usr_rol_id, usr_estado_usuario_id, usr_area_id, usr_nombres, usr_apellido_paterno, usr_apellido_materno, usr_rut_sin_dv, usr_dv, usr_telefono, usr_email, usr_contrasena) FROM stdin;
7	\N	4	\N	QAUpdated	Auto	\N	64f1b104	K	933333333	qauf1b112@qa.cl	$2b$12$M6U.BbsQjxAxSxjVO9X.OuVy0.Ae3/Ydy7u8mp3/K8DFP5/xqGMjW
6	\N	4	\N	QATest	Auto	\N	63f1b103	K	911111111	qaif1b112@qa.cl	$2b$12$pbzYttoM46C8ci6/W5tc7ubCVk7JJW5tZivu4acRhICRO8TAQZWm.
5	\N	4	\N	QATest	Auto	\N	62f1b102	K	911111111	qanf1b112@qa.cl	$2b$12$73HTApOKK5VIBKbkKnEZg.igoY3JENngctJZ5g/6f6wZbsBV1nR8u
4	\N	4	\N	QATest	Auto	\N	61f1b101	K	911111111	qavf1b112@qa.cl	$2b$12$9ysx8qfqfSWssHfo9UhqNuorlGrX1Ia8FqA4QVw9t43KOeRCjZOBy
1	1	1	1	Noelid	Chavez	Rodriguez	26380143	1	931448429	noelidch@gmail.com	$2b$12$S0YM8KNrn7v7eLGudRKiKOmBX.D/6Os51ifKaCqgXAGJwxIfOBnWy
3	2	1	2	Felipe	Valdes	Mella	18002594	4	978611801	f.valdesmella@gmail.com	$2b$12$d/.weLW56ESPmI/U6fij2e6dJc1PsNAw1VTJDD0t/9bYy0x3SNssa
2	4	1	3	Catherine	Rebolledo	Pastene	23040635	9	957034447	cathyrebopas@gmail.com	$2b$12$MGTM3.TM3g8S.yJ9A18e8eZNfiB3.iFHL8bya1.cqFSl0Sp9D9ObW
11	\N	4	\N	QAUpdated	Auto	\N	64b9b404	K	933333333	qaub9b4c8@qa.cl	$2b$12$D21NVfQenCWjvQ1P00lDaeWvyyg7ZuC9WdIw4d8GpvJaBj20cMMvm
10	\N	4	\N	QATest	Auto	\N	63b9b403	K	911111111	qaib9b4c8@qa.cl	$2b$12$QdKGm8u23y.uyGLycobdaO5LZv1CgK1RXNI0W5yzHWj3n0Tuubk1G
9	\N	4	\N	QATest	Auto	\N	62b9b402	K	911111111	qanb9b4c8@qa.cl	$2b$12$RdlXEHQwQ3ii4BocgDaMCuRnOmPZGiFM1Qfl4hdi.QNHapuVfe2tK
8	\N	4	\N	QATest	Auto	\N	61b9b401	K	911111111	qavb9b4c8@qa.cl	$2b$12$Gek6Bfxu0G9UZ..iqxH55epKEAJpwE8d3/.uCqhDBtb3RraGI2Aqi
12	1	1	1	Admin	QA	M5	60000001	1	960000001	qa.admin.m5@sakura.cl	$2a$12$GwLDVg7d.1gUeYcaWOVF/.xHoBd6kqkQg7eeU0ck9UoXKyiHMfk/i
13	2	1	1	Recruiter	QA	M5	60000002	2	960000002	qa.rec.m5@sakura.cl	$2a$12$sCFeep7hnPTx.Ld1rIQa3OXfaOJdeZDaKzF2peHqsh.PX63lnShf2
14	4	1	1	Interviewer1	QA	M5	60000003	3	960000003	qa.int1.m5@sakura.cl	$2a$12$VH.SGNjaTIAvdIsQAeosY.UF4t2jxjDWGYgLxWC6WZwcsvTHkSMcS
15	4	1	1	Interviewer2	QA	M5	60000004	4	960000004	qa.int2.m5@sakura.cl	$2a$12$BOgNHqjQGgfqedNGAt0Vve7NIH1U0Vfw7D4iDpS.SqCqLwmL.aAES
\.


--
-- Data for Name: tbl_usuario_cita_entrevista; Type: TABLE DATA; Schema: public; Owner: elitsoft_admin
--

COPY public.tbl_usuario_cita_entrevista (usrce_cita_entrevista_id, usrce_usuario_id, usrce_tipo_entrevista_id) FROM stdin;
1	2	2
2	12	1
2	13	1
2	12	2
4	12	1
4	13	1
4	12	2
6	12	1
6	13	1
6	12	2
7	12	1
7	13	1
7	12	2
8	12	1
8	13	1
9	12	1
9	13	1
11	12	1
11	13	1
11	12	2
13	12	1
13	13	1
13	12	2
14	12	1
14	13	1
14	12	2
15	12	1
15	13	1
16	12	1
16	13	1
\.


--
-- Name: tbl_area_area_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_area_area_id_seq', 11, true);


--
-- Name: tbl_candidato_cand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_cand_id_seq', 12, true);


--
-- Name: tbl_candidato_cuestionario_cdcu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_cuestionario_cdcu_id_seq', 17, true);


--
-- Name: tbl_candidato_habilidad_cdhb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_habilidad_cdhb_id_seq', 23, true);


--
-- Name: tbl_candidato_idioma_cdio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_candidato_idioma_cdio_id_seq', 1, false);


--
-- Name: tbl_cargo_crgo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cargo_crgo_id_seq', 23, true);


--
-- Name: tbl_carrera_crra_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_carrera_crra_id_seq', 49, true);


--
-- Name: tbl_categoria_habilidad_cthb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_categoria_habilidad_cthb_id_seq', 14, true);


--
-- Name: tbl_cita_entrevista_ctev_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cita_entrevista_ctev_id_seq', 17, true);


--
-- Name: tbl_cliente_cli_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cliente_cli_id_seq', 8, true);


--
-- Name: tbl_comuna_com_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_comuna_com_id_seq', 348, true);


--
-- Name: tbl_cuestionario_cues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_cuestionario_cues_id_seq', 18, true);


--
-- Name: tbl_curso_curs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_curso_curs_id_seq', 10, true);


--
-- Name: tbl_direccion_candidato_drcd_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_direccion_candidato_drcd_id_seq', 1, true);


--
-- Name: tbl_disponibilidad_disp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_disponibilidad_disp_id_seq', 7, true);


--
-- Name: tbl_documento_reporte_candidato_drcp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_documento_reporte_candidato_drcp_id_seq', 36, true);


--
-- Name: tbl_empresa_emp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_empresa_emp_id_seq', 7, true);


--
-- Name: tbl_estado_cuestionario_candidato_escc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_cuestionario_candidato_escc_id_seq', 8, true);


--
-- Name: tbl_estado_entrevista_esev_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_entrevista_esev_id_seq', 8, true);


--
-- Name: tbl_estado_solicitud_candidato_essc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_solicitud_candidato_essc_id_seq', 8, true);


--
-- Name: tbl_estado_solicitud_essl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_solicitud_essl_id_seq', 8, true);


--
-- Name: tbl_estado_usuario_esusr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estado_usuario_esusr_id_seq', 6, true);


--
-- Name: tbl_estudio_candidato_etcd_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_estudio_candidato_etcd_id_seq', 4, true);


--
-- Name: tbl_evaluacion_entrevista_even_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_evaluacion_entrevista_even_id_seq', 10, true);


--
-- Name: tbl_experiencia_laboral_expl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_experiencia_laboral_expl_id_seq', 4, true);


--
-- Name: tbl_habilidad_hab_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_habilidad_hab_id_seq', 54, true);


--
-- Name: tbl_historial_solicitud_hsol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_historial_solicitud_hsol_id_seq', 45, true);


--
-- Name: tbl_idioma_idio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_idioma_idio_id_seq', 7, true);


--
-- Name: tbl_institucion_inst_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_institucion_inst_id_seq', 39, true);


--
-- Name: tbl_modalidad_mdld_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_modalidad_mdld_id_seq', 5, true);


--
-- Name: tbl_motivo_rechazo_mtrc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_motivo_rechazo_mtrc_id_seq', 14, true);


--
-- Name: tbl_nivel_educacional_nved_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nivel_educacional_nved_id_seq', 10, true);


--
-- Name: tbl_nivel_habilidad_nvhb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nivel_habilidad_nvhb_id_seq', 7, true);


--
-- Name: tbl_nivel_idioma_nvid_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nivel_idioma_nvid_id_seq', 10, true);


--
-- Name: tbl_nombre_resultado_nore_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_nombre_resultado_nore_id_seq', 7, true);


--
-- Name: tbl_notificacion_reclutamiento_ntfr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_notificacion_reclutamiento_ntfr_id_seq', 3, true);


--
-- Name: tbl_opcion_respuesta_opcr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_opcion_respuesta_opcr_id_seq', 30, true);


--
-- Name: tbl_pais_pais_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_pais_pais_id_seq', 7, true);


--
-- Name: tbl_password_reset_token_prst_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_password_reset_token_prst_id_seq', 1, false);


--
-- Name: tbl_permiso_per_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_permiso_per_id_seq', 22, true);


--
-- Name: tbl_plantilla_notificacion_plnt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_plantilla_notificacion_plnt_id_seq', 3, true);


--
-- Name: tbl_pregunta_cuestionario_prcu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_pregunta_cuestionario_prcu_id_seq', 27, true);


--
-- Name: tbl_pregunta_preg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_pregunta_preg_id_seq', 10, true);


--
-- Name: tbl_prioridad_solicitud_prsol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_prioridad_solicitud_prsol_id_seq', 5, true);


--
-- Name: tbl_region_reg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_region_reg_id_seq', 20, true);


--
-- Name: tbl_respuesta_pregunta_rspr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_respuesta_pregunta_rspr_id_seq', 16, true);


--
-- Name: tbl_rol_rol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_rol_rol_id_seq', 10, true);


--
-- Name: tbl_solicitud_candidato_slcd_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_candidato_slcd_id_seq', 9, true);


--
-- Name: tbl_solicitud_habilidad_solhb_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_habilidad_solhb_id_seq', 35, true);


--
-- Name: tbl_solicitud_sol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_solicitud_sol_id_seq', 16, true);


--
-- Name: tbl_tipo_contrato_tpct_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_tipo_contrato_tpct_id_seq', 7, true);


--
-- Name: tbl_tipo_entrevista_tpet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_tipo_entrevista_tpet_id_seq', 8, true);


--
-- Name: tbl_tipo_institucion_tint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_tipo_institucion_tint_id_seq', 11, true);


--
-- Name: tbl_usuario_usr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: elitsoft_admin
--

SELECT pg_catalog.setval('public.tbl_usuario_usr_id_seq', 15, true);


--
-- Name: tbl_area pk_tbl_area; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT pk_tbl_area PRIMARY KEY (area_id);


--
-- Name: tbl_candidato pk_tbl_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT pk_tbl_candidato PRIMARY KEY (cand_id);


--
-- Name: tbl_candidato_cuestionario pk_tbl_candidato_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT pk_tbl_candidato_cuestionario PRIMARY KEY (cdcu_id);


--
-- Name: tbl_candidato_habilidad pk_tbl_candidato_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT pk_tbl_candidato_habilidad PRIMARY KEY (cdhb_id);


--
-- Name: tbl_cargo pk_tbl_cargo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT pk_tbl_cargo PRIMARY KEY (crgo_id);


--
-- Name: tbl_carrera pk_tbl_carrera; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_carrera
    ADD CONSTRAINT pk_tbl_carrera PRIMARY KEY (crra_id);


--
-- Name: tbl_cita_entrevista pk_tbl_cita_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT pk_tbl_cita_entrevista PRIMARY KEY (ctev_id);


--
-- Name: tbl_cita_tipo_entrevista pk_tbl_cita_tipo_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_tipo_entrevista
    ADD CONSTRAINT pk_tbl_cita_tipo_entrevista PRIMARY KEY (cten_tipo_entrevista_id, cten_cita_entrevista_id);


--
-- Name: tbl_cliente pk_tbl_cliente; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT pk_tbl_cliente PRIMARY KEY (cli_id);


--
-- Name: tbl_comuna pk_tbl_comuna; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_comuna
    ADD CONSTRAINT pk_tbl_comuna PRIMARY KEY (com_id);


--
-- Name: tbl_cuestionario pk_tbl_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cuestionario
    ADD CONSTRAINT pk_tbl_cuestionario PRIMARY KEY (cues_id);


--
-- Name: tbl_curso pk_tbl_curso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT pk_tbl_curso PRIMARY KEY (curs_id);


--
-- Name: tbl_direccion_candidato pk_tbl_direccion_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT pk_tbl_direccion_candidato PRIMARY KEY (drcd_id);


--
-- Name: tbl_disponibilidad pk_tbl_disponibilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_disponibilidad
    ADD CONSTRAINT pk_tbl_disponibilidad PRIMARY KEY (disp_id);


--
-- Name: tbl_empresa pk_tbl_empresa; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT pk_tbl_empresa PRIMARY KEY (emp_id);


--
-- Name: tbl_estado_cuestionario_candidato pk_tbl_estado_cuestionario_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_cuestionario_candidato
    ADD CONSTRAINT pk_tbl_estado_cuestionario_candidato PRIMARY KEY (escc_id);


--
-- Name: tbl_estado_entrevista pk_tbl_estado_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_entrevista
    ADD CONSTRAINT pk_tbl_estado_entrevista PRIMARY KEY (esev_id);


--
-- Name: tbl_estado_solicitud pk_tbl_estado_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT pk_tbl_estado_solicitud PRIMARY KEY (essl_id);


--
-- Name: tbl_estado_solicitud_candidato pk_tbl_estado_solicitud_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud_candidato
    ADD CONSTRAINT pk_tbl_estado_solicitud_candidato PRIMARY KEY (essc_id);


--
-- Name: tbl_estado_usuario pk_tbl_estado_usuario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_usuario
    ADD CONSTRAINT pk_tbl_estado_usuario PRIMARY KEY (esusr_id);


--
-- Name: tbl_estudio_candidato pk_tbl_estudio_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT pk_tbl_estudio_candidato PRIMARY KEY (etcd_id);


--
-- Name: tbl_evaluacion_entrevista pk_tbl_evaluacion_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT pk_tbl_evaluacion_entrevista PRIMARY KEY (even_id);


--
-- Name: tbl_experiencia_laboral pk_tbl_experiencia_laboral; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT pk_tbl_experiencia_laboral PRIMARY KEY (expl_id);


--
-- Name: tbl_experiencia_laboral_habilidad pk_tbl_experiencia_laboral_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral_habilidad
    ADD CONSTRAINT pk_tbl_experiencia_laboral_habilidad PRIMARY KEY (exph_experiencia_laboral_id, exph_habilidad_id);


--
-- Name: tbl_habilidad pk_tbl_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT pk_tbl_habilidad PRIMARY KEY (hab_id);


--
-- Name: tbl_historial_solicitud pk_tbl_historial_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT pk_tbl_historial_solicitud PRIMARY KEY (hsol_id);


--
-- Name: tbl_institucion pk_tbl_institucion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_institucion
    ADD CONSTRAINT pk_tbl_institucion PRIMARY KEY (inst_id);


--
-- Name: tbl_modalidad pk_tbl_modalidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT pk_tbl_modalidad PRIMARY KEY (mdld_id);


--
-- Name: tbl_motivo_rechazo pk_tbl_motivo_rechazo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_motivo_rechazo
    ADD CONSTRAINT pk_tbl_motivo_rechazo PRIMARY KEY (mtrc_id);


--
-- Name: tbl_nivel_educacional pk_tbl_nivel_educacional; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_educacional
    ADD CONSTRAINT pk_tbl_nivel_educacional PRIMARY KEY (nved_id);


--
-- Name: tbl_nivel_habilidad pk_tbl_nivel_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad
    ADD CONSTRAINT pk_tbl_nivel_habilidad PRIMARY KEY (nvhb_id);


--
-- Name: tbl_nombre_resultado pk_tbl_nombre_resultado; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nombre_resultado
    ADD CONSTRAINT pk_tbl_nombre_resultado PRIMARY KEY (nore_id);


--
-- Name: tbl_opcion_respuesta pk_tbl_opcion_respuesta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_opcion_respuesta
    ADD CONSTRAINT pk_tbl_opcion_respuesta PRIMARY KEY (opcr_id);


--
-- Name: tbl_pais pk_tbl_pais; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pais
    ADD CONSTRAINT pk_tbl_pais PRIMARY KEY (pais_id);


--
-- Name: tbl_permiso pk_tbl_permiso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_permiso
    ADD CONSTRAINT pk_tbl_permiso PRIMARY KEY (per_id);


--
-- Name: tbl_pregunta pk_tbl_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT pk_tbl_pregunta PRIMARY KEY (preg_id);


--
-- Name: tbl_pregunta_cuestionario pk_tbl_pregunta_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT pk_tbl_pregunta_cuestionario PRIMARY KEY (prcu_id);


--
-- Name: tbl_prioridad_solicitud pk_tbl_prioridad_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad_solicitud
    ADD CONSTRAINT pk_tbl_prioridad_solicitud PRIMARY KEY (prsol_id);


--
-- Name: tbl_region pk_tbl_region; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT pk_tbl_region PRIMARY KEY (reg_id);


--
-- Name: tbl_respuesta_pregunta pk_tbl_respuesta_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT pk_tbl_respuesta_pregunta PRIMARY KEY (rspr_id);


--
-- Name: tbl_rol pk_tbl_rol; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol
    ADD CONSTRAINT pk_tbl_rol PRIMARY KEY (rol_id);


--
-- Name: tbl_rol_permiso pk_tbl_rol_permiso; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT pk_tbl_rol_permiso PRIMARY KEY (rlpm_rol_id, rlpm_permiso_id);


--
-- Name: tbl_solicitud pk_tbl_solicitud; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT pk_tbl_solicitud PRIMARY KEY (sol_id);


--
-- Name: tbl_solicitud_candidato pk_tbl_solicitud_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT pk_tbl_solicitud_candidato PRIMARY KEY (slcd_id);


--
-- Name: tbl_solicitud_habilidad pk_tbl_solicitud_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT pk_tbl_solicitud_habilidad PRIMARY KEY (solhb_id);


--
-- Name: tbl_tipo_contrato pk_tbl_tipo_contrato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_contrato
    ADD CONSTRAINT pk_tbl_tipo_contrato PRIMARY KEY (tpct_id);


--
-- Name: tbl_tipo_entrevista pk_tbl_tipo_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_entrevista
    ADD CONSTRAINT pk_tbl_tipo_entrevista PRIMARY KEY (tpet_id);


--
-- Name: tbl_tipo_institucion pk_tbl_tipo_institucion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_institucion
    ADD CONSTRAINT pk_tbl_tipo_institucion PRIMARY KEY (tint_id);


--
-- Name: tbl_usuario pk_tbl_usuario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT pk_tbl_usuario PRIMARY KEY (usr_id);


--
-- Name: tbl_usuario_cita_entrevista pk_tbl_usuario_cita_entrevista; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT pk_tbl_usuario_cita_entrevista PRIMARY KEY (usrce_cita_entrevista_id, usrce_usuario_id, usrce_tipo_entrevista_id);


--
-- Name: tbl_candidato_idioma tbl_candidato_idioma_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_idioma
    ADD CONSTRAINT tbl_candidato_idioma_pkey PRIMARY KEY (cdio_id);


--
-- Name: tbl_categoria_habilidad tbl_categoria_habilidad_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_categoria_habilidad
    ADD CONSTRAINT tbl_categoria_habilidad_pkey PRIMARY KEY (cthb_id);


--
-- Name: tbl_documento_reporte_candidato tbl_documento_reporte_candidato_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_documento_reporte_candidato
    ADD CONSTRAINT tbl_documento_reporte_candidato_pkey PRIMARY KEY (drcp_id);


--
-- Name: tbl_idioma tbl_idioma_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_idioma
    ADD CONSTRAINT tbl_idioma_pkey PRIMARY KEY (idio_id);


--
-- Name: tbl_nivel_idioma tbl_nivel_idioma_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_idioma
    ADD CONSTRAINT tbl_nivel_idioma_pkey PRIMARY KEY (nvid_id);


--
-- Name: tbl_notificacion_reclutamiento tbl_notificacion_reclutamiento_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_notificacion_reclutamiento
    ADD CONSTRAINT tbl_notificacion_reclutamiento_pkey PRIMARY KEY (ntfr_id);


--
-- Name: tbl_password_reset_token tbl_password_reset_token_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_password_reset_token
    ADD CONSTRAINT tbl_password_reset_token_pkey PRIMARY KEY (prst_id);


--
-- Name: tbl_plantilla_notificacion tbl_plantilla_notificacion_pkey; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_plantilla_notificacion
    ADD CONSTRAINT tbl_plantilla_notificacion_pkey PRIMARY KEY (plnt_id);


--
-- Name: tbl_area uq_tbl_area_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_area
    ADD CONSTRAINT uq_tbl_area_nombre UNIQUE (area_nombre);


--
-- Name: tbl_candidato_cuestionario uq_tbl_candidato_cuestionario_candidato_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT uq_tbl_candidato_cuestionario_candidato_cuestionario UNIQUE (cdcu_candidato_id, cdcu_cuestionario_id);


--
-- Name: tbl_candidato uq_tbl_candidato_email; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT uq_tbl_candidato_email UNIQUE (cand_email);


--
-- Name: tbl_candidato_habilidad uq_tbl_candidato_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT uq_tbl_candidato_habilidad UNIQUE (cdhb_candidato_id, cdhb_habilidad_id);


--
-- Name: tbl_candidato_habilidad uq_tbl_candidato_habilidad_candidato_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT uq_tbl_candidato_habilidad_candidato_habilidad UNIQUE (cdhb_candidato_id, cdhb_habilidad_id);


--
-- Name: tbl_candidato_idioma uq_tbl_candidato_idioma; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_idioma
    ADD CONSTRAINT uq_tbl_candidato_idioma UNIQUE (cdio_candidato_id, cdio_idioma_id);


--
-- Name: tbl_candidato uq_tbl_candidato_rut; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT uq_tbl_candidato_rut UNIQUE (cand_rut_sin_dv, cand_dv);


--
-- Name: tbl_cargo uq_tbl_cargo_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cargo
    ADD CONSTRAINT uq_tbl_cargo_nombre UNIQUE (crgo_nombre);


--
-- Name: tbl_carrera uq_tbl_carrera_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_carrera
    ADD CONSTRAINT uq_tbl_carrera_nombre UNIQUE (crra_nombre);


--
-- Name: tbl_categoria_habilidad uq_tbl_categoria_habilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_categoria_habilidad
    ADD CONSTRAINT uq_tbl_categoria_habilidad_nombre UNIQUE (cthb_nombre);


--
-- Name: tbl_cita_entrevista uq_tbl_cita_entrevista_agenda; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT uq_tbl_cita_entrevista_agenda UNIQUE (ctev_solicitud_candidato_id, ctev_tipo_entrevista_id, ctev_fecha_hora_inicio);


--
-- Name: tbl_cliente uq_tbl_cliente_email; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT uq_tbl_cliente_email UNIQUE (cli_email);


--
-- Name: tbl_cliente uq_tbl_cliente_email2; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT uq_tbl_cliente_email2 UNIQUE (cli_email2);


--
-- Name: tbl_comuna uq_tbl_comuna_comuna_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_comuna
    ADD CONSTRAINT uq_tbl_comuna_comuna_nombre UNIQUE (com_region_id, com_nombre);


--
-- Name: tbl_cuestionario uq_tbl_cuestionario_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cuestionario
    ADD CONSTRAINT uq_tbl_cuestionario_nombre UNIQUE (cues_nombre);


--
-- Name: tbl_curso uq_tbl_curso_candidato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT uq_tbl_curso_candidato_nombre UNIQUE (curs_candidato_id, curs_nombre_curso);


--
-- Name: tbl_direccion_candidato uq_tbl_direccion_candidato_direccion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT uq_tbl_direccion_candidato_direccion UNIQUE (drcd_candidato_id, drcd_comuna_id, drcd_calle, drcd_numero, drcd_dpto_oficina);


--
-- Name: tbl_disponibilidad uq_tbl_disponibilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_disponibilidad
    ADD CONSTRAINT uq_tbl_disponibilidad_nombre UNIQUE (disp_nombre);


--
-- Name: tbl_empresa uq_tbl_empresa_identificacion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT uq_tbl_empresa_identificacion UNIQUE (emp_identificacion);


--
-- Name: tbl_empresa uq_tbl_empresa_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_empresa
    ADD CONSTRAINT uq_tbl_empresa_nombre UNIQUE (emp_nombre);


--
-- Name: tbl_estado_cuestionario_candidato uq_tbl_estado_cuestionario_candidato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_cuestionario_candidato
    ADD CONSTRAINT uq_tbl_estado_cuestionario_candidato_nombre UNIQUE (escc_nombre);


--
-- Name: tbl_estado_entrevista uq_tbl_estado_entrevista_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_entrevista
    ADD CONSTRAINT uq_tbl_estado_entrevista_nombre UNIQUE (esev_nombre);


--
-- Name: tbl_estado_solicitud_candidato uq_tbl_estado_solicitud_candidato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud_candidato
    ADD CONSTRAINT uq_tbl_estado_solicitud_candidato_nombre UNIQUE (essc_nombre);


--
-- Name: tbl_estado_solicitud uq_tbl_estado_solicitud_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_solicitud
    ADD CONSTRAINT uq_tbl_estado_solicitud_nombre UNIQUE (essl_nombre);


--
-- Name: tbl_estado_usuario uq_tbl_estado_usuario_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estado_usuario
    ADD CONSTRAINT uq_tbl_estado_usuario_nombre UNIQUE (esusr_nombre);


--
-- Name: tbl_estudio_candidato uq_tbl_estudio_candidato_registro; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT uq_tbl_estudio_candidato_registro UNIQUE (etcd_candidato_id, etcd_institucion_id, etcd_carrera_id, etcd_fecha_inicio);


--
-- Name: tbl_experiencia_laboral uq_tbl_experiencia_laboral_registro; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT uq_tbl_experiencia_laboral_registro UNIQUE (expl_candidato_id, expl_empresa_id, expl_cargo_id, expl_fecha_inicio);


--
-- Name: tbl_habilidad uq_tbl_habilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT uq_tbl_habilidad_nombre UNIQUE (hab_nombre);


--
-- Name: tbl_idioma uq_tbl_idioma_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_idioma
    ADD CONSTRAINT uq_tbl_idioma_nombre UNIQUE (idio_nombre);


--
-- Name: tbl_institucion uq_tbl_institucion_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_institucion
    ADD CONSTRAINT uq_tbl_institucion_nombre UNIQUE (inst_nombre);


--
-- Name: tbl_modalidad uq_tbl_modalidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_modalidad
    ADD CONSTRAINT uq_tbl_modalidad_nombre UNIQUE (mdld_nombre);


--
-- Name: tbl_motivo_rechazo uq_tbl_motivo_rechazo_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_motivo_rechazo
    ADD CONSTRAINT uq_tbl_motivo_rechazo_nombre UNIQUE (mtrc_nombre);


--
-- Name: tbl_nivel_educacional uq_tbl_nivel_educacional_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_educacional
    ADD CONSTRAINT uq_tbl_nivel_educacional_nombre UNIQUE (nved_nombre);


--
-- Name: tbl_nivel_habilidad uq_tbl_nivel_habilidad_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_habilidad
    ADD CONSTRAINT uq_tbl_nivel_habilidad_nombre UNIQUE (nvhb_nombre);


--
-- Name: tbl_nivel_idioma uq_tbl_nivel_idioma_codigo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_idioma
    ADD CONSTRAINT uq_tbl_nivel_idioma_codigo UNIQUE (nvid_codigo);


--
-- Name: tbl_nivel_idioma uq_tbl_nivel_idioma_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nivel_idioma
    ADD CONSTRAINT uq_tbl_nivel_idioma_nombre UNIQUE (nvid_nombre);


--
-- Name: tbl_nombre_resultado uq_tbl_nombre_resultado_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_nombre_resultado
    ADD CONSTRAINT uq_tbl_nombre_resultado_nombre UNIQUE (nore_nombre);


--
-- Name: tbl_opcion_respuesta uq_tbl_opcion_respuesta_pregunta_opcion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_opcion_respuesta
    ADD CONSTRAINT uq_tbl_opcion_respuesta_pregunta_opcion UNIQUE (opcr_pregunta_id, opcr_texto_opcion);


--
-- Name: tbl_pais uq_tbl_pais_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pais
    ADD CONSTRAINT uq_tbl_pais_nombre UNIQUE (pais_nombre);


--
-- Name: tbl_password_reset_token uq_tbl_password_reset_token_hash; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_password_reset_token
    ADD CONSTRAINT uq_tbl_password_reset_token_hash UNIQUE (prst_token_hash);


--
-- Name: tbl_permiso uq_tbl_permiso_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_permiso
    ADD CONSTRAINT uq_tbl_permiso_nombre UNIQUE (per_nombre);


--
-- Name: tbl_plantilla_notificacion uq_tbl_plantilla_notificacion_tipo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_plantilla_notificacion
    ADD CONSTRAINT uq_tbl_plantilla_notificacion_tipo UNIQUE (plnt_tipo);


--
-- Name: tbl_pregunta_cuestionario uq_tbl_pregunta_cuestionario; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT uq_tbl_pregunta_cuestionario UNIQUE (prcu_cuestionario_id, prcu_pregunta_id);


--
-- Name: tbl_pregunta uq_tbl_pregunta_texto_habilidad_nivel; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT uq_tbl_pregunta_texto_habilidad_nivel UNIQUE (preg_texto_pregunta, preg_habilidad_id, preg_nivel_habilidad_id);


--
-- Name: tbl_prioridad_solicitud uq_tbl_prioridad_solicitud_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_prioridad_solicitud
    ADD CONSTRAINT uq_tbl_prioridad_solicitud_nombre UNIQUE (prsol_nombre);


--
-- Name: tbl_region uq_tbl_region_pais_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT uq_tbl_region_pais_nombre UNIQUE (reg_pais_id, reg_nombre);


--
-- Name: tbl_respuesta_pregunta uq_tbl_respuesta_asignacion_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT uq_tbl_respuesta_asignacion_pregunta UNIQUE (rspr_candidato_cuestionario_id, rspr_pregunta_cuestionario_id);


--
-- Name: tbl_respuesta_pregunta uq_tbl_respuesta_pregunta_candidato_pregunta; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT uq_tbl_respuesta_pregunta_candidato_pregunta UNIQUE (rspr_candidato_cuestionario_id, rspr_pregunta_cuestionario_id);


--
-- Name: tbl_rol uq_tbl_rol_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol
    ADD CONSTRAINT uq_tbl_rol_nombre UNIQUE (rol_nombre);


--
-- Name: tbl_solicitud_candidato uq_tbl_solicitud_candidato_postulacion; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT uq_tbl_solicitud_candidato_postulacion UNIQUE (slcd_candidato_id, slcd_solicitud_id);


--
-- Name: tbl_solicitud_candidato uq_tbl_solicitud_candidato_solicitud_candidato; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT uq_tbl_solicitud_candidato_solicitud_candidato UNIQUE (slcd_solicitud_id, slcd_candidato_id);


--
-- Name: tbl_solicitud uq_tbl_solicitud_codigo; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT uq_tbl_solicitud_codigo UNIQUE (sol_codigo);


--
-- Name: tbl_solicitud_habilidad uq_tbl_solicitud_habilidad; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT uq_tbl_solicitud_habilidad UNIQUE (solhb_solicitud_id, solhb_habilidad_id);


--
-- Name: tbl_tipo_contrato uq_tbl_tipo_contrato_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_contrato
    ADD CONSTRAINT uq_tbl_tipo_contrato_nombre UNIQUE (tpct_nombre);


--
-- Name: tbl_tipo_entrevista uq_tbl_tipo_entrevista_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_entrevista
    ADD CONSTRAINT uq_tbl_tipo_entrevista_nombre UNIQUE (tpet_nombre);


--
-- Name: tbl_tipo_institucion uq_tbl_tipo_institucion_nombre; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_tipo_institucion
    ADD CONSTRAINT uq_tbl_tipo_institucion_nombre UNIQUE (tint_tipo_institucion);


--
-- Name: tbl_usuario uq_tbl_usuario_email; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT uq_tbl_usuario_email UNIQUE (usr_email);


--
-- Name: tbl_usuario uq_tbl_usuario_rut; Type: CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT uq_tbl_usuario_rut UNIQUE (usr_rut_sin_dv, usr_dv);


--
-- Name: idx_m5_cita_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_m5_cita_estado ON public.tbl_cita_entrevista USING btree (ctev_estado_entrevista_id);


--
-- Name: idx_m5_cita_fecha; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_m5_cita_fecha ON public.tbl_cita_entrevista USING btree (ctev_fecha_hora_inicio);


--
-- Name: idx_m5_cita_slcd; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_m5_cita_slcd ON public.tbl_cita_entrevista USING btree (ctev_solicitud_candidato_id);


--
-- Name: idx_m5_eval_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_m5_eval_cita ON public.tbl_evaluacion_entrevista USING btree (even_cita_entrevista_id);


--
-- Name: idx_m5_usuario_cita_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_m5_usuario_cita_tipo ON public.tbl_usuario_cita_entrevista USING btree (usrce_tipo_entrevista_id);


--
-- Name: idx_m5_usuario_cita_usuario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_m5_usuario_cita_usuario ON public.tbl_usuario_cita_entrevista USING btree (usrce_usuario_id);


--
-- Name: idx_tbl_area_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_area_nombre ON public.tbl_area USING btree (area_nombre);


--
-- Name: idx_tbl_candidato_apellidos; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_apellidos ON public.tbl_candidato USING btree (cand_apellido_paterno, cand_apellido_materno);


--
-- Name: idx_tbl_candidato_cuestionario_aprobado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_aprobado ON public.tbl_candidato_cuestionario USING btree (cdcu_aprobado);


--
-- Name: idx_tbl_candidato_cuestionario_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_candidato ON public.tbl_candidato_cuestionario USING btree (cdcu_candidato_id);


--
-- Name: idx_tbl_candidato_cuestionario_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_cuestionario ON public.tbl_candidato_cuestionario USING btree (cdcu_cuestionario_id);


--
-- Name: idx_tbl_candidato_cuestionario_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_estado ON public.tbl_candidato_cuestionario USING btree (cdcu_estado_cuestionario_candidato_id);


--
-- Name: idx_tbl_candidato_cuestionario_fecha_asignacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_cuestionario_fecha_asignacion ON public.tbl_candidato_cuestionario USING btree (cdcu_fecha_asignacion);


--
-- Name: idx_tbl_candidato_disponibilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_disponibilidad ON public.tbl_candidato USING btree (cand_disponibilidad_id);


--
-- Name: idx_tbl_candidato_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_email ON public.tbl_candidato USING btree (cand_email);


--
-- Name: idx_tbl_candidato_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_fecha_creacion ON public.tbl_candidato USING btree (cand_fecha_creacion);


--
-- Name: idx_tbl_candidato_habilidad_anios; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_anios ON public.tbl_candidato_habilidad USING btree (cdhb_anios_experiencia);


--
-- Name: idx_tbl_candidato_habilidad_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_candidato ON public.tbl_candidato_habilidad USING btree (cdhb_candidato_id);


--
-- Name: idx_tbl_candidato_habilidad_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_habilidad ON public.tbl_candidato_habilidad USING btree (cdhb_habilidad_id);


--
-- Name: idx_tbl_candidato_habilidad_nivel; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_habilidad_nivel ON public.tbl_candidato_habilidad USING btree (cdhb_nivel_habilidad_id);


--
-- Name: idx_tbl_candidato_titulo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_candidato_titulo ON public.tbl_candidato USING btree (cand_titulo);


--
-- Name: idx_tbl_cargo_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cargo_nombre ON public.tbl_cargo USING btree (crgo_nombre);


--
-- Name: idx_tbl_carrera_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_carrera_nombre ON public.tbl_carrera USING btree (crra_nombre);


--
-- Name: idx_tbl_cita_entrevista_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_estado ON public.tbl_cita_entrevista USING btree (ctev_estado_entrevista_id);


--
-- Name: idx_tbl_cita_entrevista_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_fecha_creacion ON public.tbl_cita_entrevista USING btree (ctev_fecha_creacion);


--
-- Name: idx_tbl_cita_entrevista_fecha_fin; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_fecha_fin ON public.tbl_cita_entrevista USING btree (ctev_fecha_hora_fin);


--
-- Name: idx_tbl_cita_entrevista_fecha_inicio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_fecha_inicio ON public.tbl_cita_entrevista USING btree (ctev_fecha_hora_inicio);


--
-- Name: idx_tbl_cita_entrevista_solicitud_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_solicitud_candidato ON public.tbl_cita_entrevista USING btree (ctev_solicitud_candidato_id);


--
-- Name: idx_tbl_cita_entrevista_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_entrevista_tipo ON public.tbl_cita_entrevista USING btree (ctev_tipo_entrevista_id);


--
-- Name: idx_tbl_cita_tipo_entrevista_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_tipo_entrevista_cita ON public.tbl_cita_tipo_entrevista USING btree (cten_cita_entrevista_id);


--
-- Name: idx_tbl_cita_tipo_entrevista_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cita_tipo_entrevista_tipo ON public.tbl_cita_tipo_entrevista USING btree (cten_tipo_entrevista_id);


--
-- Name: idx_tbl_cliente_area_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_area_empresa ON public.tbl_cliente USING btree (cli_area_empresa_id);


--
-- Name: idx_tbl_cliente_cargo_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_cargo_empresa ON public.tbl_cliente USING btree (cli_cargo_empresa_id);


--
-- Name: idx_tbl_cliente_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_email ON public.tbl_cliente USING btree (cli_email);


--
-- Name: idx_tbl_cliente_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_empresa ON public.tbl_cliente USING btree (cli_empresa_id);


--
-- Name: idx_tbl_cliente_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cliente_nombre ON public.tbl_cliente USING btree (cli_nombre);


--
-- Name: idx_tbl_comuna_ciudad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_comuna_ciudad ON public.tbl_comuna USING btree (com_region_id);


--
-- Name: idx_tbl_comuna_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_comuna_nombre ON public.tbl_comuna USING btree (com_nombre);


--
-- Name: idx_tbl_cuestionario_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cuestionario_nombre ON public.tbl_cuestionario USING btree (cues_nombre);


--
-- Name: idx_tbl_cuestionario_porcentaje_aprobacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cuestionario_porcentaje_aprobacion ON public.tbl_cuestionario USING btree (cues_porcentaje_aprobacion);


--
-- Name: idx_tbl_cuestionario_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_cuestionario_solicitud ON public.tbl_cuestionario USING btree (cues_solicitud_id);


--
-- Name: idx_tbl_curso_anio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_anio ON public.tbl_curso USING btree (curs_anio_curso);


--
-- Name: idx_tbl_curso_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_candidato ON public.tbl_curso USING btree (curs_candidato_id);


--
-- Name: idx_tbl_curso_institucion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_institucion ON public.tbl_curso USING btree (curs_institucion_id);


--
-- Name: idx_tbl_curso_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_curso_nombre ON public.tbl_curso USING btree (curs_nombre_curso);


--
-- Name: idx_tbl_direccion_candidato_calle; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_direccion_candidato_calle ON public.tbl_direccion_candidato USING btree (drcd_calle);


--
-- Name: idx_tbl_direccion_candidato_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_direccion_candidato_candidato ON public.tbl_direccion_candidato USING btree (drcd_candidato_id);


--
-- Name: idx_tbl_direccion_candidato_comuna; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_direccion_candidato_comuna ON public.tbl_direccion_candidato USING btree (drcd_comuna_id);


--
-- Name: idx_tbl_disponibilidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_disponibilidad_nombre ON public.tbl_disponibilidad USING btree (disp_nombre);


--
-- Name: idx_tbl_empresa_identificacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_empresa_identificacion ON public.tbl_empresa USING btree (emp_identificacion);


--
-- Name: idx_tbl_empresa_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_empresa_nombre ON public.tbl_empresa USING btree (emp_nombre);


--
-- Name: idx_tbl_estado_cuestionario_candidato_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_cuestionario_candidato_nombre ON public.tbl_estado_cuestionario_candidato USING btree (escc_nombre);


--
-- Name: idx_tbl_estado_entrevista_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_entrevista_nombre ON public.tbl_estado_entrevista USING btree (esev_nombre);


--
-- Name: idx_tbl_estado_solicitud_candidato_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_solicitud_candidato_nombre ON public.tbl_estado_solicitud_candidato USING btree (essc_nombre);


--
-- Name: idx_tbl_estado_solicitud_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_solicitud_nombre ON public.tbl_estado_solicitud USING btree (essl_nombre);


--
-- Name: idx_tbl_estado_usuario_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estado_usuario_nombre ON public.tbl_estado_usuario USING btree (esusr_nombre);


--
-- Name: idx_tbl_estudio_candidato_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_candidato ON public.tbl_estudio_candidato USING btree (etcd_candidato_id);


--
-- Name: idx_tbl_estudio_candidato_carrera; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_carrera ON public.tbl_estudio_candidato USING btree (etcd_carrera_id);


--
-- Name: idx_tbl_estudio_candidato_fecha_fin; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_fecha_fin ON public.tbl_estudio_candidato USING btree (etcd_fecha_fin);


--
-- Name: idx_tbl_estudio_candidato_fecha_inicio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_fecha_inicio ON public.tbl_estudio_candidato USING btree (etcd_fecha_inicio);


--
-- Name: idx_tbl_estudio_candidato_institucion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_institucion ON public.tbl_estudio_candidato USING btree (etcd_institucion_id);


--
-- Name: idx_tbl_estudio_candidato_nivel_educacional; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_estudio_candidato_nivel_educacional ON public.tbl_estudio_candidato USING btree (etcd_nivel_educacional_id);


--
-- Name: idx_tbl_evaluacion_entrevista_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_evaluacion_entrevista_cita ON public.tbl_evaluacion_entrevista USING btree (even_cita_entrevista_id);


--
-- Name: idx_tbl_evaluacion_entrevista_resultado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_evaluacion_entrevista_resultado ON public.tbl_evaluacion_entrevista USING btree (even_nombre_resultado_id);


--
-- Name: idx_tbl_experiencia_laboral_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_candidato ON public.tbl_experiencia_laboral USING btree (expl_candidato_id);


--
-- Name: idx_tbl_experiencia_laboral_cargo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_cargo ON public.tbl_experiencia_laboral USING btree (expl_cargo_id);


--
-- Name: idx_tbl_experiencia_laboral_empresa; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_empresa ON public.tbl_experiencia_laboral USING btree (expl_empresa_id);


--
-- Name: idx_tbl_experiencia_laboral_fecha_fin; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_fecha_fin ON public.tbl_experiencia_laboral USING btree (expl_fecha_fin);


--
-- Name: idx_tbl_experiencia_laboral_fecha_inicio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_experiencia_laboral_fecha_inicio ON public.tbl_experiencia_laboral USING btree (expl_fecha_inicio);


--
-- Name: idx_tbl_expl_habilidad_experiencia; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_expl_habilidad_experiencia ON public.tbl_experiencia_laboral_habilidad USING btree (exph_experiencia_laboral_id);


--
-- Name: idx_tbl_expl_habilidad_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_expl_habilidad_habilidad ON public.tbl_experiencia_laboral_habilidad USING btree (exph_habilidad_id);


--
-- Name: idx_tbl_habilidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_habilidad_nombre ON public.tbl_habilidad USING btree (hab_nombre);


--
-- Name: idx_tbl_historial_solicitud_estado_actual; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_estado_actual ON public.tbl_historial_solicitud USING btree (hsol_estado_actual_id);


--
-- Name: idx_tbl_historial_solicitud_estado_anterior; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_estado_anterior ON public.tbl_historial_solicitud USING btree (hsol_estado_anterior_id);


--
-- Name: idx_tbl_historial_solicitud_fecha_cambio; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_fecha_cambio ON public.tbl_historial_solicitud USING btree (hsol_fecha_cambio);


--
-- Name: idx_tbl_historial_solicitud_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_solicitud ON public.tbl_historial_solicitud USING btree (hsol_solicitud_id);


--
-- Name: idx_tbl_historial_solicitud_usuario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_historial_solicitud_usuario ON public.tbl_historial_solicitud USING btree (hsol_usuario_id);


--
-- Name: idx_tbl_institucion_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_institucion_nombre ON public.tbl_institucion USING btree (inst_nombre);


--
-- Name: idx_tbl_institucion_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_institucion_tipo ON public.tbl_institucion USING btree (inst_tipo_institucion_id);


--
-- Name: idx_tbl_modalidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_modalidad_nombre ON public.tbl_modalidad USING btree (mdld_nombre);


--
-- Name: idx_tbl_motivo_rechazo_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_motivo_rechazo_nombre ON public.tbl_motivo_rechazo USING btree (mtrc_nombre);


--
-- Name: idx_tbl_nivel_educacional_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nivel_educacional_nombre ON public.tbl_nivel_educacional USING btree (nved_nombre);


--
-- Name: idx_tbl_nivel_habilidad_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nivel_habilidad_nombre ON public.tbl_nivel_habilidad USING btree (nvhb_nombre);


--
-- Name: idx_tbl_nivel_habilidad_puntaje; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nivel_habilidad_puntaje ON public.tbl_nivel_habilidad USING btree (nvhb_puntaje_base);


--
-- Name: idx_tbl_nombre_resultado_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_nombre_resultado_nombre ON public.tbl_nombre_resultado USING btree (nore_nombre);


--
-- Name: idx_tbl_opcion_respuesta_correcta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_opcion_respuesta_correcta ON public.tbl_opcion_respuesta USING btree (opcr_es_correcta);


--
-- Name: idx_tbl_opcion_respuesta_pregunta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_opcion_respuesta_pregunta ON public.tbl_opcion_respuesta USING btree (opcr_pregunta_id);


--
-- Name: idx_tbl_pais_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pais_nombre ON public.tbl_pais USING btree (pais_nombre);


--
-- Name: idx_tbl_permiso_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_permiso_nombre ON public.tbl_permiso USING btree (per_nombre);


--
-- Name: idx_tbl_pregunta_cuestionario_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_cuestionario_cuestionario ON public.tbl_pregunta_cuestionario USING btree (prcu_cuestionario_id);


--
-- Name: idx_tbl_pregunta_cuestionario_pregunta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_cuestionario_pregunta ON public.tbl_pregunta_cuestionario USING btree (prcu_pregunta_id);


--
-- Name: idx_tbl_pregunta_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_fecha_creacion ON public.tbl_pregunta USING btree (preg_fecha_creacion);


--
-- Name: idx_tbl_pregunta_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_habilidad ON public.tbl_pregunta USING btree (preg_habilidad_id);


--
-- Name: idx_tbl_pregunta_nivel_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_pregunta_nivel_habilidad ON public.tbl_pregunta USING btree (preg_nivel_habilidad_id);


--
-- Name: idx_tbl_prioridad_solicitud_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_prioridad_solicitud_nombre ON public.tbl_prioridad_solicitud USING btree (prsol_nombre);


--
-- Name: idx_tbl_region_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_region_nombre ON public.tbl_region USING btree (reg_nombre);


--
-- Name: idx_tbl_region_pais; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_region_pais ON public.tbl_region USING btree (reg_pais_id);


--
-- Name: idx_tbl_respuesta_asignacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_asignacion ON public.tbl_respuesta_pregunta USING btree (rspr_candidato_cuestionario_id);


--
-- Name: idx_tbl_respuesta_pregunta_candidato_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_candidato_cuestionario ON public.tbl_respuesta_pregunta USING btree (rspr_candidato_cuestionario_id);


--
-- Name: idx_tbl_respuesta_pregunta_correcta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_correcta ON public.tbl_respuesta_pregunta USING btree (rspr_es_correcta);


--
-- Name: idx_tbl_respuesta_pregunta_opcion_respuesta; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_opcion_respuesta ON public.tbl_respuesta_pregunta USING btree (rspr_opcion_respuesta_id);


--
-- Name: idx_tbl_respuesta_pregunta_pregunta_cuestionario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_respuesta_pregunta_pregunta_cuestionario ON public.tbl_respuesta_pregunta USING btree (rspr_pregunta_cuestionario_id);


--
-- Name: idx_tbl_rol_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_nombre ON public.tbl_rol USING btree (rol_nombre);


--
-- Name: idx_tbl_rol_permiso_permiso; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_permiso_permiso ON public.tbl_rol_permiso USING btree (rlpm_permiso_id);


--
-- Name: idx_tbl_rol_permiso_rol; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_rol_permiso_rol ON public.tbl_rol_permiso USING btree (rlpm_rol_id);


--
-- Name: idx_tbl_solicitud_candidato_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_candidato ON public.tbl_solicitud_candidato USING btree (slcd_candidato_id);


--
-- Name: idx_tbl_solicitud_candidato_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_estado ON public.tbl_solicitud_candidato USING btree (slcd_estado_solicitud_candidato_id);


--
-- Name: idx_tbl_solicitud_candidato_fecha_postulacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_fecha_postulacion ON public.tbl_solicitud_candidato USING btree (slcd_fecha_postulacion);


--
-- Name: idx_tbl_solicitud_candidato_motivo_rechazo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_motivo_rechazo ON public.tbl_solicitud_candidato USING btree (slcd_motivo_rechazo_id);


--
-- Name: idx_tbl_solicitud_candidato_puntaje; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_puntaje ON public.tbl_solicitud_candidato USING btree (slcd_puntaje_compatibilidad);


--
-- Name: idx_tbl_solicitud_candidato_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_candidato_solicitud ON public.tbl_solicitud_candidato USING btree (slcd_solicitud_id);


--
-- Name: idx_tbl_solicitud_cargo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_cargo ON public.tbl_solicitud USING btree (sol_cargo_id);


--
-- Name: idx_tbl_solicitud_cliente; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_cliente ON public.tbl_solicitud USING btree (sol_cliente_id);


--
-- Name: idx_tbl_solicitud_codigo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_codigo ON public.tbl_solicitud USING btree (sol_codigo);


--
-- Name: idx_tbl_solicitud_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_estado ON public.tbl_solicitud USING btree (sol_estado_solicitud_id);


--
-- Name: idx_tbl_solicitud_fecha_cierre_busqueda; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_fecha_cierre_busqueda ON public.tbl_solicitud USING btree (sol_fecha_cierre_busqueda);


--
-- Name: idx_tbl_solicitud_fecha_creacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_fecha_creacion ON public.tbl_solicitud USING btree (sol_fecha_creacion);


--
-- Name: idx_tbl_solicitud_fecha_inicio_busqueda; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_fecha_inicio_busqueda ON public.tbl_solicitud USING btree (sol_fecha_inicio_busqueda);


--
-- Name: idx_tbl_solicitud_habilidad_excluyente; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_excluyente ON public.tbl_solicitud_habilidad USING btree (solhb_es_excluyente);


--
-- Name: idx_tbl_solicitud_habilidad_habilidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_habilidad ON public.tbl_solicitud_habilidad USING btree (solhb_habilidad_id);


--
-- Name: idx_tbl_solicitud_habilidad_nivel; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_nivel ON public.tbl_solicitud_habilidad USING btree (solhb_nivel_habilidad_id);


--
-- Name: idx_tbl_solicitud_habilidad_solicitud; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_habilidad_solicitud ON public.tbl_solicitud_habilidad USING btree (solhb_solicitud_id);


--
-- Name: idx_tbl_solicitud_modalidad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_modalidad ON public.tbl_solicitud USING btree (sol_modalidad_id);


--
-- Name: idx_tbl_solicitud_prioridad; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_prioridad ON public.tbl_solicitud USING btree (sol_prioridad_id);


--
-- Name: idx_tbl_solicitud_tipo_contrato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_tipo_contrato ON public.tbl_solicitud USING btree (sol_tipo_contrato_id);


--
-- Name: idx_tbl_solicitud_usuario_asignado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_usuario_asignado ON public.tbl_solicitud USING btree (sol_usuario_asignado_id);


--
-- Name: idx_tbl_solicitud_usuario_creador; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_solicitud_usuario_creador ON public.tbl_solicitud USING btree (sol_usuario_creador_id);


--
-- Name: idx_tbl_tipo_contrato_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_tipo_contrato_nombre ON public.tbl_tipo_contrato USING btree (tpct_nombre);


--
-- Name: idx_tbl_tipo_entrevista_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_tipo_entrevista_nombre ON public.tbl_tipo_entrevista USING btree (tpet_nombre);


--
-- Name: idx_tbl_tipo_institucion_nombre; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_tipo_institucion_nombre ON public.tbl_tipo_institucion USING btree (tint_tipo_institucion);


--
-- Name: idx_tbl_usuario_apellidos; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_apellidos ON public.tbl_usuario USING btree (usr_apellido_paterno, usr_apellido_materno);


--
-- Name: idx_tbl_usuario_area; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_area ON public.tbl_usuario USING btree (usr_area_id);


--
-- Name: idx_tbl_usuario_cita_entrevista_cita; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_cita_entrevista_cita ON public.tbl_usuario_cita_entrevista USING btree (usrce_cita_entrevista_id);


--
-- Name: idx_tbl_usuario_cita_entrevista_usuario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_cita_entrevista_usuario ON public.tbl_usuario_cita_entrevista USING btree (usrce_usuario_id);


--
-- Name: idx_tbl_usuario_email; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_email ON public.tbl_usuario USING btree (usr_email);


--
-- Name: idx_tbl_usuario_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_estado ON public.tbl_usuario USING btree (usr_estado_usuario_id);


--
-- Name: idx_tbl_usuario_nombre_completo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_nombre_completo ON public.tbl_usuario USING btree (usr_nombres, usr_apellido_paterno, usr_apellido_materno);


--
-- Name: idx_tbl_usuario_rol; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX idx_tbl_usuario_rol ON public.tbl_usuario USING btree (usr_rol_id);


--
-- Name: ix_password_reset_expiracion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_password_reset_expiracion ON public.tbl_password_reset_token USING btree (prst_fecha_expiracion);


--
-- Name: ix_password_reset_usuario; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_password_reset_usuario ON public.tbl_password_reset_token USING btree (prst_usuario_id);


--
-- Name: ix_tbl_candidato_email_lower; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_candidato_email_lower ON public.tbl_candidato USING btree (lower((cand_email)::text));


--
-- Name: ix_tbl_candidato_idioma_candidato; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_candidato_idioma_candidato ON public.tbl_candidato_idioma USING btree (cdio_candidato_id);


--
-- Name: ix_tbl_candidato_idioma_nivel; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_candidato_idioma_nivel ON public.tbl_candidato_idioma USING btree (cdio_nivel_idioma_id);


--
-- Name: ix_tbl_documento_reporte_fecha; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_documento_reporte_fecha ON public.tbl_documento_reporte_candidato USING btree (drcp_fecha_generacion DESC);


--
-- Name: ix_tbl_documento_reporte_postulacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_documento_reporte_postulacion ON public.tbl_documento_reporte_candidato USING btree (drcp_solicitud_candidato_id);


--
-- Name: ix_tbl_habilidad_categoria; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_habilidad_categoria ON public.tbl_habilidad USING btree (hab_categoria_habilidad_id);


--
-- Name: ix_tbl_nivel_idioma_activo_orden; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_nivel_idioma_activo_orden ON public.tbl_nivel_idioma USING btree (nvid_activo, nvid_orden);


--
-- Name: ix_tbl_nivel_idioma_grupo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_nivel_idioma_grupo ON public.tbl_nivel_idioma USING btree (nvid_grupo);


--
-- Name: ix_tbl_notificacion_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_notificacion_estado ON public.tbl_notificacion_reclutamiento USING btree (ntfr_estado);


--
-- Name: ix_tbl_notificacion_fecha; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_notificacion_fecha ON public.tbl_notificacion_reclutamiento USING btree (ntfr_fecha_creacion DESC);


--
-- Name: ix_tbl_notificacion_postulacion; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_notificacion_postulacion ON public.tbl_notificacion_reclutamiento USING btree (ntfr_solicitud_candidato_id);


--
-- Name: ix_tbl_solicitud_candidato_solicitud_estado; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE INDEX ix_tbl_solicitud_candidato_solicitud_estado ON public.tbl_solicitud_candidato USING btree (slcd_solicitud_id, slcd_estado_solicitud_candidato_id);


--
-- Name: uq_m5_evaluacion_cita_usuario_tipo; Type: INDEX; Schema: public; Owner: elitsoft_admin
--

CREATE UNIQUE INDEX uq_m5_evaluacion_cita_usuario_tipo ON public.tbl_evaluacion_entrevista USING btree (even_cita_entrevista_id, even_usuario_id, even_tipo_entrevista_id) WHERE ((even_usuario_id IS NOT NULL) AND (even_tipo_entrevista_id IS NOT NULL));


--
-- Name: tbl_candidato_cuestionario fk_tbl_candidato_cuestionario_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT fk_tbl_candidato_cuestionario_candidato FOREIGN KEY (cdcu_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_candidato_cuestionario fk_tbl_candidato_cuestionario_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT fk_tbl_candidato_cuestionario_cuestionario FOREIGN KEY (cdcu_cuestionario_id) REFERENCES public.tbl_cuestionario(cues_id);


--
-- Name: tbl_candidato_cuestionario fk_tbl_candidato_cuestionario_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_cuestionario
    ADD CONSTRAINT fk_tbl_candidato_cuestionario_estado FOREIGN KEY (cdcu_estado_cuestionario_candidato_id) REFERENCES public.tbl_estado_cuestionario_candidato(escc_id);


--
-- Name: tbl_candidato fk_tbl_candidato_disponibilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT fk_tbl_candidato_disponibilidad FOREIGN KEY (cand_disponibilidad_id) REFERENCES public.tbl_disponibilidad(disp_id);


--
-- Name: tbl_candidato_habilidad fk_tbl_candidato_habilidad_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT fk_tbl_candidato_habilidad_candidato FOREIGN KEY (cdhb_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_candidato_habilidad fk_tbl_candidato_habilidad_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT fk_tbl_candidato_habilidad_habilidad FOREIGN KEY (cdhb_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_candidato_habilidad fk_tbl_candidato_habilidad_nivel; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_habilidad
    ADD CONSTRAINT fk_tbl_candidato_habilidad_nivel FOREIGN KEY (cdhb_nivel_habilidad_id) REFERENCES public.tbl_nivel_habilidad(nvhb_id);


--
-- Name: tbl_candidato_idioma fk_tbl_candidato_idioma_nivel; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_idioma
    ADD CONSTRAINT fk_tbl_candidato_idioma_nivel FOREIGN KEY (cdio_nivel_idioma_id) REFERENCES public.tbl_nivel_idioma(nvid_id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_estado FOREIGN KEY (ctev_estado_entrevista_id) REFERENCES public.tbl_estado_entrevista(esev_id);


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_solicitud_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_solicitud_candidato FOREIGN KEY (ctev_solicitud_candidato_id) REFERENCES public.tbl_solicitud_candidato(slcd_id);


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_tipo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_tipo FOREIGN KEY (ctev_tipo_entrevista_id) REFERENCES public.tbl_tipo_entrevista(tpet_id);


--
-- Name: tbl_cita_entrevista fk_tbl_cita_entrevista_usuario_creador; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_entrevista
    ADD CONSTRAINT fk_tbl_cita_entrevista_usuario_creador FOREIGN KEY (ctev_usuario_creador_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_cita_tipo_entrevista fk_tbl_cita_tipo_entrevista_cita; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_tipo_entrevista
    ADD CONSTRAINT fk_tbl_cita_tipo_entrevista_cita FOREIGN KEY (cten_cita_entrevista_id) REFERENCES public.tbl_cita_entrevista(ctev_id);


--
-- Name: tbl_cita_tipo_entrevista fk_tbl_cita_tipo_entrevista_tipo_entrevista; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cita_tipo_entrevista
    ADD CONSTRAINT fk_tbl_cita_tipo_entrevista_tipo_entrevista FOREIGN KEY (cten_tipo_entrevista_id) REFERENCES public.tbl_tipo_entrevista(tpet_id);


--
-- Name: tbl_cliente fk_tbl_cliente_area_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT fk_tbl_cliente_area_empresa FOREIGN KEY (cli_area_empresa_id) REFERENCES public.tbl_area(area_id);


--
-- Name: tbl_cliente fk_tbl_cliente_cargo_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT fk_tbl_cliente_cargo_empresa FOREIGN KEY (cli_cargo_empresa_id) REFERENCES public.tbl_cargo(crgo_id);


--
-- Name: tbl_cliente fk_tbl_cliente_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cliente
    ADD CONSTRAINT fk_tbl_cliente_empresa FOREIGN KEY (cli_empresa_id) REFERENCES public.tbl_empresa(emp_id);


--
-- Name: tbl_comuna fk_tbl_comuna_region; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_comuna
    ADD CONSTRAINT fk_tbl_comuna_region FOREIGN KEY (com_region_id) REFERENCES public.tbl_region(reg_id);


--
-- Name: tbl_cuestionario fk_tbl_cuestionario_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_cuestionario
    ADD CONSTRAINT fk_tbl_cuestionario_solicitud FOREIGN KEY (cues_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


--
-- Name: tbl_curso fk_tbl_curso_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT fk_tbl_curso_candidato FOREIGN KEY (curs_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_curso fk_tbl_curso_institucion; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_curso
    ADD CONSTRAINT fk_tbl_curso_institucion FOREIGN KEY (curs_institucion_id) REFERENCES public.tbl_institucion(inst_id);


--
-- Name: tbl_direccion_candidato fk_tbl_direccion_candidato_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT fk_tbl_direccion_candidato_candidato FOREIGN KEY (drcd_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_direccion_candidato fk_tbl_direccion_candidato_comuna; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_direccion_candidato
    ADD CONSTRAINT fk_tbl_direccion_candidato_comuna FOREIGN KEY (drcd_comuna_id) REFERENCES public.tbl_comuna(com_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_candidato FOREIGN KEY (etcd_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_carrera; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_carrera FOREIGN KEY (etcd_carrera_id) REFERENCES public.tbl_carrera(crra_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_institucion; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_institucion FOREIGN KEY (etcd_institucion_id) REFERENCES public.tbl_institucion(inst_id);


--
-- Name: tbl_estudio_candidato fk_tbl_estudio_candidato_nivel_educacional; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_estudio_candidato
    ADD CONSTRAINT fk_tbl_estudio_candidato_nivel_educacional FOREIGN KEY (etcd_nivel_educacional_id) REFERENCES public.tbl_nivel_educacional(nved_id);


--
-- Name: tbl_evaluacion_entrevista fk_tbl_evaluacion_entrevista_cita; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT fk_tbl_evaluacion_entrevista_cita FOREIGN KEY (even_cita_entrevista_id) REFERENCES public.tbl_cita_entrevista(ctev_id);


--
-- Name: tbl_evaluacion_entrevista fk_tbl_evaluacion_entrevista_resultado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT fk_tbl_evaluacion_entrevista_resultado FOREIGN KEY (even_nombre_resultado_id) REFERENCES public.tbl_nombre_resultado(nore_id);


--
-- Name: tbl_evaluacion_entrevista fk_tbl_evaluacion_entrevista_tipo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT fk_tbl_evaluacion_entrevista_tipo FOREIGN KEY (even_tipo_entrevista_id) REFERENCES public.tbl_tipo_entrevista(tpet_id);


--
-- Name: tbl_evaluacion_entrevista fk_tbl_evaluacion_entrevista_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_evaluacion_entrevista
    ADD CONSTRAINT fk_tbl_evaluacion_entrevista_usuario FOREIGN KEY (even_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_experiencia_laboral fk_tbl_experiencia_laboral_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT fk_tbl_experiencia_laboral_candidato FOREIGN KEY (expl_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_experiencia_laboral fk_tbl_experiencia_laboral_cargo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT fk_tbl_experiencia_laboral_cargo FOREIGN KEY (expl_cargo_id) REFERENCES public.tbl_cargo(crgo_id);


--
-- Name: tbl_experiencia_laboral fk_tbl_experiencia_laboral_empresa; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral
    ADD CONSTRAINT fk_tbl_experiencia_laboral_empresa FOREIGN KEY (expl_empresa_id) REFERENCES public.tbl_empresa(emp_id);


--
-- Name: tbl_experiencia_laboral_habilidad fk_tbl_expl_habilidad_experiencia; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral_habilidad
    ADD CONSTRAINT fk_tbl_expl_habilidad_experiencia FOREIGN KEY (exph_experiencia_laboral_id) REFERENCES public.tbl_experiencia_laboral(expl_id);


--
-- Name: tbl_experiencia_laboral_habilidad fk_tbl_expl_habilidad_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_experiencia_laboral_habilidad
    ADD CONSTRAINT fk_tbl_expl_habilidad_habilidad FOREIGN KEY (exph_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_habilidad fk_tbl_habilidad_categoria_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_habilidad
    ADD CONSTRAINT fk_tbl_habilidad_categoria_habilidad FOREIGN KEY (hab_categoria_habilidad_id) REFERENCES public.tbl_categoria_habilidad(cthb_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_estado_actual; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_estado_actual FOREIGN KEY (hsol_estado_actual_id) REFERENCES public.tbl_estado_solicitud(essl_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_estado_anterior; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_estado_anterior FOREIGN KEY (hsol_estado_anterior_id) REFERENCES public.tbl_estado_solicitud(essl_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_solicitud FOREIGN KEY (hsol_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


--
-- Name: tbl_historial_solicitud fk_tbl_historial_solicitud_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_historial_solicitud
    ADD CONSTRAINT fk_tbl_historial_solicitud_usuario FOREIGN KEY (hsol_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_institucion fk_tbl_institucion_tipo_institucion; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_institucion
    ADD CONSTRAINT fk_tbl_institucion_tipo_institucion FOREIGN KEY (inst_tipo_institucion_id) REFERENCES public.tbl_tipo_institucion(tint_id);


--
-- Name: tbl_opcion_respuesta fk_tbl_opcion_respuesta_pregunta; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_opcion_respuesta
    ADD CONSTRAINT fk_tbl_opcion_respuesta_pregunta FOREIGN KEY (opcr_pregunta_id) REFERENCES public.tbl_pregunta(preg_id);


--
-- Name: tbl_password_reset_token fk_tbl_password_reset_token_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_password_reset_token
    ADD CONSTRAINT fk_tbl_password_reset_token_usuario FOREIGN KEY (prst_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_pregunta_cuestionario fk_tbl_pregunta_cuestionario_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT fk_tbl_pregunta_cuestionario_cuestionario FOREIGN KEY (prcu_cuestionario_id) REFERENCES public.tbl_cuestionario(cues_id);


--
-- Name: tbl_pregunta_cuestionario fk_tbl_pregunta_cuestionario_pregunta; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta_cuestionario
    ADD CONSTRAINT fk_tbl_pregunta_cuestionario_pregunta FOREIGN KEY (prcu_pregunta_id) REFERENCES public.tbl_pregunta(preg_id);


--
-- Name: tbl_pregunta fk_tbl_pregunta_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT fk_tbl_pregunta_habilidad FOREIGN KEY (preg_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_pregunta fk_tbl_pregunta_nivel_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_pregunta
    ADD CONSTRAINT fk_tbl_pregunta_nivel_habilidad FOREIGN KEY (preg_nivel_habilidad_id) REFERENCES public.tbl_nivel_habilidad(nvhb_id);


--
-- Name: tbl_region fk_tbl_region_pais; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_region
    ADD CONSTRAINT fk_tbl_region_pais FOREIGN KEY (reg_pais_id) REFERENCES public.tbl_pais(pais_id);


--
-- Name: tbl_respuesta_pregunta fk_tbl_respuesta_pregunta_candidato_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT fk_tbl_respuesta_pregunta_candidato_cuestionario FOREIGN KEY (rspr_candidato_cuestionario_id) REFERENCES public.tbl_candidato_cuestionario(cdcu_id);


--
-- Name: tbl_respuesta_pregunta fk_tbl_respuesta_pregunta_opcion_respuesta; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT fk_tbl_respuesta_pregunta_opcion_respuesta FOREIGN KEY (rspr_opcion_respuesta_id) REFERENCES public.tbl_opcion_respuesta(opcr_id);


--
-- Name: tbl_respuesta_pregunta fk_tbl_respuesta_pregunta_pregunta_cuestionario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_respuesta_pregunta
    ADD CONSTRAINT fk_tbl_respuesta_pregunta_pregunta_cuestionario FOREIGN KEY (rspr_pregunta_cuestionario_id) REFERENCES public.tbl_pregunta_cuestionario(prcu_id);


--
-- Name: tbl_rol_permiso fk_tbl_rol_permiso_permiso; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT fk_tbl_rol_permiso_permiso FOREIGN KEY (rlpm_permiso_id) REFERENCES public.tbl_permiso(per_id);


--
-- Name: tbl_rol_permiso fk_tbl_rol_permiso_rol; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_rol_permiso
    ADD CONSTRAINT fk_tbl_rol_permiso_rol FOREIGN KEY (rlpm_rol_id) REFERENCES public.tbl_rol(rol_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_candidato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_candidato FOREIGN KEY (slcd_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_estado FOREIGN KEY (slcd_estado_solicitud_candidato_id) REFERENCES public.tbl_estado_solicitud_candidato(essc_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_motivo_rechazo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_motivo_rechazo FOREIGN KEY (slcd_motivo_rechazo_id) REFERENCES public.tbl_motivo_rechazo(mtrc_id);


--
-- Name: tbl_solicitud_candidato fk_tbl_solicitud_candidato_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_candidato
    ADD CONSTRAINT fk_tbl_solicitud_candidato_solicitud FOREIGN KEY (slcd_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_cargo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_cargo FOREIGN KEY (sol_cargo_id) REFERENCES public.tbl_cargo(crgo_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_cliente; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_cliente FOREIGN KEY (sol_cliente_id) REFERENCES public.tbl_cliente(cli_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_estado FOREIGN KEY (sol_estado_solicitud_id) REFERENCES public.tbl_estado_solicitud(essl_id);


--
-- Name: tbl_solicitud_habilidad fk_tbl_solicitud_habilidad_habilidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_tbl_solicitud_habilidad_habilidad FOREIGN KEY (solhb_habilidad_id) REFERENCES public.tbl_habilidad(hab_id);


--
-- Name: tbl_solicitud_habilidad fk_tbl_solicitud_habilidad_nivel; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_tbl_solicitud_habilidad_nivel FOREIGN KEY (solhb_nivel_habilidad_id) REFERENCES public.tbl_nivel_habilidad(nvhb_id);


--
-- Name: tbl_solicitud_habilidad fk_tbl_solicitud_habilidad_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud_habilidad
    ADD CONSTRAINT fk_tbl_solicitud_habilidad_solicitud FOREIGN KEY (solhb_solicitud_id) REFERENCES public.tbl_solicitud(sol_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_modalidad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_modalidad FOREIGN KEY (sol_modalidad_id) REFERENCES public.tbl_modalidad(mdld_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_prioridad; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_prioridad FOREIGN KEY (sol_prioridad_id) REFERENCES public.tbl_prioridad_solicitud(prsol_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_tipo_contrato; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_tipo_contrato FOREIGN KEY (sol_tipo_contrato_id) REFERENCES public.tbl_tipo_contrato(tpct_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_usuario_asignado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_usuario_asignado FOREIGN KEY (sol_usuario_asignado_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_solicitud fk_tbl_solicitud_usuario_creador; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_solicitud
    ADD CONSTRAINT fk_tbl_solicitud_usuario_creador FOREIGN KEY (sol_usuario_creador_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_usuario fk_tbl_usuario_area; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_area FOREIGN KEY (usr_area_id) REFERENCES public.tbl_area(area_id);


--
-- Name: tbl_usuario_cita_entrevista fk_tbl_usuario_cita_entrevista_cita; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT fk_tbl_usuario_cita_entrevista_cita FOREIGN KEY (usrce_cita_entrevista_id) REFERENCES public.tbl_cita_entrevista(ctev_id);


--
-- Name: tbl_usuario_cita_entrevista fk_tbl_usuario_cita_entrevista_tipo; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT fk_tbl_usuario_cita_entrevista_tipo FOREIGN KEY (usrce_tipo_entrevista_id) REFERENCES public.tbl_tipo_entrevista(tpet_id);


--
-- Name: tbl_usuario_cita_entrevista fk_tbl_usuario_cita_entrevista_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario_cita_entrevista
    ADD CONSTRAINT fk_tbl_usuario_cita_entrevista_usuario FOREIGN KEY (usrce_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_usuario fk_tbl_usuario_estado; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_estado FOREIGN KEY (usr_estado_usuario_id) REFERENCES public.tbl_estado_usuario(esusr_id);


--
-- Name: tbl_candidato fk_tbl_usuario_estado_usuario; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato
    ADD CONSTRAINT fk_tbl_usuario_estado_usuario FOREIGN KEY (cand_estado_usuario_id) REFERENCES public.tbl_estado_usuario(esusr_id);


--
-- Name: tbl_usuario fk_tbl_usuario_rol; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_usuario
    ADD CONSTRAINT fk_tbl_usuario_rol FOREIGN KEY (usr_rol_id) REFERENCES public.tbl_rol(rol_id);


--
-- Name: tbl_candidato_idioma tbl_candidato_idioma_cdio_candidato_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_idioma
    ADD CONSTRAINT tbl_candidato_idioma_cdio_candidato_id_fkey FOREIGN KEY (cdio_candidato_id) REFERENCES public.tbl_candidato(cand_id);


--
-- Name: tbl_candidato_idioma tbl_candidato_idioma_cdio_idioma_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_candidato_idioma
    ADD CONSTRAINT tbl_candidato_idioma_cdio_idioma_id_fkey FOREIGN KEY (cdio_idioma_id) REFERENCES public.tbl_idioma(idio_id);


--
-- Name: tbl_documento_reporte_candidato tbl_documento_reporte_candidat_drcp_solicitud_candidato_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_documento_reporte_candidato
    ADD CONSTRAINT tbl_documento_reporte_candidat_drcp_solicitud_candidato_id_fkey FOREIGN KEY (drcp_solicitud_candidato_id) REFERENCES public.tbl_solicitud_candidato(slcd_id);


--
-- Name: tbl_documento_reporte_candidato tbl_documento_reporte_candidato_drcp_usuario_generador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_documento_reporte_candidato
    ADD CONSTRAINT tbl_documento_reporte_candidato_drcp_usuario_generador_id_fkey FOREIGN KEY (drcp_usuario_generador_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_notificacion_reclutamiento tbl_notificacion_reclutamiento_ntfr_solicitud_candidato_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_notificacion_reclutamiento
    ADD CONSTRAINT tbl_notificacion_reclutamiento_ntfr_solicitud_candidato_id_fkey FOREIGN KEY (ntfr_solicitud_candidato_id) REFERENCES public.tbl_solicitud_candidato(slcd_id);


--
-- Name: tbl_notificacion_reclutamiento tbl_notificacion_reclutamiento_ntfr_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_notificacion_reclutamiento
    ADD CONSTRAINT tbl_notificacion_reclutamiento_ntfr_usuario_id_fkey FOREIGN KEY (ntfr_usuario_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: tbl_plantilla_notificacion tbl_plantilla_notificacion_plnt_usuario_actualizacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: elitsoft_admin
--

ALTER TABLE ONLY public.tbl_plantilla_notificacion
    ADD CONSTRAINT tbl_plantilla_notificacion_plnt_usuario_actualizacion_id_fkey FOREIGN KEY (plnt_usuario_actualizacion_id) REFERENCES public.tbl_usuario(usr_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: elitsoft_admin
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict QxoTx3f0RRc8mzfUmYZOba4AO4FbmAMG7KPcNadJ0J6bV4A7D2F1ahPGp8fz0HW
