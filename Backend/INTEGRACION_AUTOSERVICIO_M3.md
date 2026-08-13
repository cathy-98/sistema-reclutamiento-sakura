# M3 - Autoservicio del candidato

Reemplazar:
- Backend/app/candidatos/router.py
- Backend/app/candidatos/services.py
- Backend/app/candidatos/schemas.py

No requiere migración SQL.

## Endpoints nuevos
- GET /candidatos/me/perfil-completo
- PATCH /candidatos/me
- GET/POST /candidatos/me/habilidades
- PATCH/DELETE /candidatos/me/habilidades/{item_id}
- GET/POST /candidatos/me/estudios
- PATCH/DELETE /candidatos/me/estudios/{item_id}
- GET/POST /candidatos/me/experiencias
- PATCH/DELETE /candidatos/me/experiencias/{item_id}
- GET/POST /candidatos/me/cursos
- PATCH/DELETE /candidatos/me/cursos/{item_id}
- GET /candidatos/me/direcciones
- PUT/DELETE /candidatos/me/direccion
- GET /candidatos/me/solicitudes

El cand_id se obtiene siempre desde el JWT principal_type=candidato.
El candidato no puede editar email, nombres, RUT/DV, fecha de nacimiento, estado, fecha de creación, cand_cv_urls ni estados/datos de postulaciones.

## Pruebas
Copiar test/test_modulo3_completo.py a Backend/test/ y ejecutar:
pytest test/test_modulo3_completo.py -v -x

Luego copiar live/test_modulo3_live_completo.py a Backend/live/ y ejecutar con QA_ADMIN_EMAIL/QA_ADMIN_PASSWORD:
python live/test_modulo3_live_completo.py
