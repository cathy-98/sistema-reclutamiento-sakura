# Preparacion de integraciones frontend

Fuente revisada: `base_inicial.sql`, `arquitectura.txt` y `docs/criterio-mapeo-integracion.md`.

## Criterio aplicado

- No tocar backend para esta preparacion.
- Mantener servicios API con nombres fisicos de BD/backend (`cand_*`, `ctev_*`, `preg_*`, `cues_*`).
- Mantener pantallas con nombres legibles solo despues de pasar por mappers.
- Crear nuevas opciones de catalogo desde formularios cuando el endpoint ya existe.
- Evitar editar/eliminar catalogos desde formularios transaccionales: afecta trazabilidad de solicitudes y postulaciones historicas.

## Listo para conectar de a poco

| Modulo | Preparacion frontend | Pendiente real |
| --- | --- | --- |
| Solicitudes | Mapper activo `solicitud.mapper.ts`; modal consume catalogos, crea opciones permitidas y prepara `SOL-###` provisional desde el listado. | Cliente aparece pendiente porque no hay router `/clientes` activo. El correlativo definitivo deberia generarse en backend/BD para evitar duplicados concurrentes. |
| Candidatos | Mapper preparado en `candidato.mapper.ts`; acepta `cand_apellido_paterno/materno` y `cand_apellidos`. | Conectar cuando `/candidatos` tenga contrato estable para lista/perfil. |
| Entrevistas | Mapper preparado en `entrevista.mapper.ts`; arma `ctev_fecha_hora_inicio/fin` desde fecha y hora del modal. | Conectar cuando exista endpoint de citas e integrantes. |
| Cuestionarios | Mapper preparado en `cuestionario.mapper.ts`; separa `preg_*` y respuestas `oprs_*`. | Conectar cuando exista endpoint de preguntas/cuestionarios/respuestas. |
| Clientes/Empresas | Modelo SQL existe (`tbl_cliente`, `tbl_empresa`) y solicitud tiene `sol_cliente_id`. | Falta endpoint activo; no se debe simular CRUD en frontend contra una ruta inexistente. |

## Orden recomendado

1. Terminar Cliente/Empresa como integracion dedicada, porque `sol_cliente_id` depende de eso.
2. Conectar listado/perfil de Candidatos con mapper tolerante a diferencias de apellidos.
3. Conectar Entrevistas despues de definir como vendran los participantes (`tbl_usuario_cita_entrevista`).
4. Conectar Cuestionarios al final, porque necesita preguntas, respuestas, asignaciones y resultados.

## Nota de trazabilidad

Para catalogos usados por registros historicos conviene permitir crear, pero no editar/eliminar inline. Si despues se necesita mantenimiento, deberia vivir en una pantalla administrativa y aplicar reglas como "bloquear eliminacion si esta en uso" o "desactivar en vez de borrar".

## Codigo de solicitud

`tbl_solicitud.sol_codigo` tiene formato `SOL-###`, largo 8 y restriccion unica. El frontend puede preparar el siguiente valor como ayuda visual y para desbloquear el POST actual, pero no debe ser la fuente definitiva cuando existan varios usuarios creando solicitudes al mismo tiempo.
