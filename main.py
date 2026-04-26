from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from schemas import CartaSchema, UsuarioSchema, CarritoItemSchema, CambiarEmailSchema, CambiarPasswordSchema
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI(title="Grimorio Backend/API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Esto es para que la base de datos se conecte y desconecte sola 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar el token JWT

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
# Ruta protegida para obtener el usuario actual a partir del token JWT

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verificar_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario

# RUTA PARA CREAR UNA CARTA y bloqueo para que solo los admins puedan crear cartas
@app.post("/cartas/")
def crear_carta(carta: CartaSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    nueva_carta = models.Carta(nombre=carta.nombre, expansion=carta.expansion, precio=carta.precio, stock=carta.stock, categoria=carta.categoria)
    db.add(nueva_carta)
    db.commit() # Esto guarda los cambios de verdad
    db.refresh(nueva_carta) # Esto actualiza la info con el ID que le puso la DB
    return {"mensaje": "Carta guardada con éxito", "carta": nueva_carta}

# RUTA PARA OBTENER TODAS LAS CARTAS
@app.get("/cartas")
def obtener_cartas(db: Session = Depends(get_db)):
    cartas = db.query(models.Carta).all()
    return {"cartas": cartas}

#ruta para obtener una carta por su ID

@app.get("/cartas/{carta_id}")
def obtener_carta(carta_id: int, db: Session = Depends(get_db)):
    carta = db.query(models.Carta).filter(models.Carta.id == carta_id).first()
    if carta:
        return {"carta": carta}
    else:
        return {"mensaje": "Carta no encontrada"}
    

#ruta para eliminar una carta por su ID

@app.delete("/cartas/{carta_id}")
def eliminar_carta(carta_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    carta = db.query(models.Carta).filter(models.Carta.id == carta_id).first()
    if carta:
        db.delete(carta)
        db.commit()
        return {"mensaje": "Carta eliminada con éxito"}
    else:
        return {"mensaje": "Carta no encontrada"}
    
#ruta para actualizar una carta por su ID

@app.put("/cartas/{carta_id}")
def actualizar_carta(carta_id: int, carta_actualizada: CartaSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")

    carta = db.query(models.Carta).filter(models.Carta.id == carta_id).first()
    if carta:
        carta.nombre = carta_actualizada.nombre
        carta.expansion = carta_actualizada.expansion
        carta.precio = carta_actualizada.precio
        carta.stock = carta_actualizada.stock
        carta.categoria = carta_actualizada.categoria
        db.commit()
        db.refresh(carta)
        return {"mensaje": "Carta actualizada con éxito", "carta": carta}   
    else:
        return {"mensaje": "Carta no encontrada"}
    
# RUTA PARA CREAR UN USUARIO
@app.post("/usuarios/registrar/")
def registrar_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    password_hash = pwd_context.hash(usuario.password)
    nuevo_usuario = models.Usuario(email=usuario.email, password=password_hash)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado, Todo fino", "usuario": nuevo_usuario}

# Función para crear un token JWT

def crear_token(data: dict):
    datos = data.copy()
    expiracion = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos.update({"exp": expiracion})
    token = jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)
    return token

# RUTA PARA INICIAR SESIÓN Y OBTENER UN TOKEN JWT

@app.post("/usuarios/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not db_usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not pwd_context.verify(form_data.password, db_usuario.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    token = crear_token({"sub": db_usuario.email})
    return {"access_token": token, "token_type": "bearer", "usuario_id": db_usuario.id}

    
# RUTA PARA HACER ADMIN A UN USUARIO (SOLO ADMINS PUEDEN HACER ESTO)

@app.put("/usuarios/{usuario_id}/hacer-admin")
def hacer_admin(usuario_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.es_admin = True
    db.commit()
    return {"mensaje": "Usuario ahora es admin"}

#ruta para agregar items al carrito, solo pueden agregar al carrito si tienen un token JWT válido.
    
@app.post("/carrito/")
def agregar_al_carrito(item: CarritoItemSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    carta=db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
    if not carta:
        raise HTTPException(status_code=404, detail="Carta no encontrada")  
    if carta.stock < item.cantidad:
        raise HTTPException(status_code=400, detail="No hay suficiente stock")
    carrito_item = models.CarritoItem(
        usuario_id=usuario_actual.id,
        carta_id=item.carta_id,
    cantidad=item.cantidad
    )
    db.add(carrito_item)
    db.commit()
    db.refresh(carrito_item)
    return {"mensaje": "Ítem agregado al carrito", "item": carrito_item}

#ruta para ver los items del carrito del usuario actual, solo pueden ver su propio carrito gracias al token JWT, aunque eso no debería ser un problema porque el token solo les da acceso a su propio carrito, pero por si las moscas, mejor prevenir que lamentar.
@app.get("/carrito/")
def ver_carrito(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    items = db.query(models.CarritoItem).filter(models.CarritoItem.usuario_id == usuario_actual.id).all()
    total = 0
    for item in items:
        carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
        total += carta.precio * item.cantidad
    carrito_detalle = []
    for item in items:
        carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
        carrito_detalle.append({
            "id": item.id,
            "carta_id": item.carta_id,
            "nombre": carta.nombre,
            "cantidad": item.cantidad,
            "precio": carta.precio
        })

    return {"carrito": carrito_detalle, "total": total}

#borra items del carrito por su ID, pero solo si el item pertenece al usuario actual, para evitar que borren cosas de otros usuarios, aunque eso no debería pasar porque el token JWT solo les da acceso a su propio carrito, pero por si las moscas.
@app.delete("/carrito/{item_id}")
def eliminar_del_carrito(item_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    item = db.query(models.CarritoItem).filter(models.CarritoItem.id == item_id, models.CarritoItem.usuario_id == usuario_actual.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito")
    carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
    if carta:
        carta.stock += item.cantidad
    db.delete(item)
    db.commit()
    return {"mensaje": "Ítem eliminado del carrito"}

@app.post("/ordenes/")
def crear_orden(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    items = db.query(models.CarritoItem).filter(models.CarritoItem.usuario_id == usuario_actual.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")
    
    # Calcular el total
    total = 0
    for item in items:
        carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
        total += carta.precio * item.cantidad
    
    # Crear la orden UNA sola vez
    nueva_orden = models.Orden(
        usuario_id=usuario_actual.id,
        fecha=datetime.utcnow().isoformat(),
        total=total
    )
    db.add(nueva_orden)
    db.commit()
    db.refresh(nueva_orden)

    # Crear los items de la orden
    for item in items:
        carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
        orden_item = models.OrdenItem(
            orden_id=nueva_orden.id,
            carta_id=item.carta_id,
            cantidad=item.cantidad,
            precio_unitario=carta.precio
        )
        db.add(orden_item)

    db.commit()

    # Descontar el stock
    for item in items:
        carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
        carta.stock -= item.cantidad

    # Limpiar el carrito
    for item in items:
        db.delete(item)

    db.commit()

    return {"mensaje": "Orden creada con éxito", "orden_id": nueva_orden.id, "total": total}

@app.get("/history_ordenes/{usuario_id}")
def historial_ordenes(usuario_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
        if usuario_actual.id != usuario_id and not usuario_actual.es_admin:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este historial")
        ordenes = db.query(models.Orden).filter(models.Orden.usuario_id == usuario_id).all()
        historial = []
        for orden in ordenes:
            items = db.query(models.OrdenItem).filter(models.OrdenItem.orden_id == orden.id).all()
            historial.append({
                "orden": orden,
                "items": items
            })
        return {"historial_ordenes": historial}

@app.put("/usuarios/cambiar-password")
def cambiar_password(datos: CambiarPasswordSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not pwd_context.verify(datos.password_actual, usuario_actual.password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    usuario_actual.password = pwd_context.hash(datos.password_nueva)
    db.commit()
    return {"mensaje": "Contraseña actualizada con éxito"}

@app.put("/usuarios/cambiar-email")
def cambiar_email(datos: CambiarEmailSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    email_existente = db.query(models.Usuario).filter(models.Usuario.email == datos.email_nuevo).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="El email ya está en uso")
    usuario_actual.email = datos.email_nuevo
    db.commit()
    return {"mensaje": "Email actualizado con éxito"}

