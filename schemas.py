from pydantic import BaseModel

class CartaSchema(BaseModel):
    nombre: str
    expansion: str
    precio: float
    stock: int
    categoria: str

class UsuarioSchema(BaseModel):
    email: str
    password: str

class CarritoItemSchema(BaseModel):
    carta_id: int
    cantidad: int

class CambiarPasswordSchema(BaseModel):
    password_actual: str
    password_nueva: str

class CambiarEmailSchema(BaseModel):
    email_nuevo: str    