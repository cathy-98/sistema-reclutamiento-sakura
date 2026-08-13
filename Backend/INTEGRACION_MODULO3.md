# Integración Módulo 3 — Candidatos / CV / Postulaciones

## Alcance implementado
- CRUD de candidatos con `CAN_VIEW`, `CAN_UPDATE`, `CAN_DELETE`.
- Baja lógica con estado `Eliminado`.
- Login único `/auth/login` para usuario interno y candidato; JWT incorpora `principal_type`.
- `/auth/change-password` funciona para ambos tipos de identidad.
- Email cruzado: email existente en `tbl_usuario` rechaza creación de candidato; email de candidato rechaza creación/edición de usuario interno.
- Alta manual y alta/actualización desde uno o varios CV.
- Lectura conservadora PDF/DOCX/TXT.
- CV almacenado por ruta; varias rutas en `cand_cv_urls`, separadas por `;`, con deduplicación.
- CRUD de habilidades, estudios, cursos y experiencias.
- Asociación candidato ↔ solicitud y estados de postulación.
- `Inhabilitado`/`Descartado` requieren motivo de rechazo.
- Incumplir skills excluyentes no bloquea asociación: devuelve advertencia.
- Regla de cierre M2↔M3: 0 contratados bloquea `Cerrado`; parcial permite cierre con warning; contratados >= vacantes cierra normal.
- Entrevistas detalladas e historial candidato/solicitud quedan fuera del alcance acordado.

## Instalación
1. Copiar/reemplazar los archivos bajo `Backend/app`.
2. Agregar `requirements-modulo3.txt` a `Backend/requirements.txt`.
3. Ejecutar `migrations/004_modulo3_candidatos_postulaciones.sql`.
4. Configurar opcionalmente `CANDIDATE_CV_STORAGE_DIR`; default: `storage/cv`.
5. Reiniciar/reconstruir backend.

### Migración Docker
```powershell
Get-Content -Raw .\migrations\004_modulo3_candidatos_postulaciones.sql | docker compose exec -T postgres_db psql -U elitsoft_admin -d db_reclutamiento_elitsoft
```

## Endpoints principales
- `GET/POST /candidatos`
- `GET/PUT/PATCH/DELETE /candidatos/{id}`
- `GET /candidatos/me`
- `POST /candidatos/importar-cv`
- `POST /candidatos/importar-cvs`
- `POST/PATCH/DELETE /candidatos/{id}/habilidades`
- `POST/PATCH/DELETE /candidatos/{id}/estudios`
- `POST/PATCH/DELETE /candidatos/{id}/cursos`
- `POST/PATCH/DELETE /candidatos/{id}/experiencias`
- `POST /solicitudes/{solicitud_id}/candidatos/{candidato_id}`
- `GET /solicitudes/{solicitud_id}/candidatos`
- `GET /candidatos/{candidato_id}/solicitudes`
- `PATCH /postulaciones/{id}`
- `PATCH /postulaciones/{id}/estado`

## Importación CV
El parser es deliberadamente conservador: extrae solo datos que puede identificar razonablemente y no crea catálogos arbitrarios. Si el email ya existe en `tbl_candidato`, se reutiliza el candidato, se complementan campos vacíos, se acumula la nueva ruta del CV y no se modifica la contraseña.

## Password inicial
Si no se entrega `password_inicial`, el backend genera una contraseña aleatoria, guarda solamente bcrypt y devuelve el texto original una única vez en `password_temporal`. `cand_password` nunca aparece en respuestas normales.

## Recuperación por correo
`/auth/change-password` ya soporta candidato autenticado. `forgot-password/reset-password` se mantiene en esta entrega para usuarios internos porque la tabla M1 de tokens referencia `tbl_usuario`; puede extenderse posteriormente con una tabla/token polimórfico para candidatos.
