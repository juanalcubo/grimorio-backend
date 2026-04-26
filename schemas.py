from pydantic import BaseModel, EmailStr

class CartaSchema(BaseModel):
    nombre: str
    expansion: str
    precio: float
    stock: int
    categoria: str

class CartaActualizarSchema(BaseModel):
    nombre: str | None = None
    expansion: str | None = None
    precio: float | None = None
    stock: int | None = None
    categoria: str | None = None

class UsuarioSchema(BaseModel):
    email: EmailStr
    password: str

class CarritoItemSchema(BaseModel):
    carta_id: int
    cantidad: int

class CambiarPasswordSchema(BaseModel):
    password_actual: str
    password_nueva: str

class CambiarEmailSchema(BaseModel):
    email_nuevo: str    