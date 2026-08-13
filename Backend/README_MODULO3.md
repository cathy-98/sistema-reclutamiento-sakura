# Módulo 3 — Candidatos, CV y Postulaciones

Paquete de reemplazo/agregado para el backend Sakura basado en el esquema físico de `base_inicial.sql` y las reglas funcionales acordadas.

Lea primero `INTEGRACION_MODULO3.md`.

## Validación realizada al generar el paquete
- `python -m compileall` sobre los archivos generados: OK.
- Registro de `app.main` y `sqlalchemy.orm.configure_mappers()`: OK en motor SQLite de validación (con stub de bcrypt únicamente porque el runtime de generación no tenía ese paquete; el proyecto real ya lo declara en requirements).
- Rutas principales M3 registradas: OK.

## Importante
Antes de ejecutar el backend real, aplique `migrations/004_modulo3_candidatos_postulaciones.sql` y agregue `python-docx` a requirements si desea importar DOCX.
