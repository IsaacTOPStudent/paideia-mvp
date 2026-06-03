# Paideia MVP

Sistema de caracterización de estudiantes con necesidades educativas especiales (NEE), desarrollado como un MVP de microservicios.

##  Visión general

Esta solución está organizada como una plataforma de múltiples servicios:

- `auth-service`: Gestión de autenticación y seguridad.
- `student-service`: Registro y gestión de estudiantes.
- `diagnostic-service`: Gestión de diagnósticos.
- `evaluation-service`: Gestión de evaluaciones.
- `frontend/paideia-frontend`: Interfaz de usuario en Angular.
- `postgres`: Base de datos PostgreSQL.
- `nginx`: Proxy inverso que sirve como gateway.

##  Estructura del repositorio

- `backend/`: Servicios Django independientes.
  - `auth-service/`
  - `student-service/`
  - `diagnostic-service/`
  - `evaluation-service/`
- `frontend/paideia-frontend/`: Aplicación Angular.
- `docker/`: Configuración de Nginx y SSL.
- `scripts/`: Scripts de inicialización de la base de datos.
- `docker-compose.yml`: Orquestación de contenedores.

##  Tecnologías principales

- Django para los microservicios de backend.
- PostgreSQL como base de datos relacional.
- Angular para la aplicación frontend.
- Docker y Docker Compose para la infraestructura local.
- Nginx como gateway/proxy inverso.

##  Requisitos previos

- Docker
- Docker Compose
- Node.js y npm (solo si se usa el frontend localmente sin Docker)

##  Configuración y ejecución

### 1. Crear un archivo `.env`

Debes crear un archivo `.env` en la raíz del proyecto con al menos estas variables:

```env
POSTGRES_DB=paideia_db
POSTGRES_USER=paideia_user
POSTGRES_PASSWORD=paideia_pass
JWT_SECRET=una_clave_secreta
```

> Ajusta los valores según tu entorno.

### 2. Levantar todos los servicios

Desde la raíz del proyecto:

```bash
docker-compose up --build
```

Este comando construye y arranca:

- `postgres`: puerto `5432`
- `auth-service`: puerto `8001`
- `student-service`: puerto `8002`
- `diagnostic-service`: puerto `8003`
- `evaluation-service`: puerto `8004`
- `frontend`: puerto `4200`
- `nginx`: puertos `80` y `443`

### 3. Acceder a la aplicación

- Frontend Angular: `http://localhost:4200`
- API de autenticación: `http://localhost:8001`
- API de estudiantes: `http://localhost:8002`
- API de diagnósticos: `http://localhost:8003`
- API de evaluaciones: `http://localhost:8004`

##  Pruebas

Cada servicio backend usa `pytest` en su carpeta correspondiente. Por ejemplo:

```bash
cd backend/auth-service
pytest
```

### Frontend

```bash
cd frontend/paideia-frontend
npm test
```

##  Desarrollo local del frontend

Si quieres trabajar con Angular localmente sin Docker:

```bash
cd frontend/paideia-frontend
npm install
npm start
```

## 🛠 Comandos útiles

- `docker-compose up --build`: Arranca el sistema completo.
- `docker-compose down`: Detiene los contenedores.
- `docker-compose logs -f`: Ver logs en tiempo real.
- `docker-compose ps`: Ver el estado de los contenedores.

##  Notas importantes

- Los servicios backend se conectan a PostgreSQL mediante la variable `DATABASE_URL` definida en `docker-compose.yml`.
- El frontend se comporta como una aplicación Angular clásica y consume las APIs de los microservicios.
- Nginx actúa de gateway y sirve las conexiones en `80`/`443`.

##  Contribuciones

Si quieres contribuir, puedes:

1. Crear una rama nueva.
2. Añadir o mejorar funcionalidades.
3. Abrir un pull request con descripción clara.

##  Recursos

- `docker-compose.yml`: Orquestación de contenedores.
- `docker/nginx/nginx.conf`: Configuración de gateway.
- Cada `backend/*/Dockerfile`: Construcción de servicio Docker.
- `frontend/paideia-frontend/package.json`: Dependencias y scripts de Angular.

---

Proyecto desarrollado como MVP de caracterización de estudiantes con NEE.
