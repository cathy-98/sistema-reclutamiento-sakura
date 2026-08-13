# QA Automatizada — Módulo 3 Candidatos / CV / Postulaciones

Esta suite valida el Módulo 3 generado para Sakura sin modificar PostgreSQL durante las pruebas aisladas.

## Contenido

- `test/test_modulo3.py`: suite aislada FastAPI + SQLite en memoria. Incluye 45 funciones de test (46 casos por parametrización).
- `test/test_modulo3_reglas_unitarias.py`: reglas puras ya incluidas originalmente con M3.
- `live/test_modulo3_live.py`: recorrido contra el backend real, Docker y PostgreSQL.
- `requirements-test-modulo3.txt`: dependencias de QA.

## Cobertura aislada

La suite prueba:

- JWT y RBAC: 401/403, CAN_VIEW, CAN_UPDATE y aislamiento del candidato.
- CRUD de candidatos y baja lógica.
- Password automática, password explícita, hash no expuesto, login candidato y cambio de password.
- Regla de email: usuario interno vs candidato y duplicados de candidato.
- Validaciones de RUT/DV, disponibilidad y referencias.
- Normalización y deduplicación de URLs separadas por `;`.
- Dirección, habilidades, estudios, cursos y experiencia laboral.
- Importación de CV TXT, reimportación sin cambiar password, importación múltiple y formatos inválidos.
- Asociación candidato-solicitud y evaluación de habilidades excluyentes sin bloqueo.
- Postulaciones, listados, actualización y flujo de estados.
- Motivo de rechazo obligatorio para Inhabilitado/Descartado.
- Estados terminales.
- Integración M2↔M3: cierre con 0 contratados bloqueado, cierre parcial con warning y cierre total sin warning.

## Ejecución aislada

Copie `test/test_modulo3.py` y, si lo desea, `test/test_modulo3_reglas_unitarias.py` a `Backend/test/`.

Desde `Backend`:

```powershell
pytest test/test_modulo3_reglas_unitarias.py -v
pytest test/test_modulo3.py -v -x
```

La suite usa SQLite en memoria y no toca PostgreSQL.

## Ejecución LIVE

Requiere backend y PostgreSQL levantados y un usuario administrador con permisos de M1/M2/M3. También necesita un Reclutador Activo para crear la solicitud de prueba.

```powershell
$env:SAKURA_API_URL="http://127.0.0.1:8000"
$env:QA_ADMIN_EMAIL="correo_admin@dominio.cl"
$env:QA_ADMIN_PASSWORD="password_admin"
```

Si no puede descubrir automáticamente un Reclutador Activo:

```powershell
$env:QA_RECRUITER_USER_ID="2"
```

Ejecute:

```powershell
python live/test_modulo3_live.py
```

El runner LIVE crea una solicitud QA de 2 vacantes, un candidato que termina Contratado y valida el cierre parcial con `X-Sakura-Warning`. La solicitud y ese candidato quedan conservados deliberadamente como evidencia de trazabilidad. El candidato creado solo para importación de CV se da de baja lógica al final.

## Gmail

Estos tests no requieren Gmail ni envían correos. El flujo M3 validado aquí cubre login y cambio de contraseña del candidato. La recuperación por correo sigue separada.
