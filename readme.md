# Grimorio Backend API

Backend de una tienda de cartas TCG desarrollado con FastAPI y Python.

## Tecnologías
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT para autenticación
- Bcrypt para encriptación de contraseñas

## Funcionalidades
- CRUD completo de cartas con categorías (Pokémon, Magic)
- Registro y login de usuarios con contraseñas encriptadas
- Sistema de roles (admin/usuario)
- Carrito de compras
- Sistema de órdenes con transacciones seguras
- Historial de compras paginado
- Cambio de email y contraseña
- Validación de stock al agregar al carrito
- Endpoints de cambio de email y contraseña protegidos por JWT
- Paginación en el historial

## Cómo ejecutar el proyecto

### 1. Instalar dependencias
pip install -r requirements.txt

### 2. Configurar variables de entorno
Crear un archivo .env con:
DATABASE_URL=postgresql://usuario:password@localhost/nombre_db
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

### 3. Ejecutar el servidor
uvicorn main:app --reload

### 4. Ver la documentación
Abrir http://127.0.0.1:8000/docs