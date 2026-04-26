# Grimorio Backend API

Backend de una tienda de cartas TCG Pokémon desarrollado con FastAPI y Python.

## Tecnologías
- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT para autenticación

## Funcionalidades
- CRUD completo de cartas
- Registro y login de usuarios con contraseñas encriptadas
- Sistema de roles (admin/usuario)
- Carrito de compras con control de stock
- Sistema de órdenes
- Historial de compras

## Cómo ejecutar el proyecto

### 1. Instalar dependencias
pip install -r requirements.txt

### 2. Configurar variables de entorno
Crear un archivo .env con:
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

### 3. Ejecutar el servidor
uvicorn main:app --reload

### 4. Ver la documentación
Abrir http://127.0.0.1:8000/docs