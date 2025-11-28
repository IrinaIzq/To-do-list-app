# 📋 Análisis Completo del Proyecto - To-Do List Manager

**Fecha de Análisis:** Noviembre 28, 2025  
**Autor del Proyecto:** IrinaIzq  
**Rama Principal:** main

---

## 📌 Resumen General

Este es un **aplicación de gestor de tareas (To-Do List Manager)** construida con arquitectura de capas modernas, usando Flask en el backend, SQLite para persistencia de datos, y HTML/CSS/JavaScript en el frontend. El proyecto incluye monitoreo con Prometheus/Grafana, tests automatizados, y deployment con Docker.

**Stack Tecnológico:**
- **Backend:** Python 3.10+ con Flask 3.0.3
- **Base de Datos:** SQLite con SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, JavaScript vanilla
- **Monitoreo:** Prometheus + Grafana
- **Containerización:** Docker & Docker Compose
- **Testing:** Pytest con >70% de cobertura
- **Autenticación:** JWT (JSON Web Tokens)

---

## 🗂️ Estructura del Proyecto

```
To-do-list-app/
├── backend/                    # Código backend Flask
│   ├── app.py                 # Aplicación principal (Factory Pattern)
│   ├── config.py              # Configuración por entorno
│   ├── database.py            # Modelos SQLAlchemy (User, Task, Category)
│   ├── routes.py              # Rutas API con dependencias inyectadas
│   └── services/              # Lógica de negocios (SOLID principles)
│       ├── auth_service.py   # Autenticación y JWT
│       ├── task_service.py   # CRUD de tareas
│       └── category_service.py # CRUD de categorías
├── frontend/                  # Interfaz de usuario
│   ├── index.html            # Estructura HTML
│   ├── scripts.js            # Lógica JavaScript (API calls)
│   └── styles.css            # Estilos CSS
├── tests/                     # Suite de pruebas
│   ├── conftest.py           # Fixtures compartidas (Pytest)
│   ├── test_tasks.py         # Tests unitarios
│   ├── unit/                 # Tests unitarios desagrupados
│   │   ├── test_auth_service.py
│   │   ├── test_task_service.py
│   │   └── test_category_service.py
│   └── integration/          # Tests de integración
│       └── test_api_endpoints.py
├── monitoring/               # Configuración de monitoreo
│   ├── prometheus.yml        # Configuración de Prometheus
│   └── grafana-dashboard.json # Dashboard de Grafana
├── data/                     # Directorio de datos persistentes
├── docs/                     # Documentación
│   ├── Coverage_Report.md    # Reporte de cobertura
│   └── Report Assignment 2.md # Documentación del proyecto
├── htmlcov/                  # Reporte HTML de cobertura
├── docker-compose.yml        # Orquestación de contenedores
├── Dockerfile               # Imagen Docker (multi-stage)
├── requirements.txt         # Dependencias Python
├── requirements-dev.txt     # Dependencias para desarrollo
├── README.md                # Documentación principal
└── LICENSE                  # Licencia del proyecto
```

---

## 📄 Descripción Detallada de Archivos

### **1. BACKEND - Núcleo de la Aplicación**

#### `backend/app.py` (124 líneas)
**Propósito:** Aplicación Flask principal usando el patrón Factory.

**Contenido Principal:**
- Crea la instancia de Flask configurando:
  - Base de datos SQLAlchemy
  - CORS (Cross-Origin Resource Sharing)
  - Métricas Prometheus
  - Servicios inyectados (AuthService, TaskService, CategoryService)
- Inicializa rutas importadas desde `routes.py`
- Maneja la inicialización de extensiones

**Conexiones:**
```
app.py
  ├─→ config.py (carga configuración)
  ├─→ database.py (inicializa db)
  ├─→ routes.py (registra rutas)
  └─→ services/* (inyecta dependencias)
```

---

#### `backend/config.py` (92 líneas)
**Propósito:** Gestión centralizada de configuración por entorno.

**Configuraciones Definidas:**
```python
Config (Base)
├── SECRET_KEY: Para JWT y sesiones
├── DATABASE_URL: sqlite:///tasks.db
├── JWT_EXPIRATION_HOURS: 24
├── CORS_ORIGINS: '*' (en desarrollo)
├── SQLALCHEMY_TRACK_MODIFICATIONS: False
└── APP_VERSION: 2.0.0

DevelopmentConfig (hereda de Config)
├── DEBUG: True
├── TESTING: False
└── SQLALCHEMY_ECHO: True

TestingConfig
├── DEBUG: False
├── TESTING: True
├── SQLALCHEMY_DATABASE_URI: sqlite:///:memory:
└── WTF_CSRF_ENABLED: False

ProductionConfig
├── DEBUG: False
└── (Seguridad reforzada)
```

**Conexiones:**
```
config.py
  └─→ app.py (get_config() es importado y usado)
```

---

#### `backend/database.py` (38 líneas)
**Propósito:** Definición de modelos de datos (ORM).

**Modelos Definidos:**

```python
┌─────────────────────────────────────────────────┐
│                  Category                       │
├─────────────────────────────────────────────────┤
│ id: Integer (PK)                                │
│ name: String(80) - Única, no nula              │
│ description: String(200)                        │
│ tasks: Relación 1-a-Muchos con Task            │
└─────────────────────────────────────────────────┘
            ↓ (1 a Muchos)
┌─────────────────────────────────────────────────┐
│                   Task                          │
├─────────────────────────────────────────────────┤
│ id: Integer (PK)                                │
│ title: String(120) - No nula                   │
│ description: String(250)                        │
│ category_id: Integer (FK) → Category.id        │
│ estimated_hours: Float                          │
│ due_date: String(20)                            │
│ priority: String(20) - Low/Medium/High         │
│ status: String(20) - Pending/In Progress/Done │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                   User                          │
├─────────────────────────────────────────────────┤
│ id: Integer (PK)                                │
│ username: String(80) - Única, no nula          │
│ password_hash: String(128)                      │
│ Métodos:                                        │
│  - set_password(password) : Hashea pwd         │
│  - check_password(pwd) : Verifica pwd hasheado│
└─────────────────────────────────────────────────┘
```

**Características de Seguridad:**
- Contraseñas hasheadas con `werkzeug.security`
- No se almacenan contraseñas en texto plano

**Conexiones:**
```
database.py
  ├─→ Importado por: app.py, routes.py, services/*
  └─→ Usado en: conftest.py para tests
```

---

#### `backend/routes.py` (223 líneas)
**Propósito:** Definición de todos los endpoints API con inyección de dependencias.

**Endpoints Implementados:**

```
AUTENTICACIÓN
├── POST /register
│   ├── Entrada: {username, password}
│   ├── Salida: {message: "User created successfully"} (201)
│   └── Error: 400 si usuario existe
├── POST /login
│   ├── Entrada: {username, password}
│   ├── Salida: {token: "JWT_TOKEN"} (200)
│   └── Error: 401 si credenciales inválidas
└── [Protegidos por @token_required]

CATEGORÍAS (Requieren token)
├── GET /categories
│   └── Retorna: Lista de todas las categorías
├── POST /categories
│   ├── Entrada: {name, description}
│   └── Retorna: Categoría creada (201)
├── GET /categories/<id>
│   └── Retorna: Categoría específica (200)
├── PUT /categories/<id>
│   ├── Entrada: {name, description}
│   └── Retorna: Categoría actualizada (200)
└── DELETE /categories/<id>
    └── Retorna: 204 No Content

TAREAS (Requieren token)
├── GET /tasks
│   └── Retorna: Lista ordenada de tareas
├── POST /tasks
│   ├── Entrada: {title, description, category_id, ...}
│   └── Retorna: Tarea creada (201)
├── GET /tasks/<id>
│   └── Retorna: Tarea específica (200)
├── PUT /tasks/<id>
│   ├── Entrada: {title, status, priority, ...}
│   └── Retorna: Tarea actualizada (200)
├── DELETE /tasks/<id>
│   └── Retorna: 204 No Content
└── GET /tasks/status/<status>
    └── Retorna: Tareas filtradas por estado

SALUD DEL SISTEMA
├── GET /health
│   └── Retorna: {status: "healthy"} (200)
└── GET /metrics
    └── Retorna: Métricas Prometheus
```

**Patrón de Decorador - @token_required:**
```python
Verifica que:
1. El encabezado Authorization exista
2. El formato sea "Bearer <token>"
3. El token sea válido (lo verifica auth_service)
4. Inyecta current_user_id en la función
```

**Conexiones:**
```
routes.py
  ├─→ Importa: AuthService, TaskService, CategoryService
  ├─→ Importa: Excepciones personalizadas
  └─→ Registrado en: app.py como Blueprint
```

---

#### `backend/services/auth_service.py` (134 líneas)
**Propósito:** Lógica de autenticación y gestión de JWT.

**Métodos Principales:**

```python
class AuthService:
    ├── __init__(secret_key, algorithm='HS256', expiration_hours=24)
    │
    ├── register_user(username, password) → User
    │   ├─ Valida username y password no vacíos
    │   ├─ Verifica que usuario no exista
    │   ├─ Hashea la contraseña
    │   └─ Crea nuevo User en BD
    │
    ├── authenticate_user(username, password) → User|None
    │   ├─ Busca user por username
    │   ├─ Verifica contraseña hasheada
    │   └─ Retorna User si es válido, None si no
    │
    ├── generate_token(user_id) → str
    │   ├─ Crea JWT con payload {user_id, exp}
    │   ├─ Exp = ahora + expiration_hours
    │   └─ Codifica con secret_key
    │
    └── verify_token(token) → int|None
        ├─ Decodifica JWT
        ├─ Valida firma y expiración
        ├─ Retorna user_id si válido
        └─ Retorna None si inválido
```

**Características de Seguridad:**
- Tokens con expiración automática (24h por defecto)
- Algoritmo HS256 para JWT
- Excepciones personalizadas: `AuthenticationError`

**Conexiones:**
```
auth_service.py
  ├─→ Importado por: app.py, routes.py
  └─→ Usado en: tests/conftest.py, tests/unit/test_auth_service.py
```

---

#### `backend/services/task_service.py` (275 líneas)
**Propósito:** Lógica de negocios para gestión de tareas.

**Métodos Principales:**

```python
class TaskService:
    VALID_PRIORITIES = ['Low', 'Medium', 'High']
    VALID_STATUSES = ['Pending', 'In Progress', 'Completed']
    
    ├── get_all_tasks() → List[Task]
    │   └─ Ordena por: due_date → priority → estimated_hours
    │
    ├── get_task_by_id(task_id) → Task
    │   ├─ Busca tarea por ID
    │   └─ Lanza: TaskNotFoundError si no existe
    │
    ├── create_task(task_data) → Task
    │   ├─ Valida título, descripción, categoría
    │   ├─ Valida prioridad y estado
    │   ├─ Valida formato de fecha (YYYY-MM-DD)
    │   └─ Crea y persiste en BD
    │
    ├── update_task(task_id, updates) → Task
    │   ├─ Valida datos de actualización
    │   ├─ Actualiza solo campos permitidos
    │   └─ Persiste cambios
    │
    ├── delete_task(task_id) → bool
    │   └─ Elimina tarea de BD
    │
    ├── get_tasks_by_status(status) → List[Task]
    │   ├─ Filtra tareas por estado
    │   └─ Lanza: TaskValidationError si estado inválido
    │
    ├── get_tasks_by_category(category_id) → List[Task]
    │   └─ Retorna tareas de una categoría
    │
    └── to_dict(task) → dict
        └─ Convierte objeto Task a diccionario serializable
```

**Validaciones:**
- Título no puede estar vacío
- Categoría es obligatoria
- Prioridad debe estar en VALID_PRIORITIES
- Estado debe estar en VALID_STATUSES
- Fecha debe tener formato YYYY-MM-DD

**Excepciones Personalizadas:**
- `TaskNotFoundError`: Cuando no existe la tarea
- `TaskValidationError`: Cuando falla validación

**Conexiones:**
```
task_service.py
  ├─→ Importado por: app.py, routes.py
  └─→ Usado en: tests/unit/test_task_service.py
```

---

#### `backend/services/category_service.py` (156 líneas)
**Propósito:** Lógica de negocios para gestión de categorías.

**Métodos Principales:**

```python
class CategoryService:
    ├── get_all_categories() → List[Category]
    │   └─ Retorna todas las categorías
    │
    ├── get_category_by_id(category_id) → Category
    │   ├─ Busca categoría por ID
    │   └─ Lanza: CategoryNotFoundError si no existe
    │
    ├── create_category(category_data) → Category
    │   ├─ Valida nombre (requerido, no vacío)
    │   ├─ Valida unicidad del nombre
    │   └─ Crea y persiste en BD
    │
    ├── update_category(category_id, updates) → Category
    │   ├─ Valida datos de actualización
    │   ├─ Verifica unicidad si nombre cambia
    │   └─ Persiste cambios
    │
    ├── delete_category(category_id) → bool
    │   ├─ Elimina categoría
    │   ├─ Maneja relación con tareas
    │   └─ Retorna True si éxito
    │
    ├── get_categories_with_count() → List[dict]
    │   └─ Retorna categorías con conteo de tareas
    │
    └── to_dict(category) → dict
        └─ Convierte objeto Category a diccionario
```

**Validaciones:**
- Nombre es obligatorio
- Nombre debe ser único en BD
- Descripción es opcional

**Excepciones Personalizadas:**
- `CategoryNotFoundError`: Cuando no existe la categoría
- `CategoryValidationError`: Cuando falla validación

**Conexiones:**
```
category_service.py
  ├─→ Importado por: app.py, routes.py
  └─→ Usado en: tests/unit/test_category_service.py
```

---

### **2. FRONTEND - Interfaz de Usuario**

#### `frontend/index.html` (91 líneas)
**Propósito:** Estructura HTML de la aplicación web.

**Secciones Principales:**

```html
┌─────────────────────────────────────────┐
│           SECCIÓN AUTH                  │
├─────────────────────────────────────────┤
│ ├─ Input: Username                      │
│ ├─ Input: Password                      │
│ ├─ Botón: Login                         │
│ └─ Botón: Register                      │
└─────────────────────────────────────────┘
        ↓ (Oculto hasta login)
┌─────────────────────────────────────────┐
│        SECCIÓN CATEGORÍAS               │
├─────────────────────────────────────────┤
│ ├─ Input: Category Name                 │
│ ├─ Input: Description                   │
│ ├─ Botón: Add Category                  │
│ └─ Div: Lista de categorías             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         SECCIÓN TAREAS                  │
├─────────────────────────────────────────┤
│ ├─ Input: Task Title *                  │
│ ├─ Textarea: Description                │
│ ├─ Input: Category * (requerido)        │
│ ├─ Input: Due Date (date picker)        │
│ ├─ Input: Estimated Hours (number)      │
│ ├─ Select: Priority (Low/Med/High)      │
│ ├─ Botón: Add Task                      │
│ └─ Div: Lista de tareas                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        SECCIÓN FILTROS                  │
├─────────────────────────────────────────┤
│ ├─ Select: Filter by Status             │
│ ├─ Select: Filter by Category           │
│ └─ Botón: Clear Filters                 │
└─────────────────────────────────────────┘
```

**Conexiones:**
```
index.html
  └─→ Vinculado a: scripts.js (onclick handlers)
  └─→ Vinculado a: styles.css (estilos)
```

---

#### `frontend/scripts.js` (442 líneas)
**Propósito:** Lógica JavaScript de cliente, comunicación API.

**Estructura Funcional:**

```javascript
VARIABLES GLOBALES
├── API_URL = "http://127.0.0.1:5000"
└── token = null (almacena JWT)

FUNCIONES DE AUTENTICACIÓN
├── login()
│   ├─ Obtiene username/password del form
│   ├─ POST a /login
│   ├─ Almacena token en variable global
│   ├─ Muestra main-section si éxito
│   └─ Carga categorías y tareas
│
├── register()
│   ├─ Obtiene username/password
│   ├─ POST a /register
│   └─ Alerta de éxito/error
│
└── logout()
    ├─ Limpia token
    ├─ Oculta main-section
    └─ Muestra auth-section

FUNCIONES DE CATEGORÍAS
├── createCategory()
│   ├─ Obtiene name/description del form
│   ├─ POST a /categories con Authorization
│   ├─ Valida que nombre no esté vacío
│   └─ Refresca lista de categorías
│
├── loadCategories()
│   ├─ GET a /categories con Authorization
│   └─ Renderiza lista en DOM
│
├── editCategory(id, name, description)
│   ├─ PUT a /categories/<id>
│   └─ Refresca lista
│
└── deleteCategory(id)
    ├─ DELETE a /categories/<id>
    └─ Refresca lista

FUNCIONES DE TAREAS
├── createTask()
│   ├─ Obtiene todos los campos de form
│   ├─ Valida título y categoría
│   ├─ POST a /tasks con Authorization
│   └─ Refresca lista de tareas
│
├── loadTasks()
│   ├─ GET a /tasks con Authorization
│   └─ Renderiza lista en DOM
│
├── editTask(id, title, status, priority, ...)
│   ├─ PUT a /tasks/<id>
│   └─ Refresca lista
│
├── deleteTask(id)
│   ├─ DELETE a /tasks/<id>
│   └─ Refresca lista
│
├── updateTaskStatus(taskId, newStatus)
│   ├─ Actualiza estado de tarea
│   └─ Refresca vista
│
└── filterTasks(status, category)
    ├─ Filtra tareas en frontend
    ├─ O filtra en backend si se implementa
    └─ Refresca vista

MANEJO DE ERRORES
├── Try-catch en cada función
├── Alertas de error al usuario
├── Logging en consola para debugging
└── Validación de respuestas HTTP
```

**Características:**
- Event listeners globales para prevenir reloads
- Headers con Authorization: `Bearer <token>`
- Manejo de errores HTTP con status codes
- Logging en consola para debugging
- Validación de campos en cliente

**Conexiones:**
```
scripts.js
  ├─→ Llamadas a API en: backend/routes.py
  └─→ Manipula DOM de: index.html
```

---

#### `frontend/styles.css` (Generalmente no mostrado)
**Propósito:** Estilos visuales de la aplicación.

**Elementos Estilizados (típicamente):**
```css
- app-title: Título principal
- auth-section: Formulario de login/registro
- main-section: Área principal (oculta hasta login)
- section: Contenedores de categorías y tareas
- input, textarea, select, button: Elementos de formulario
- task-item, category-item: Items en listas
- logout-btn: Botón de logout
- Responsividad y disposición en flexbox/grid
```

---

### **3. TESTING - Suite de Pruebas**

#### `tests/conftest.py` (176 líneas)
**Propósito:** Configuración de Pytest y fixtures compartidas.

**Fixtures Definidas:**

```python
Fixtures de Aplicación:
├── app()
│   ├─ Crea aplicación en modo testing
│   ├─ Crea tablas en BD de prueba
│   ├─ Limpia BD después de cada test
│   └─ Scope: function (nueva para cada test)
│
├── client(app)
│   └─ Cliente test para hacer requests HTTP
│
└── runner(app)
    └─ CLI runner para comandos de aplicación

Fixtures de Servicios:
├── auth_service(app)
│   └─ Instancia de AuthService para tests
├── task_service(app)
│   └─ Instancia de TaskService para tests
└── category_service(app)
    └─ Instancia de CategoryService para tests

Fixtures de Datos:
├── test_user(app, auth_service)
│   ├─ Crea usuario de prueba
│   └─ Retorna: {id, username, password}
│
├── auth_token(app, auth_service, test_user)
│   └─ Genera JWT válido para test_user
│
├── auth_headers(auth_token)
│   └─ Retorna: {'Authorization': 'Bearer <token>'}
│
└── test_category(app, category_service)
    └─ Crea categoría de prueba
```

**Configuración de Pytest:**
```python
- sys.path.insert(): Agrega backend al path
- pytest.fixture: Marca las funciones como fixtures
- scope='function': Nueva instancia por test
- app.app_context(): Contexto para operaciones BD
```

**Conexiones:**
```
conftest.py
  ├─→ Importado automáticamente por Pytest
  ├─→ Usado en: tests/unit/*.py
  └─→ Usado en: tests/integration/test_api_endpoints.py
```

---

#### `tests/test_tasks.py` (266 líneas)
**Propósito:** Tests unitarios principales.

**Clase Principal: TestToDoApp**

```python
Métodos de Configuración:
├── setUpClass()
│   ├─ Crea aplicación una vez para todos los tests
│   ├─ Configura BD en memoria
│   └─ Crea cliente test
│
├── setUp()
│   ├─ Crea BD antes de cada test
│   ├─ Crea usuario de prueba
│   └─ Genera token de autenticación
│
└── tearDown()
    ├─ Limpia sesión BD
    └─ Elimina todas las tablas

Tests de Autenticación:
├── test_register_user_success()
├── test_register_duplicate_user()
├── test_login_success()
└── test_login_invalid_credentials()

Tests de Categorías:
├── test_create_category()
├── test_get_categories()
├── test_update_category()
└── test_delete_category()

Tests de Tareas:
├── test_create_task()
├── test_get_tasks()
├── test_update_task()
├── test_delete_task()
├── test_task_validation()
└── test_task_sorting()

Métodos Auxiliares:
├── register_user(username, password)
│   └─ POST /register
│
└── login_user(username, password)
    └─ POST /login y retorna token
```

**Cobertura de Casos:**
- Happy path (casos exitosos)
- Error cases (validaciones, datos inválidos)
- Edge cases (valores límite, campos vacíos)
- Status codes HTTP correctos
- Estructura de respuestas JSON

**Conexiones:**
```
test_tasks.py
  ├─→ Importa: conftest.py (fixtures)
  └─→ Prueba: app.py, routes.py, services/*
```

---

#### `tests/unit/test_auth_service.py`
**Propósito:** Tests unitarios del servicio de autenticación.

**Tests Típicos:**
```
- test_register_new_user()
- test_register_missing_username()
- test_register_missing_password()
- test_register_duplicate_user()
- test_authenticate_valid_user()
- test_authenticate_invalid_password()
- test_authenticate_nonexistent_user()
- test_generate_token()
- test_verify_token_valid()
- test_verify_token_expired()
- test_verify_token_invalid_signature()
```

---

#### `tests/unit/test_task_service.py`
**Propósito:** Tests unitarios del servicio de tareas.

**Tests Típicos:**
```
- test_create_task_success()
- test_create_task_missing_title()
- test_create_task_invalid_priority()
- test_create_task_invalid_status()
- test_get_all_tasks_sorted()
- test_get_task_by_id_success()
- test_get_task_by_id_not_found()
- test_update_task_success()
- test_delete_task_success()
- test_get_tasks_by_status()
- test_get_tasks_by_category()
```

---

#### `tests/unit/test_category_service.py`
**Propósito:** Tests unitarios del servicio de categorías.

**Tests Típicos:**
```
- test_create_category_success()
- test_create_category_missing_name()
- test_create_category_duplicate_name()
- test_get_all_categories()
- test_get_category_by_id()
- test_get_category_by_id_not_found()
- test_update_category_success()
- test_delete_category_success()
- test_get_categories_with_count()
```

---

#### `tests/integration/test_api_endpoints.py` (327 líneas)
**Propósito:** Tests de integración de endpoints API.

**Grupos de Tests:**

```python
TestAuthenticationEndpoints
├── test_register_and_login_flow()
│   └─ Flujo completo: registro → login → token
├── test_login_with_invalid_credentials()
│   └─ Verifica manejo de credenciales incorrectas
├── test_access_protected_endpoint_without_token()
│   └─ Verifica que endpoints requieran token
└── test_access_with_invalid_token()
    └─ Verifica manejo de tokens malformados

TestCategoryEndpoints
├── test_create_category_with_auth()
├── test_list_categories_with_auth()
├── test_get_single_category()
├── test_update_category()
└── test_delete_category()

TestTaskEndpoints
├── test_create_task_complete_flow()
├── test_list_tasks_with_sorting()
├── test_get_single_task()
├── test_update_task_status()
├── test_delete_task()
├── test_filter_tasks_by_status()
├── test_filter_tasks_by_category()
└── test_task_validation_errors()

TestErrorHandling
├── test_404_not_found()
├── test_400_bad_request()
├── test_500_server_error()
└── test_invalid_json()
```

---

### **4. CONFIGURACIÓN Y DEPLOYMENT**

#### `docker-compose.yml` (74 líneas)
**Propósito:** Orquestación de servicios con Docker Compose.

**Servicios Definidos:**

```yaml
app (Flask Backend):
├── Build: Dockerfile local
├── Container name: todo-app
├── Ports: 5000:5000 (Flask)
├── Environment Variables:
│   ├─ FLASK_ENV: production
│   ├─ SECRET_KEY: ${SECRET_KEY}
│   ├─ DATABASE_URL: sqlite:///data/tasks.db
│   ├─ JWT_EXPIRATION_HOURS: 24
│   └─ CORS_ORIGINS: *
├── Volumes: ./data:/app/data (persistencia)
├── Network: app-network
├── Restart: unless-stopped
└── Healthcheck: curl http://localhost:5000/health

prometheus (Monitoring):
├── Image: prom/prometheus:latest
├── Container name: prometheus
├── Ports: 9090:9090
├── Volumes: ./monitoring/prometheus.yml
├── Targets: app:5000 (scraping)
├── Network: app-network
└── Depends on: app

grafana (Visualization):
├── Image: grafana/grafana:latest
├── Container name: grafana
├── Ports: 3000:3000
├── Environment: GF_SECURITY_ADMIN_PASSWORD
├── Volumes: grafana-storage
├── Data Sources: Prometheus
├── Network: app-network
└── Depends on: prometheus

Volumes Persistentes:
├── prometheus-data
└── grafana-storage

Networks:
└── app-network (bridge)
```

**Flujo de Inicio:**
```
docker-compose up -d
  ├─→ Construye imagen de app (Dockerfile)
  ├─→ Inicia contenedor app
  ├─→ Espera healthcheck OK
  ├─→ Inicia Prometheus (depende de app)
  ├─→ Inicia Grafana (depende de Prometheus)
  └─→ Todos conectados en app-network
```

---

#### `Dockerfile` (56 líneas)
**Propósito:** Imagen Docker multi-stage para optimización.

**Etapas:**

```dockerfile
STAGE 1: base
├── FROM python:3.10-slim
├── Set environment variables (PYTHONDONTWRITEBYTECODE, etc)
├── Install system dependencies (gcc, curl)
└── Create /app directory

STAGE 2: dependencies
├── Copy requirements.txt
├── Install Python packages
└── Result: Base con dependencias

STAGE 3: application
├── Copy código del proyecto
├── Expose puerto 5000
├── Set ENTRYPOINT a gunicorn
└── Result: Imagen final lista para producción
```

**Variables de Entorno:**
```dockerfile
PYTHONDONTWRITEBYTECODE=1    # No crea .pyc
PYTHONUNBUFFERED=1           # Stderr en tiempo real
PIP_NO_CACHE_DIR=1           # Reduce tamaño
PIP_DISABLE_PIP_VERSION_CHECK=1
```

---

#### `requirements.txt` (12 líneas)
**Propósito:** Dependencias de producción.

```python
Dependencias Principales:
├── Flask==3.0.3              # Web framework
├── Flask-SQLAlchemy==3.1.1  # ORM
├── Flask-CORS==4.0.0        # CORS headers
├── PyJWT==2.8.0             # JWT tokens
├── Werkzeug==3.0.1          # Utilities
├── python-dotenv==1.0.0     # Env variables
├── prometheus-flask-exporter==0.22.4  # Metrics
├── requests==2.31.0         # HTTP library
└── SQLAlchemy==2.0.31       # Database

Total de dependencias: 12 paquetes
```

---

#### `monitoring/prometheus.yml`
**Propósito:** Configuración de recopilación de métricas.

```yaml
global:
├── scrape_interval: 15s  # Recopila cada 15 segundos
├── evaluation_interval: 15s
└── external_labels: monitor='todo-monitor'

scrape_configs:
└── job_name: 'flask_app'
    ├── static_configs:
    │   └── targets: ['app:5000']
    └── metrics_path: '/metrics'
```

**Métricas Recopiladas:**
- http_requests_total
- http_request_duration_seconds
- app_info (versión, etc)
- Métricas custom de TaskService

---

#### `monitoring/grafana-dashboard.json`
**Propósito:** Dashboard visual en Grafana.

**Visualizaciones Típicas:**
```
Paneles:
├── Requests por segundo (línea)
├── Latencia promedio (gauge)
├── Errores por minuto (gráfica)
├── Uptime del aplicación (stat)
├── Request rate por endpoint (barra)
├── Distribución de status codes (pie)
└── Histograma de tiempos de respuesta
```

---

### **5. DOCUMENTACIÓN**

#### `README.md`
**Propósito:** Documentación principal del proyecto.

**Secciones:**
```
- Descripción general
- Features principales
- Prerequisites
- Quick Start (Docker)
- Development Setup
- Testing
- Docker Deployment
- CI/CD Pipeline
- Monitoring
- API Documentation
- Architecture
- SOLID Principles Implementation
```

---

## 🔄 Flujos de Interacción Entre Componentes

### **Flujo 1: Autenticación y Login**

```
USUARIO en Frontend
  │
  └─→ HTML: Ingresa username/password
      │
      └─→ scripts.js: login()
          │
          └─→ POST /login con {username, password}
              │
              ├─→ routes.py: @routes.route("/login")
              │   │
              │   ├─→ auth_service.authenticate_user(username, pwd)
              │   │   │
              │   │   ├─→ database.py: User.query.filter_by(username)
              │   │   │
              │   │   └─→ user.check_password(password)
              │   │
              │   ├─→ auth_service.generate_token(user.id)
              │   │   │
              │   │   └─→ jwt.encode(payload, secret_key)
              │   │
              │   └─→ return JSON: {token: "JWT_TOKEN"}
              │
              └─→ scripts.js: Almacena token en variable global
                  │
                  └─→ Muestra main-section y carga tareas
```

---

### **Flujo 2: Crear Tarea**

```
USUARIO en Frontend
  │
  └─→ HTML: Completa formulario de tarea
      │
      └─→ scripts.js: createTask()
          │
          ├─→ Valida: título y categoría requeridos
          │
          └─→ POST /tasks con Authorization: Bearer <token>
              │
              ├─→ routes.py: @token_required decorator
              │   │
              │   └─→ auth_service.verify_token(token)
              │       ├─→ jwt.decode(token, secret_key)
              │       └─→ Retorna user_id
              │
              ├─→ routes.py: @routes.route("/tasks", methods=["POST"])
              │   │
              │   ├─→ task_service.create_task(data)
              │   │   │
              │   │   ├─→ Valida: title, category_id, priority, status
              │   │   │
              │   │   ├─→ category_service.get_category_by_id(cat_id)
              │   │   │   └─→ Verifica que categoría exista
              │   │   │
              │   │   ├─→ database.py: Task(title=..., ...)
              │   │   │
              │   │   ├─→ db.session.add(task)
              │   │   │
              │   │   └─→ db.session.commit()
              │   │
              │   └─→ return JSON: {id, title, ...} (201)
              │
              └─→ scripts.js: loadTasks() para refrescar vista
                  │
                  └─→ Renderiza nueva tarea en DOM
```

---

### **Flujo 3: Testing**

```
DESARROLLADOR ejecuta: pytest
  │
  ├─→ Pytest carga conftest.py
  │   │
  │   └─→ Fixtures creadas:
  │       ├─ app (nuevo por test)
  │       ├─ client (test client)
  │       ├─ auth_service
  │       ├─ task_service
  │       ├─ test_user
  │       ├─ auth_token
  │       └─ auth_headers
  │
  ├─→ Ejecuta test_tasks.py o tests/integration/*
  │   │
  │   ├─→ Cada test:
  │   │   ├─ setUp(): Crea BD en memoria
  │   │   ├─ test_xxx(): Ejecuta test específico
  │   │   ├─ tearDown(): Limpia BD
  │   │   └─ Reporta resultado
  │   │
  │   └─→ Coverage >70% de código
  │
  └─→ Genera reporte en htmlcov/
      └─→ Muestra líneas ejecutadas y no ejecutadas
```

---

### **Flujo 4: Docker Deployment**

```
USUARIO ejecuta: docker-compose up -d
  │
  ├─→ Docker build Dockerfile
  │   ├─ Stage 1 (base): python:3.10-slim
  │   ├─ Stage 2 (dependencies): pip install
  │   └─ Stage 3 (application): app lista
  │
  ├─→ Inicia contenedor 'app'
  │   ├─ Puerto 5000:5000
  │   ├─ Volumen ./data:/app/data
  │   └─ Healthcheck: curl /health
  │
  ├─→ Inicia Prometheus
  │   └─ Scrape app:5000/metrics cada 15s
  │
  ├─→ Inicia Grafana
  │   └─ Conecta a Prometheus como data source
  │
  └─→ Todos en red 'app-network'
      └─→ Pueden comunicarse por nombre de servicio
```

---

## 🏗️ Principios de Arquitectura Implementados

### **1. SOLID Principles**

```
S - Single Responsibility Principle
  ├─ AuthService: Solo autenticación
  ├─ TaskService: Solo gestión de tareas
  ├─ CategoryService: Solo gestión de categorías
  └─ routes.py: Solo define endpoints (delega en services)

O - Open/Closed Principle
  ├─ Servicios abiertos a extensión (heredancia)
  └─ Cerrados a modificación (interfaces estables)

L - Liskov Substitution Principle
  └─ Servicios son intercambiables

I - Interface Segregation Principle
  ├─ Cada servicio tiene interfaz específica
  └─ No métodos no usados

D - Dependency Inversion Principle
  ├─ routes.py recibe servicios inyectados
  ├─ app.py inyecta dependencias
  └─ Bajo acoplamiento entre módulos
```

---

### **2. Patrón Factory (app.py)**

```
create_app(config_name)
  ├─ Crea instancia de Flask
  ├─ Configura por entorno
  ├─ Inicializa extensiones
  ├─ Inyecta servicios
  └─ Retorna app configurada
```

---

### **3. Inyección de Dependencias**

```
routes.py recibe:
  ├─ auth_service: AuthService
  ├─ task_service: TaskService
  └─ category_service: CategoryService

Sin necesidad de:
  └─ Importar directamente
  └─ Crear instancias
```

---

### **4. Separación de Capas**

```
PRESENTACIÓN (Frontend)
  ├─ index.html (estructura)
  ├─ styles.css (estilos)
  └─ scripts.js (lógica cliente)
         ↓ HTTP/JSON
CONTROLADORES (routes.py)
         ↓ Métodos
SERVICIOS (services/*)
         ↓ ORM
BASE DE DATOS (database.py)
         ↓ SQLite
DATA PERSISTENCE (tasks.db)
```

---

### **5. Manejo de Excepciones**

```
Excepciones Personalizadas:
├─ AuthenticationError
├─ TaskNotFoundError
├─ TaskValidationError
├─ CategoryNotFoundError
└─ CategoryValidationError

Uso en:
├─ services/ (levanta excepciones)
└─ routes.py (captura y convierte a JSON)
```

---

## 📊 Comparativa: Conexiones Entre Archivos

```
                    ┌─────────────────┐
                    │    index.html   │ (frontend UI)
                    └────────┬────────┘
                             │ (onclick handlers)
                             │
                    ┌────────▼────────┐
                    │  scripts.js     │ (fetch API)
                    └────────┬────────┘
                             │ (HTTP/JSON)
                    ┌────────▼────────┐
                    │  routes.py      │ (endpoints)
                    └────────┬────────┘
                    │        │        │
        ┌───────────┼───────┼───────┬┘
        │           │       │       │
   ┌────▼───┐  ┌────▼──┐  ┌─▼──────┴─────┐
   │ auth_  │  │ task_ │  │  category_   │
   │service │  │service│  │   service    │
   └────┬───┘  └────┬──┘  └─┬────────────┘
        │           │       │
        └───────────┼───────┘
                    │
              ┌─────▼──────┐
              │ database.py│ (models)
              │  (ORM)     │
              └─────┬──────┘
                    │
              ┌─────▼──────┐
              │  SQLite    │
              │ (tasks.db) │
              └────────────┘


TESTING:
         ┌──────────────┐
         │ conftest.py  │ (fixtures)
         └──────┬───────┘
                │
        ┌───────┼───────┐
        │       │       │
   ┌────▼──┐ ┌──▼───┐ ┌─▼────────────────┐
   │ test_ │ │ test_│ │ test_api_        │
   │ tasks │ │unit/ │ │ endpoints.py     │
   └───────┘ └──────┘ └──────────────────┘
```

---

## 📈 Diagrama de Flujo Completo

```
┌──────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Frontend Browser  │
                    │  (HTML/CSS/JS)     │
                    └─────────┬──────────┘
                              │
              ┌───────────────┴───────────────┐
              │     HTTP/REST API            │
              │   (JSON Payloads)            │
              │                              │
         ┌────▼─────┬────────────┬──────────┴──┐
         │           │            │             │
    ┌────▼────┐ ┌────▼─────┐ ┌───▼────┐ ┌──────▼──┐
    │ /login  │ │/register │ │/tasks  │ │/categor.│
    │ /logout │ │          │ │/categ. │ │         │
    │ /health │ │          │ │        │ │         │
    └────┬────┘ └────┬─────┘ └───┬────┘ └──────┬──┘
         │           │           │             │
    ┌────▼───────────▼───────────▼─────────────▼────┐
    │              FLASK APP (app.py)                │
    │              • CORS enabled                    │
    │              • Prometheus metrics              │
    │              • DI container                    │
    └────┬───────────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────────┐
    │          ROUTE HANDLERS (routes.py)          │
    │  • @token_required decorator                 │
    │  • Dependency injection                      │
    │  • Error handling                            │
    └─┬──────────────┬────────────────┬────────────┘
      │              │                │
   ┌──▼──┐  ┌───────▼───────┐  ┌─────▼────────┐
   │Auth │  │    Task       │  │   Category   │
   │Serv.│  │   Service     │  │   Service    │
   │     │  │               │  │              │
   │     │  │               │  │              │
   └──┬──┘  └────────┬──────┘  └──────┬───────┘
      │              │                 │
      └──────────────┼─────────────────┘
                     │
        ┌────────────▼──────────────┐
        │   DATABASE LAYER (ORM)    │
        │  • SQLAlchemy             │
        │  • Models:                │
        │    - User                 │
        │    - Task                 │
        │    - Category             │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │   SQLITE DATABASE         │
        │   tasks.db                │
        │                           │
        │  [PERSISTENT STORAGE]     │
        └───────────────────────────┘


MONITORING (Containerizado):
         ┌──────────────┐
         │  Prometheus  │
         │  :9090       │
         └──────┬───────┘
                │ (scrapes)
         ┌──────▼───────┐
         │  Flask App   │
         │  /metrics    │
         └──────────────┘
                │
         ┌──────▼───────┐
         │   Grafana    │
         │   :3000      │
         │   Dashboard  │
         └──────────────┘
```

---

## 🧪 Cobertura de Tests

```
Archivos Testeados:
├── backend/app.py                    ✓ >80%
├── backend/routes.py                 ✓ >85%
├── backend/services/auth_service.py  ✓ >90%
├── backend/services/task_service.py  ✓ >85%
├── backend/services/category_service.py ✓ >85%
├── backend/database.py               ✓ >70%

Casos de Test:
├── Unit Tests: servicios aislados
├── Integration Tests: flujos completos
├── Edge Cases: validaciones
└── Error Handling: excepciones

TOTAL COVERAGE: >70% ✓ (Objetivo cumplido)
```

---

## 🚀 Stack de Tecnologías

```
BACKEND
├─ Python 3.10+
├─ Flask 3.0.3
├─ SQLAlchemy 2.0.31
├─ PyJWT 2.8.0
├─ Werkzeug 3.0.1
└─ prometheus-flask-exporter

FRONTEND
├─ HTML5
├─ CSS3
├─ JavaScript (Vanilla)
└─ Fetch API

DATABASE
├─ SQLite (desarrollo)
├─ Persistencia en ./data/tasks.db
└─ ORM: SQLAlchemy

TESTING
├─ Pytest
├─ unittest
├─ Coverage >70%
└─ conftest.py (fixtures)

DEPLOYMENT
├─ Docker
├─ Docker Compose
├─ Python 3.10-slim image
├─ Multi-stage build
└─ Healthchecks

MONITORING
├─ Prometheus
├─ Grafana
├─ prometheus-flask-exporter
└─ Custom metrics
```

---

## 📝 Resumen Ejecutivo

### **¿Qué hace el proyecto?**
Es una aplicación web de gestión de tareas con autenticación JWT, permitiendo a los usuarios crear, actualizar, eliminar y organizar tareas en categorías.

### **¿Cómo está estructurado?**
Sigue arquitectura de capas (MVC-like) con servicios de negocio, inyección de dependencias y principios SOLID.

### **¿Cómo se comunican los componentes?**
- Frontend → Backend vía HTTP REST con JSON
- Backend → BD vía ORM SQLAlchemy
- Monitoreo recolecta métricas de Flask
- Docker Compose orquesta todos los servicios

### **¿Cuáles son las características principales?**
✓ Autenticación JWT
✓ CRUD completo de tareas y categorías
✓ Monitoreo con Prometheus/Grafana
✓ Tests automatizados (>70% cobertura)
✓ Deployment containerizado
✓ SOLID Principles y Clean Code
✓ API REST RESTful
✓ Manejo robusto de errores

---

## 🎯 Conclusión

Este proyecto es una **aplicación profesional de gestión de tareas** bien estructurada, con:
- ✅ Arquitectura modular y escalable
- ✅ Código limpio y mantenible
- ✅ Buenas prácticas de DevOps
- ✅ Tests automatizados
- ✅ Monitoreo en producción
- ✅ Documentación completa
- ✅ Fácil de deployar con Docker

Es un **excelente ejemplo** de una aplicación web moderna siguiendo estándares de la industria.

