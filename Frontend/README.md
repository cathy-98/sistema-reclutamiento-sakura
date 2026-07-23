# Frontend Sakura

Aplicación web del sistema de reclutamiento Sakura, construida con Angular. Este frontend contiene las vistas operativas para autenticación, gestión de solicitudes y gestión de candidatos.

## Stack

- Angular `21.2`
- TypeScript `5.9`
- RxJS `7.8`
- Angular Router
- Angular Forms
- Vitest para pruebas

## Requisitos

- Node.js compatible con Angular 21
- npm `11.11.0` o superior
- Backend disponible cuando se conecten endpoints reales

## Instalación

Desde la carpeta `Frontend`:

```bash
npm install
```

## Ejecución Local

```bash
npm start
```

La aplicación queda disponible en:

```text
http://localhost:4200
```

Rutas principales:

- `/login`
- `/dashboard`
- `/solicitudes`
- `/candidatos`

## Scripts

```bash
npm start
```

Levanta el servidor de desarrollo.

```bash
npm run build
```

Compila la aplicación en `dist/frontend`.

```bash
npm run watch
```

Compila en modo observación para desarrollo.

```bash
npm test
```

Ejecuta pruebas con Vitest.

## Estructura Principal

```text
src/app
├── guards
│   └── auth.guard.ts
├── layouts
│   └── app-shell
├── pages
│   ├── candidatos
│   ├── dashboard
│   ├── login
│   └── solicitudes
├── services
│   ├── auth.service.ts
│   └── solicitudes.service.ts
└── shared
    ├── components
    │   ├── alert
    │   ├── confirm-dialog
    │   ├── data-table
    │   ├── file-dropzone
    │   ├── modal
    │   └── stepper
    ├── models
    └── utils
```

## Componentes Reutilizables

### `app-data-table`

Tabla reutilizable para módulos operativos. Actualmente se usa en:

- Solicitudes
- Candidatos

Responsabilidades:

- Render de columnas configurables
- Columnas sticky
- Selección por checkbox
- Acciones por fila
- Paginación
- Estado de carga
- Estado de error con reintento
- Empty state

Uso general:

```html
<app-data-table
  title="Listado"
  [columns]="columnas"
  [rows]="registrosPaginados"
  [total]="registros.length"
  [page]="paginaActual"
  [pageSize]="registrosPorPagina"
  [rowId]="obtenerId"
  [actions]="acciones"
  [loading]="cargando"
  [errorMessage]="errorCarga"
  (pageChange)="cambiarPagina($event)"
  (pageSizeChange)="cambiarRegistrosPorPagina($event)"
  (actionClick)="manejarAccionTabla($event)"
  (retry)="cargarRegistros()"
></app-data-table>
```

### `app-file-dropzone`

Componente reutilizable para carga de archivos con Drag & Drop.

Actualmente se usa en candidatos para cargar CVs.

Incluye:

- Drag & Drop
- Selección manual de archivos
- Validación de extensión
- Validación de tamaño máximo
- Lista de archivos seleccionados
- Opción para quitar archivos

Uso general:

```html
<app-file-dropzone
  title="Carga CVs de candidatos"
  description="Arrastra uno o más CVs para dejarlos listos antes de procesarlos."
  buttonText="Seleccionar CVs"
  [allowedExtensions]="['pdf', 'doc', 'docx']"
  [maxFileSizeMb]="10"
  (filesChange)="actualizarArchivos($event)"
></app-file-dropzone>
```

## Módulos

### Login

Vista de autenticación. Usa `AuthService` para iniciar sesión, guardar token y mantener datos básicos del usuario.

### Dashboard

Vista inicial posterior al login.

### Solicitudes

Módulo para listar, crear, ver, editar y cancelar solicitudes.

Notas actuales:

- La tabla usa `app-data-table`.
- El listado usa datos locales desde `SolicitudesService`.
- El flujo está preparado para cargar desde backend.
- Incluye estados UX de carga, error, vacío y reintento.

### Candidatos

Módulo para listar candidatos, filtrar registros y cargar CVs.

Notas actuales:

- La tabla usa `app-data-table`.
- Los datos de candidatos son mock locales.
- La carga de CVs usa `app-file-dropzone`.
- Falta conectar endpoint real para candidatos y subida de archivos.

## Conexión con Backend

Hoy algunos servicios usan datos locales para avanzar en UI/UX. Para conectar backend, reemplazar la fuente local por `HttpClient`.

Ejemplo:

```ts
return this.http.get<SolicitudResumen[]>('http://localhost:8000/api/solicitudes');
```

Para carga de CVs, usar `FormData`:

```ts
const formData = new FormData();

archivos.forEach((archivo) => {
  formData.append('archivos', archivo);
});

return this.http.post('/api/candidatos/cvs', formData);
```

## UX y Accesibilidad

La interfaz se está ajustando para usuarios operativos, incluyendo usuarios +40:

- Textos más legibles en tablas y formularios
- Inputs con altura cómoda
- Botones con mayor área clickeable
- Foco visible para teclado
- Estados claros de carga, error y vacío
- Acciones masivas visibles solo cuando aplican
- Componentes reutilizables para mantener consistencia

## Build

```bash
npm run build
```

El build puede mostrar warnings de presupuesto SCSS en algunos componentes. Mientras no aparezca `ERROR`, la compilación queda generada correctamente.

## Convenciones

- Mantener componentes compartidos en `src/app/shared/components`.
- Evitar duplicar tablas por módulo; usar `app-data-table`.
- Evitar duplicar cargas de archivos; usar `app-file-dropzone`.
- Mantener textos visibles claros y orientados a tarea.
- Usar estados explícitos: cargando, error, vacío y con datos.

## Próximos Pasos Recomendados

- Conectar `SolicitudesService` a backend real.
- Crear servicio real de candidatos.
- Implementar subida de CVs con `Multipart/Form-Data`.
- Mapear columnas reales desde `tbl_candidato`.
- Agregar pruebas para componentes compartidos.
