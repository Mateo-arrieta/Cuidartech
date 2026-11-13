🩺 Cuidar-Tech
Sistema Web de Acompañamiento y Trazabilidad del Cuidado de Personas Dependientes
📌 Descripción del Proyecto
Cuidar-Tech es un sistema web diseñado para facilitar el seguimiento, control y acompañamiento del cuidado de personas dependientes. La plataforma permite la interacción entre cuidadores y familiares, mejorando la organización de tareas, el registro de actividades y la comunicación.
Este proyecto se desarrolla en el marco de la asignatura Ingeniería de Software como parte de un trabajo académico orientado a la formulación y evaluación de una solución tecnológica.

🎯 Objetivo General
Desarrollar un sistema web que permita gestionar y monitorear el cuidado de personas dependientes, asegurando trazabilidad en las actividades realizadas y facilitando la comunicación entre los actores involucrados.

👥 Actores del Sistema
Cuidador: Registra actividades, reporta estados y realiza seguimiento.
Familiar: Consulta información, monitorea el cuidado y recibe reportes.

⚙️ Funcionalidades Principales
🔐 Autenticación de usuarios (inicio de sesión)
📋 Registro de actividades de cuidado
📊 Seguimiento y trazabilidad de tareas
👨‍👩‍👧 Visualización de información por parte de familiares
📝 Gestión básica de usuarios

🛠️ Recursos Tecnológicos
El proyecto fue desarrollado utilizando los siguientes recursos tecnológicos:
Python: Lenguaje de programación principal para la lógica del backend.
Django: Framework web utilizado para la gestión de rutas, vistas, modelos y sesiones.
PostgreSQL: Sistema gestor de bases de datos relacional para el almacenamiento de la información.
HTML: Lenguaje encargado de la estructura de las páginas web.
CSS: Lenguaje utilizado para la presentación visual e interfaz del sistema.

🔧 Herramientas de Desarrollo
Visual Studio Code: Entorno de desarrollo utilizado para la implementación del proyecto.
Git: Sistema de control de versiones.
GitHub: Plataforma para la gestión del repositorio y trabajo colaborativo.

📦 Librerías y Dependencias
python-dotenv: Manejo de variables de entorno y protección de datos sensibles.
psycopg2: Conexión entre Django y PostgreSQL.

📧 Servicios Externos
SMTP Gmail: Servicio utilizado para el envío de correos electrónicos (recuperación de contraseña).

---

# 🧩 Trabajo Final: Módulo Gestión de Pacientes (MVC + API REST)

Módulo del sistema que permite al cuidador **registrar, consultar, actualizar y desactivar** a sus pacientes, con validación por tipo de documento, auditoría y una **API REST protegida con token**.

- **Patrón arquitectónico:** MVC con capa de servicios (lógica de negocio) y capa de acceso a datos (repositorios).
- **Patrones de diseño:** Facade, Builder, Strategy, Observer y Repository.
- **Documento de arquitectura:** `docs/Trabajo_Final_Arquitectura_CuidarTech.docx`
- **Documentación de la API (Postman):** `docs/postman/Cuidartech - API Pacientes.postman_collection.json`

## 1. Requisitos

- Python 3.12 o superior
- PostgreSQL
- Git
- Postman (para probar la API)

## 2. Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Mateo-arrieta/Cuidartech.git
cd Cuidartech

# 2. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt
```

4. Crear en PostgreSQL una base de datos llamada **`cuidar_tech`**.
   Por defecto `settings.py` usa usuario `postgres`, contraseña `1234`, servidor `localhost` y puerto `5432`.
   Si tu configuración es distinta, crea un archivo `.env` en la raíz con:
   ```
   DATABASE_URL=postgres://USUARIO:CONTRASEÑA@localhost:5432/cuidar_tech
   ```

```bash
# 5. Crear las tablas
python manage.py migrate
```

## 3. Ejecución

```bash
python manage.py runserver
```

- Web: http://127.0.0.1:8000/
- API: http://127.0.0.1:8000/api/

Para usar el módulo, crea un usuario en http://127.0.0.1:8000/registro/ eligiendo el tipo **Cuidador**. Con ese correo y contraseña se inicia sesión en la web y en la API.

> La recuperación de contraseña por correo necesita `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` en el `.env`. No hace falta para probar el módulo de pacientes.

## 4. API REST

URL base: `http://127.0.0.1:8000/api`

| Método | Ruta | Qué hace | Token | Códigos |
|---|---|---|---|---|
| POST | `/auth/login/` | Entrega el token (correo y contraseña) | No | 200, 401 |
| GET | `/pacientes/` | Lista los pacientes del cuidador | Sí | 200, 401, 403 |
| POST | `/pacientes/` | Registra un paciente | Sí | 201, 400, 401, 409 |
| GET | `/pacientes/<id>/` | Consulta un paciente | Sí | 200, 401, 404 |
| PUT | `/pacientes/<id>/` | Actualiza todos los datos | Sí | 200, 400, 401, 404, 409 |
| DELETE | `/pacientes/<id>/` | Desactiva el paciente (no lo borra) | Sí | 200, 401, 404 |
| GET | `/pacientes/auditoria/` | Historial de acciones | Sí | 200, 401 |

**Seguridad:** después del login, enviar en cada petición la cabecera
`Authorization: Bearer <token>` (el token dura 8 horas).

**Regla de negocio:** cada tipo de documento tiene sus reglas (CC: 6 a 10 dígitos y mayor de edad; TI: 10 u 11 dígitos y menor de edad; CE: 6 o 7 dígitos; PA: 6 a 9 letras y números) y no se puede registrar dos pacientes con el mismo documento (409).

### Cómo probarla en Postman

1. Abrir Postman → **Import** → elegir el archivo de `docs/postman/`.
2. Ejecutar **1. Login** con el correo y contraseña del cuidador (el token se guarda solo).
3. Ejecutar las demás peticiones de la colección.

## 5. Estructura del módulo

```
usuarios/
├── controllers/          → Controlador web (paciente_controller.py)
├── api/                  → Controlador de la API (views.py, urls.py) y seguridad (token)
├── services/pacientes/   → Lógica de negocio: Facade, Builder, Strategy, Observer, PacienteService
├── repositories/         → Capa de acceso a datos (Repository)
└── models/               → Modelo (tablas)
templates/pacientes/      → Vista (páginas HTML)
```