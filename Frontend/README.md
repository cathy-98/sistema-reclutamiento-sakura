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
    │   ├── action-bar
    │   ├── alert
    │   ├── avatar
    │   ├── button
    │   ├── card
    │   ├── confirm-dialog
    │   ├── data-table
    │   ├── file-dropzone
    │   ├── file-list
    │   ├── filter-panel
    │   ├── form-actions
    │   ├── form-field
    │   ├── form-section
    │   ├── icon-button
    │   ├── match-score
    │   ├── modal
    │   ├── page-header
    │   ├── page-layout
    │   ├── pagination
    │   ├── section-header
    │   ├── state-message
    │   ├── status-badge
    │   ├── stepper
    │   ├── table-toolbar
    │   └── wizard-layout
    ├── models
    ├── pipes
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

### Componentes base de UI

Componentes compartidos para mantener consistencia entre módulos:

- `app-page-layout`: estructura base de página.
- `app-page-header`: cabecera principal de módulo.
- `app-filter-panel`: panel reusable de filtros y búsqueda rápida.
- `app-action-bar`: barra de acciones masivas.
- `app-button`: botón base con variantes.
- `app-icon-button`: botón cuadrado para acciones por icono.
- `app-status-badge`: estados y prioridades.
- `app-match-score`: porcentaje visual de match.
- `app-avatar`: avatar con iniciales.
- `app-pagination`: paginación.
- `app-state-message`: estados de carga, error y vacío.
- `app-form-section`: sección de formulario largo.
- `app-form-actions`: footer de acciones de formulario.
- `app-file-list`: listado de archivos seleccionados.

### Pipes compartidos

- `currencyCl`: formatea números con separador chileno, por ejemplo `1200000` como `1.200.000`.

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
- El perfil del candidato se abre desde la acción `Ver candidato` de la tabla.
- Falta conectar endpoint real para candidatos y subida de archivos.

#### Perfil del candidato

El perfil del candidato está implementado como un modal grande de detalle. Se eligió modal porque el flujo nace desde el listado de candidatos y permite revisar información completa sin perder filtros, página actual ni selección del listado.

Archivos principales:

```text
src/app/pages/candidatos
├── candidato-perfil-modal
│   ├── candidato-perfil-modal.ts
│   ├── candidato-perfil-modal.html
│   └── candidato-perfil-modal.scss
├── candidato-profile-tabs
│   ├── candidato-profile-tabs.ts
│   ├── candidato-profile-tabs.html
│   └── candidato-profile-tabs.scss
├── candidato-summary-card
│   ├── candidato-summary-card.ts
│   ├── candidato-summary-card.html
│   └── candidato-summary-card.scss
└── candidatos-list
```

Cómo se abre:

1. El usuario entra a `/candidatos`.
2. En la tabla, presiona la acción con icono de ojo.
3. `candidatos-list` guarda el candidato seleccionado en `candidatoSeleccionado`.
4. Se renderiza `app-candidato-perfil-modal`.
5. Al cerrar, `candidatoSeleccionado` vuelve a `null`.

Flujo en código:

```ts
manejarAccionTabla(evento: DataTableActionEvent<Candidato>) {
  if (evento.action === 'ver') {
    this.candidatoSeleccionado = evento.row;
    return;
  }
}
```

Y en template:

```html
<app-candidato-perfil-modal
  *ngIf="candidatoSeleccionado"
  [candidato]="candidatoSeleccionado"
  (cerrar)="cerrarPerfilCandidato()"
></app-candidato-perfil-modal>
```

Secciones disponibles dentro del perfil:

- Datos personales
- Experiencia laboral
- Estudios y cursos
- Historial de postulaciones
- Proceso de selección
- Análisis de match
- Documentos y notas

Componentes reutilizables usados por el perfil:

- `app-modal`
- `app-button`
- `app-avatar`
- `app-status-badge`
- `app-match-score`
- `app-icon-button`
- `app-candidato-profile-tabs`
- `app-candidato-summary-card`

Datos actuales del perfil:

- La información detallada está mockeada en `candidato-perfil-modal.ts`.
- El modal recibe los datos básicos desde la fila seleccionada.
- Las secciones internas están preparadas para reemplazarse por datos del backend.

Backend pendiente sugerido:

- `GET /api/candidatos/:id`
- `GET /api/candidatos/:id/postulaciones`
- `GET /api/candidatos/:id/experiencia`
- `GET /api/candidatos/:id/estudios`
- `GET /api/candidatos/:id/proceso-seleccion`
- `GET /api/candidatos/:id/match`
- `GET /api/candidatos/:id/documentos`
- `POST /api/candidatos/:id/notas`

Modelo sugerido para conectar el perfil:

```ts
interface CandidatoPerfil {
  id: number;
  nombre: string;
  correo: string;
  telefono: string;
  cargoActual: string;
  ubicacion: string;
  disponibilidad: string;
  expectativaSalarial: number;
  modalidadPreferida: string;
  postulaciones: PostulacionCandidato[];
  experiencia: ExperienciaLaboral[];
  estudios: EstudioCandidato[];
  procesoSeleccion: EtapaProceso[];
  match: AnalisisMatch;
  documentos: DocumentoCandidato[];
  notas: NotaCandidato[];
}
```

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
