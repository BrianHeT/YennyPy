# # 📚 YennyPy - Librería Online

YennyPy es una plataforma de comercio electrónico especializada en libros, desarrollada con Flask y PostgreSQL. Permite a los usuarios explorar catálogos, gestionar carritos de compra y realizar compras online con integración de pagos.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Características

- 🔐 **Autenticación completa**: Registro, login con email/password y OAuth con Google
- 📖 **Catálogo de libros**: Navegación por categorías, búsqueda y filtros
- 🛒 **Carrito de compras**: Gestión de productos, cantidades y stock
- 👤 **Perfiles de usuario**: Dashboard personalizado y historial
- 🔧 **Panel de administración**: CRUD completo de libros, gestión de usuarios
- ☁️ **Almacenamiento en la nube**: Integración con AWS S3 para imágenes
- 📱 **Diseño responsive**: Interfaz adaptable a dispositivos móviles y desktop

## 🚀 Demo

[Ver demo en vivo](https://yennypy.onrender.com)

**Credenciales de prueba:**
- Admin: `yenny@yenny.com` / `yenny`
- Usuario: `user@yenny.com` / `yenny`

## 🛠️ Tecnologías

### Backend
- **Flask 3.0.0** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos relacional
- **Flask-Login** - Gestión de sesiones
- **Flask-Bcrypt** - Hash de contraseñas
- **Flask-Migrate** - Migraciones de base de datos

### Frontend
- **Jinja2** - Motor de templates
- **Bootstrap 5** - Framework CSS
- **JavaScript** - Interactividad

### Servicios externos
- **AWS S3** - Almacenamiento de imágenes
- **Google OAuth 2.0** - Autenticación con Google
- **Render** - Hosting y deployment

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Cuenta de AWS con bucket S3 configurado
- Credenciales de Google OAuth (opcional)
- Git

## 🔧 Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/yennypy.git
cd yennypy
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/yennypy

# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_super_segura

# AWS S3
AWS_ACCESS_KEY_ID=tu_access_key_id
AWS_SECRET_ACCESS_KEY=tu_secret_access_key
AWS_REGION=us-east-2
AWS_S3_BUCKET=yennypy-books
S3_UPLOAD_FOLDER=books

# Google OAuth (opcional)
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret
```

### 5. Crear base de datos PostgreSQL

```bash
# Conectarse a PostgreSQL
psql -U postgres

# Crear la base de datos
CREATE DATABASE yennypy;

# Salir
\q
```

### 6. Ejecutar migraciones

```bash
flask db upgrade
```

### 8. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
yennypy/
├── app/
│   ├── blueprints/           # Blueprints de Flask
│   │   ├── auth.py           # Autenticación y OAuth
│   │   ├── books.py          # Gestión de libros
│   │   └── routes_carrito.py # Carrito de compras
│   ├── templates/            # Templates Jinja2
│   │   ├── books/
│   │   ├── carrito/
│   │   ├── errors/
│   │   └── components/
│   ├── static/               # CSS, JS
│   ├── utils/                # Utilidades
│   │   ├── s3.py             # Funciones AWS S3
│   │   └── decorators.py     # Decoradores personalizados
│   ├── __init__.py           # Factory de la aplicación
│   ├── models.py             # Modelos de base de datos
│   └── forms.py              # Formularios WTForms
├── migrations/               # Migraciones de Alembic
├── venv/                     # Entorno virtual
├── .env                      # Variables de entorno (no incluir en git)
├── .gitignore
├── requirements.txt          # Dependencias
├── run.py                    # Punto de entrada
├── reset_db.py               # Script para resetear BD
└── README.md
```

## 🔑 Configuración de Google OAuth

### 1. Crear proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita "Google+ API"

### 2. Configurar OAuth Consent Screen

1. En el menú lateral: **APIs & Services** → **OAuth consent screen**
2. Selecciona **External**
3. Completa la información requerida

### 3. Crear credenciales OAuth 2.0

1. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**
2. Application type: **Web application**
3. Agregar URIs autorizadas:

**Authorized JavaScript origins:**
```
http://localhost:5000
https://tu-app.onrender.com
```

**Authorized redirect URIs:**
```
http://localhost:5000/callback/google
https://tu-app.onrender.com/callback/google
```

4. Copia el **Client ID** y **Client Secret** a tu `.env`

## ☁️ Configuración de AWS S3

### 1. Crear bucket S3

```bash
# Desde AWS CLI
aws s3 mb s3://yennypy-books --region us-east-2
```

O desde la consola web de AWS.

### 2. Configurar política de acceso público

En AWS Console → S3 → tu bucket → Permissions → Bucket Policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::yennypy-books/*"
        }
    ]
}
```

### 3. Crear usuario IAM con permisos S3

1. IAM → Users → Add user
2. Attach policy: `AmazonS3FullAccess`
3. Copia las credenciales al `.env`

## 🚀 Deployment en Render

### 1. Preparar el proyecto

Asegúrate de tener:
- `requirements.txt` actualizado
- `Procfile` (opcional en Render)
- Variables de entorno documentadas

### 2. Crear servicio en Render

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. **New +** → **Web Service**
3. Conecta tu repositorio de GitHub
4. Configuración:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`

### 3. Agregar PostgreSQL

1. **New +** → **PostgreSQL**
2. Copia la URL de conexión
3. En tu Web Service → Environment, agrega `DATABASE_URL`

### 4. Configurar variables de entorno

En Environment, agrega todas las variables del `.env`:

```env
DATABASE_URL=postgresql://...  (Render lo provee automáticamente)
FLASK_ENV=production
SECRET_KEY=genera_una_clave_segura_aqui
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-2
AWS_S3_BUCKET=yennypy-books
S3_UPLOAD_FOLDER=books
```

### 5. Actualizar Google OAuth

Agrega las URIs de producción en Google Cloud Console:

```
https://tu-app.onrender.com
https://tu-app.onrender.com/callback/google
```

### 6. Deploy

Render desplegará automáticamente cada vez que hagas push a tu rama principal.

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/
```

## 📝 Modelos de Base de Datos

### User
- `id`: Primary key
- `name`: Nombre del usuario
- `email`: Email único
- `password_hash`: Contraseña hasheada
- `is_admin`: Permisos de administrador
- `email_verified_at`: Fecha de verificación

### Book
- `id`: Primary key
- `title`: Título del libro
- `author_name`: Nombre del autor
- `price`: Precio
- `quantity`: Stock disponible
- `synopsis`: Descripción
- `image`: URL de la imagen en S3
- `release_date`: Fecha de publicación
- `format`: Formato (físico, digital)
- `editorial`: Editorial

### CartItem
- `id`: Primary key
- `user_id`: FK a User
- `book_id`: FK a Book
- `cantidad`: Cantidad en el carrito

### Genre
- `id`: Primary key
- `name`: Nombre del género

## 👥 Autores

- **Brian He** - *Desarrollo inicial* - [BrianHeT](https://github.com/BrianHeT)
- **Rafael Macias** - *Desarrollo inicial* - [RafaelMaciasT](https://github.com/RafaelMaciasT)
- **Vanesa Olivares** - *Desarrollo inicial* - [Nesviic](https://github.com/Nesviic)
