from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import CartaSchema, CartaActualizarSchema
from auth import obtener_usuario_actual, get_db

router = APIRouter(prefix="/cartas", tags=["cartas"])


# RUTA PARA CREAR UNA CARTA y bloqueo para que solo los admins puedan crear cartas
@router.post("/")
def crear_carta(carta: CartaSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    nueva_carta = models.Carta(nombre=carta.nombre, expansion=carta.expansion, precio=carta.precio, stock=carta.stock, categoria=carta.categoria)
    db.add(nueva_carta)
    db.commit()
    db.refresh(nueva_carta)
    return {"mensaje": "Carta guardada con éxito", "carta": nueva_carta}


# RUTA PARA OBTENER TODAS LAS CARTAS
@router.get("")
def obtener_cartas(db: Session = Depends(get_db)):
    cartas = db.query(models.Carta).all()
    return {"cartas": cartas}


# ruta para obtener una carta por su ID
@router.get("/{carta_id}")
def obtener_carta(carta_id: int, db: Session = Depends(get_db)):
    carta = db.query(models.Carta).filter(models.Carta.id == carta_id).first()
    if carta:
        return {"carta": carta}
    else:
        return {"mensaje": "Carta no encontrada"}


# ruta para eliminar una carta por su ID
@router.delete("/{carta_id}")
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


# ruta para actualizar una carta por su ID
@router.put("/{carta_id}")
def actualizar_carta(carta_id: int, carta_actualizada: CartaActualizarSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")

    carta = db.query(models.Carta).filter(models.Carta.id == carta_id).first()
    if carta:
        if carta_actualizada.nombre is not None:
            carta.nombre = carta_actualizada.nombre
        if carta_actualizada.expansion is not None:
            carta.expansion = carta_actualizada.expansion
        if carta_actualizada.precio is not None:
            carta.precio = carta_actualizada.precio
        if carta_actualizada.stock is not None:
            carta.stock = carta_actualizada.stock
        if carta_actualizada.categoria is not None:
            carta.categoria = carta_actualizada.categoria
        db.commit()
        db.refresh(carta)
        return {"mensaje": "Carta actualizada con éxito", "carta": carta}
    else:
        return {"mensaje": "Carta no encontrada"}