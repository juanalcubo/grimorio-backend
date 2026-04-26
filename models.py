from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base 

class Carta(Base):
    __tablename__ = "cartas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    expansion = Column(String)
    precio = Column(Float)
    stock = Column(Integer)
    categoria = Column(String)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    es_admin = Column(Boolean, default=False)

class CarritoItem(Base):
    __tablename__ = "carrito_items"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    carta_id = Column(Integer)
    cantidad = Column(Integer)

class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    fecha = Column(String)
    total = Column(Float) 

class OrdenItem(Base):
    __tablename__ = "orden_items"

    id= Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer)
    carta_id = Column(Integer)
    cantidad = Column(Integer)
    precio_unitario = Column(Float)