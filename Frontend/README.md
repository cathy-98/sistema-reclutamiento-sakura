# Frontend Sakura

Frontend Angular del sistema de reclutamiento Sakura. Esta aplicación contiene las vistas operativas para login, dashboard, solicitudes, candidatos, perfil de candidato y gestión de entrevistas.

El objetivo del frontend es separar bien tres responsabilidades:

- `pages`: pantallas completas del sistema.
- `shared`: componentes reutilizables, pipes, modelos y utilidades.
- `services`: lógica de datos y conexión con backend.

## Stack

- Angular `21.2`
- TypeScript `5.9`
- RxJS `7.8`
- Angular Router
- Angular Forms y Reactive Forms
- Angular HttpClient con interceptor de autenticación
- Vitest para pruebas
- Docker para ejecución integrada con backend y PostgreSQL

## Requisitos

- Node.js compatible con Angular 21
- npm `11.11.0` o superior
- Docker Desktop si se ejecuta con `docker compose`
- Backend disponible en `http://localhost:8000` cuando se conecten endpoints reales

## Ejecución Local

Desde la carpeta `Frontend`:

```bash
npm install
npm start
```

La aplicación queda disponible en:

```text
http://localhost:4200
```

Si el puerto `4200` ya está ocupado, revisar qué proceso lo usa:

```powershell
netstat -ano | findstr :4200
```

## Ejecución Con Docker

Desde la raíz del proyecto:

```bash
docker compose up -d
```

Servicios principales:

- Frontend: `http://localhost:4200`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Para levantar solo el frontend:

```bash
docker compose up -d frontend
```

Para revisar contenedores:

```bash
docker ps
```

Importante: si Docker ya está usando el puerto `4200`, no ejecutar `npm start` al mismo tiempo porque ambos intentarán usar el mismo puerto.

## Scripts

```bash
npm start
```

Levanta Angular en modo desarrollo.

```bash
npm run build
```

Compila la aplicación en `dist/frontend`.

```bash
npm run watch
```

Compila en modo observación.

```bash
npm test
```

Ejecuta pruebas.

## Rutas Principales

Las rutas se configuran en:

```text
src/app/app.routes.ts
```

Rutas actuales:

- `/login`: inicio de sesión.
- `/dashboard`: vista inicial.
- `/solicitudes`: listado y gestión de solicitudes.
- `/candidatos`: listado, carga de CVs y acciones sobre candidatos.
- `/candidatos/perfil/:id`: perfil completo del candidato.
- `/entrevistas`: agenda y control de entrevistas.

Las rutas internas usan `AppShell` y `authGuard` para proteger el acceso según sesión y rol.

## Estructura Principal

```text
src/app
├── app.config.ts
├── app.routes.ts
├── guards
│   └── auth.guard.ts
├── interceptors
│   └── auth.interceptor.ts
├── layouts
│   └── app-shell
├── pages
│   ├── candidatos
│   ├── dashboard
│   ├── entrevistas
│   ├── login
│   └── solicitudes
├── services
│   ├── auth.service.ts
│   ├── entrevistas.service.ts
│   └── solicitudes.service.ts
└── shared
    ├── components
    ├── models
    ├── pipes
    └── utils
```

## Cómo Leer Una Pantalla Angular

Cada pantalla o componente suele tener tres archivos:

```text
nombre.ts
nombre.html
nombre.scss
```

- `.ts`: lógica, variables, funciones, llamadas a servicios.
- `.html`: estructura visual y bindings.
- `.scss`: estilos del componente.

Ejemplo:

```text
src/app/pages/candidatos/candidatos-list
├── candidatos-list.ts
├── candidatos-list.html
└── candidatos-list.scss
```

Regla mental:

```text
TS = lógica
HTML = vista
SCSS = estilos
Service = datos/API
Shared component = pieza reutilizable
```

## Conceptos Angular Usados

### Interpolación

Muestra valores del `.ts` en el `.html`.

```ts
nombreUsuario = 'Joaquín';
```

```html
<h1>Bienvenido {{ nombreUsuario }}</h1>
```

### Property Binding

Pasa valores desde la pantalla hacia un componente.

```html
<app-data-table [rows]="candidatos" [loading]="cargando"></app-data-table>
```

### Event Binding

Ejecuta una función cuando ocurre una acción.

```html
<button (click)="buscar()">Buscar</button>
```

### `@Input()`

Permite que un componente reutilizable reciba datos.

```ts
@Input() rows = [];
```

### `@Output()`

Permite que un componente reutilizable avise eventos.

```ts
@Output() actionClick = new EventEmitter<DataTableActionEvent<T>>();
```

Uso desde una pantalla:

```html
<app-data-table
  [rows]="candidatos"
  (actionClick)="manejarAccionTabla($event)"
></app-data-table>
```

## Variables Globales De Estilo

Los estilos se apoyan en variables globales CSS para mantener consistencia visual.

Ejemplos:

```scss
var(--color-sakura)
var(--color-border)
var(--color-text)
var(--color-muted)
var(--color-surface-soft)
var(--color-table-header)
var(--shadow-card-soft)
```

Estas variables permiten que botones, tablas, modales, filtros, formularios y estados visuales usen la misma identidad gráfica.

Ejemplo:

```scss
.card {
  border: 1px solid var(--color-border);
  background: var(--color-card-bg);
  box-shadow: var(--shadow-card-soft);
}
```

Si se cambia una variable global, se actualizan todos los componentes que la usan.

## Componentes Reutilizables

Los componentes reutilizables viven en:

```text
src/app/shared/components
```

Se usan como etiquetas Angular con prefijo `app`.

Ejemplo:

```html
<app-modal></app-modal>
<app-data-table></app-data-table>
<app-button></app-button>
```

El selector se define en el componente:

```ts
@Component({
  selector: 'app-modal'
})
```

### Componentes Compartidos Principales

- `app-page-layout`: estructura base de página.
- `app-page-header`: cabecera unificada de módulo.
- `app-filter-panel`: filtros y búsqueda rápida.
- `app-action-bar`: acciones masivas.
- `app-data-table`: tabla configurable.
- `app-pagination`: paginación.
- `app-state-message`: carga, error y vacío.
- `app-modal`: modal base.
- `app-button`: botón base.
- `app-icon-button`: botón cuadrado con ícono.
- `app-form-field`: campo de formulario.
- `app-form-section`: sección de formulario.
- `app-form-actions`: acciones inferiores de formulario.
- `app-stepper`: pasos de formularios largos.
- `app-file-dropzone`: carga de archivos drag and drop.
- `app-file-list`: tabla compacta de archivos seleccionados.
- `app-status-badge`: estados visuales.
- `app-match-score`: porcentaje de match.
- `app-avatar`: iniciales de persona.

## Cuándo Crear Un Componente Reutilizable

Conviene crear o ampliar un componente reutilizable cuando:

- Se usa en más de una pantalla.
- Tiene una estructura visual común.
- Tiene comportamiento repetido.
- Necesita mantener consistencia de UX.
- Si cambia el diseño, debería cambiar igual en varios módulos.

Ejemplos claros:

- Tablas
- Modales
- Botones
- Filtros
- Paginación
- Estados de carga/error/vacío
- Cargas de archivos
- Headers de página

No todo debe ser reutilizable. Si algo solo vive en un flujo específico, puede quedarse dentro del módulo.

## Cómo Se Cambia Un Componente Reutilizable

Hay dos formas:

### 1. Cambiar Lo Que Se Le Pasa Desde La Pantalla

Ejemplo: `app-data-table` muestra columnas distintas según el módulo.

En candidatos:

```ts
columnas = [
  { key: 'idSolicitud', label: 'ID solicitud', width: 112 },
  { key: 'nombre', label: 'Nombre completo', width: 220 },
  { key: 'correo', label: 'Correo electrónico', width: 230 },
];
```

```html
<app-data-table [columns]="columnas" [rows]="candidatos"></app-data-table>
```

En entrevistas:

```ts
columnas = [
  { key: 'idSolicitud', label: 'ID solicitud', width: 112 },
  { key: 'estado', label: 'Estado entrevista', width: 160 },
  { key: 'fecha', label: 'Fecha', width: 135 },
];
```

Mismo componente, datos diferentes.

### 2. Agregar Una Capacidad General Al Componente

Ejemplo: se agregó el ícono `trash` a `app-icon-button`.

Así cualquier pantalla puede usar:

```html
<app-icon-button icon="trash" label="Eliminar"></app-icon-button>
```

Regla:

```text
Si cambia solo una pantalla, cambia la pantalla.
Si es una capacidad para varias pantallas, cambia el componente reutilizable.
```

## `app-data-table`

Tabla reutilizable para módulos operativos.

Actualmente se usa en:

- Solicitudes
- Candidatos
- Entrevistas
- Tablas internas de formularios cuando aplica

Responsabilidades:

- Columnas configurables
- Anchos definidos
- Columnas fijas izquierda/derecha
- Selección por checkbox
- Acciones por fila
- Paginación
- Estado de carga
- Estado de error
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

## `app-file-dropzone` Y `app-file-list`

`app-file-dropzone` permite seleccionar o arrastrar archivos.

Incluye:

- Drag and drop
- Selección manual
- Validación por extensión
- Validación por tamaño máximo
- Emisión de archivos seleccionados

Uso:

```html
<app-file-dropzone
  title="Carga CVs de candidatos"
  description="Arrastra uno o más CVs para dejarlos listos antes de procesarlos."
  buttonText="Seleccionar CVs"
  [allowedExtensions]="['pdf', 'doc', 'docx']"
  [maxFileSizeMb]="10"
  (filesChange)="actualizarArchivosCv($event)"
></app-file-dropzone>
```

`app-file-list` muestra los archivos seleccionados en una tabla compacta con:

- Cantidad de archivos.
- Peso total.
- Scroll interno para listas grandes.
- Acción de eliminar por archivo.

Esto evita que la pantalla crezca demasiado si se cargan muchos CVs.

## Módulos Implementados

### Login

Vista de autenticación.

Responsabilidades:

- Capturar credenciales.
- Llamar a `AuthService`.
- Guardar sesión/token.
- Redirigir al dashboard.

Archivos:

```text
src/app/pages/login
```

### Dashboard

Vista inicial posterior al login.

Archivos:

```text
src/app/pages/dashboard
```

### Solicitudes

Módulo para listar y gestionar solicitudes de vacantes.

Archivos principales:

```text
src/app/pages/solicitudes
├── solicitudes-list
└── solicitud-form-modal
```

Usa:

- `app-page-layout`
- `app-page-header`
- `app-filter-panel`
- `app-action-bar`
- `app-data-table`
- `app-modal`
- `SolicitudesService`

Estado actual:

- Usa servicio local preparado para backend.
- Tiene tabla, filtros, acciones, modal y estados UX.
- Pendiente conectar endpoints reales.

### Candidatos

Módulo para listar candidatos, cargar CVs, filtrar registros y ejecutar acciones individuales o masivas.

Archivos principales:

```text
src/app/pages/candidatos
├── candidatos-list
├── candidato-perfil-page
├── candidato-profile-tabs
└── candidato-summary-card
```

Usa:

- `app-page-layout`
- `app-page-header`
- `app-file-dropzone`
- `app-file-list`
- `app-filter-panel`
- `app-action-bar`
- `app-data-table`
- `app-entrevista-form-modal`

Funciones actuales:

- Listado mock de candidatos.
- Filtros por solicitud, nombre, correo, teléfono, estado, cargo, disponibilidad, renta, match, nivel y experiencia.
- Carga de CVs con validación.
- Acciones por fila: ver perfil, descargar CV, agendar entrevista.
- Acciones masivas: enviar correo, agendar entrevistas.
- Agenda individual desde el ícono de calendario.
- Agenda masiva con tabla de candidatos seleccionados y opción para quitar candidatos antes de guardar.

### Perfil De Candidato

El perfil del candidato es una página:

```text
/candidatos/perfil/:id
```

Se abre desde la acción de ver candidato en la tabla.

Flujo:

```text
Click en ver candidato
↓
router.navigate(['/candidatos/perfil', id])
↓
Se abre candidato-perfil-page
```

Secciones:

- Experiencia
- Estudios
- Postulaciones
- Match
- Documentos
- Observaciones

Estado actual:

- Datos mockeados.
- Recibe datos básicos por query params desde el listado.
- Preparado para consumir detalle desde backend.

### Entrevistas

Módulo para gestionar entrevistas.

Archivos principales:

```text
src/app/pages/entrevistas
├── entrevistas-list
├── entrevista-form-modal
└── entrevista-estado-modal
```

Usa:

- `app-page-layout`
- `app-page-header`
- `app-filter-panel`
- `app-action-bar`
- `app-data-table`
- `app-entrevista-form-modal`
- `app-entrevista-estado-modal`
- `EntrevistasService`

Funciones actuales:

- Listado de entrevistas.
- Filtros por cargo, fecha, estado y tipo.
- Crear entrevista.
- Crear entrevistas masivas desde candidatos.
- Reprogramar entrevista.
- Cancelar entrevista.

## Flujo De Agenda Individual

Desde candidatos:

```text
Click en calendario de una fila
↓
manejarAccionTabla()
↓
abrirAgendaEntrevista([candidato])
↓
mostrarModalAgenda = true
↓
app-entrevista-form-modal recibe un candidato
↓
guardarAgendaEntrevista(payload)
↓
EntrevistasService.crear(payload)
```

## Flujo De Agenda Masiva

Desde candidatos:

```text
Seleccionar candidatos
↓
Click en Agendar entrevistas
↓
abrirAgendaMasiva()
↓
app-entrevista-form-modal recibe varios candidatos
↓
La modal muestra tabla de seleccionados
↓
Se pueden quitar candidatos
↓
Guardar
↓
EntrevistasService.crearMasiva(payloads)
```

En agenda masiva se crea una entrevista por cada candidato seleccionado.

## Servicios

Los servicios viven en:

```text
src/app/services
```

Servicios actuales:

- `auth.service.ts`: login, token, usuario y rol.
- `solicitudes.service.ts`: datos y operaciones de solicitudes.
- `entrevistas.service.ts`: datos y operaciones de entrevistas.

Los servicios son el punto correcto para conectar APIs reales.

## Conexión Con Backend

Angular se conecta al backend mediante `HttpClient`.

La configuración está en:

```text
src/app/app.config.ts
```

Actualmente incluye:

```ts
provideHttpClient(withInterceptors([authInterceptor]))
```

Esto habilita peticiones HTTP y agrega el interceptor de autenticación.

## Qué Es GET Y POST

### GET

Se usa para pedir información.

Ejemplos:

```text
GET /api/candidatos
GET /api/solicitudes
GET /api/entrevistas
GET /api/candidatos/:id
```

En Angular:

```ts
listar() {
  return this.http.get<Candidato[]>('http://localhost:8000/api/candidatos');
}
```

### POST

Se usa para enviar o crear información.

Ejemplos:

```text
POST /api/candidatos
POST /api/entrevistas
POST /api/candidatos/cvs
```

En Angular:

```ts
crear(payload: EntrevistaPayload) {
  return this.http.post<EntrevistaResumen>('http://localhost:8000/api/entrevistas', payload);
}
```

## Paso A Paso Para Consumir Una API

### 1. Definir El Modelo

```ts
export interface Candidato {
  id: number;
  idSolicitud: string;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  estado: string;
  match: number;
}
```

### 2. Crear O Actualizar Un Servicio

```ts
@Injectable({ providedIn: 'root' })
export class CandidatosService {
  private apiUrl = 'http://localhost:8000/api/candidatos';

  constructor(private http: HttpClient) {}

  listar() {
    return this.http.get<Candidato[]>(this.apiUrl);
  }
}
```

### 3. Inyectar El Servicio En La Página

```ts
constructor(private candidatosService: CandidatosService) {}
```

### 4. Crear Estados De Pantalla

```ts
candidatos: Candidato[] = [];
cargando = false;
errorCarga = '';
```

### 5. Llamar La API

```ts
cargarCandidatos() {
  this.cargando = true;
  this.errorCarga = '';

  this.candidatosService.listar().subscribe({
    next: (candidatos) => {
      this.candidatos = candidatos;
      this.cargando = false;
    },
    error: () => {
      this.errorCarga = 'No se pudieron cargar los candidatos.';
      this.cargando = false;
    },
  });
}
```

### 6. Mostrar Datos En La Vista

```html
<app-data-table
  title="Listado de candidatos"
  [rows]="candidatosPaginados"
  [columns]="columnas"
  [loading]="cargando"
  [errorMessage]="errorCarga"
></app-data-table>
```

### 7. Manejar Guardado Con POST

```ts
guardarEntrevista(payload: EntrevistaPayload) {
  this.entrevistasService.crear(payload).subscribe({
    next: () => {
      this.cerrarModalEntrevista();
      this.cargarEntrevistas();
    },
    error: () => {
      this.errorCarga = 'No se pudo crear la entrevista.';
    },
  });
}
```

## Subida De CVs Con `FormData`

Para subir archivos al backend se usa `Multipart/Form-Data`.

Ejemplo de servicio:

```ts
subirCvs(files: File[]) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append('files', file);
  });

  return this.http.post('http://localhost:8000/api/candidatos/cvs', formData);
}
```

Ejemplo desde componente:

```ts
archivosCv: File[] = [];

actualizarArchivosCv(files: File[]) {
  this.archivosCv = files;
}

procesarCvs() {
  this.candidatosService.subirCvs(this.archivosCv).subscribe({
    next: () => this.cargarCandidatos(),
    error: () => {
      this.errorCarga = 'No se pudieron subir los CVs.';
    },
  });
}
```

## Endpoints Pendientes Sugeridos

### Solicitudes

- `GET /api/solicitudes`
- `GET /api/solicitudes/:id`
- `POST /api/solicitudes`
- `PUT /api/solicitudes/:id`
- `POST /api/solicitudes/:id/cancelar`

### Candidatos

- `GET /api/candidatos`
- `GET /api/candidatos/:id`
- `POST /api/candidatos/cvs`
- `GET /api/candidatos/:id/postulaciones`
- `GET /api/candidatos/:id/experiencia`
- `GET /api/candidatos/:id/estudios`
- `GET /api/candidatos/:id/match`
- `GET /api/candidatos/:id/documentos`
- `POST /api/candidatos/:id/notas`

### Entrevistas

- `GET /api/entrevistas`
- `POST /api/entrevistas`
- `POST /api/entrevistas/masivo`
- `PUT /api/entrevistas/:id/reprogramar`
- `POST /api/entrevistas/:id/cancelar`

## UX Y Accesibilidad

Se han aplicado mejoras pensando en usuarios operativos y usuarios +40:

- Textos más legibles.
- Botones con áreas clickeables cómodas.
- Foco visible para navegación por teclado.
- Estados de carga, error y vacío.
- Tablas con acciones claras.
- Listados con scroll interno cuando pueden crecer mucho.
- Carga de CVs compacta para evitar scroll excesivo.
- Acciones masivas deshabilitadas hasta tener selección.
- Modales con títulos más descriptivos.

## Convenciones Del Proyecto

- Mantener pantallas en `src/app/pages`.
- Mantener componentes reutilizables en `src/app/shared/components`.
- Mantener servicios en `src/app/services`.
- Evitar duplicar tablas por módulo; usar `app-data-table`.
- Evitar duplicar modales base; usar `app-modal`.
- Evitar duplicar cargas de archivos; usar `app-file-dropzone`.
- Usar variables globales para colores, bordes, sombras y estados.
- Mantener estados explícitos: `cargando`, `errorCarga`, vacío y con datos.
- Los componentes compartidos no deben conocer reglas específicas de negocio.

## Ruta De Aprendizaje Recomendada

Para entender y poder construir nuevos módulos, estudiar en este orden:

1. Estructura de una página: `.ts`, `.html`, `.scss`.
2. Variables del `.ts` usadas en el `.html`.
3. `@Input()` y `@Output()`.
4. Cómo importar y llamar componentes reutilizables.
5. Cómo manejar clicks y eventos.
6. Cómo abrir y cerrar modales.
7. Cómo un servicio entrega datos.
8. Cómo consumir APIs con `HttpClient`.
9. Cómo reemplazar datos mock por backend real.
10. Cómo manejar carga, error y vacío.

## Checklist Para Crear Un Nuevo Módulo

1. Crear carpeta en `src/app/pages/nombre-modulo`.
2. Crear componente de listado.
3. Definir modelo o interfaz.
4. Definir columnas de `app-data-table`.
5. Definir filtros.
6. Crear o reutilizar servicio.
7. Agregar ruta en `app.routes.ts`.
8. Agregar opción en el menú si aplica.
9. Conectar estados `cargando`, `errorCarga` y vacío.
10. Conectar acciones individuales y masivas.
11. Compilar con `npm run build`.

## Build

```bash
npm run build
```

La compilación debe terminar sin `ERROR`.

Salida esperada:

```text
Application bundle generation complete.
Output location: Frontend/dist/frontend
```

## Próximos Pasos

- Crear `CandidatosService` real con `HttpClient`.
- Reemplazar mocks del listado de candidatos por `GET /api/candidatos`.
- Conectar carga de CVs con `POST /api/candidatos/cvs`.
- Conectar perfil de candidato con endpoints reales.
- Conectar solicitudes con backend real si aún quedan mocks.
- Conectar entrevistas con endpoints reales.
- Agregar pruebas unitarias a componentes compartidos críticos.
