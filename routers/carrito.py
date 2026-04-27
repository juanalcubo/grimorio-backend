from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import CarritoItemSchema
from auth import obtener_usuario_actual, get_db

router = APIRouter(prefix="/carrito", tags=["carrito"])


# ruta para agregar items al carrito
@router.post("/")
def agregar_al_carrito(item: CarritoItemSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
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


# ruta para ver los items del carrito del usuario actual
@router.get("/")
def ver_carrito(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    items = db.query(models.CarritoItem).filter(models.CarritoItem.usuario_id == usuario_actual.id).all()
    total = 0
    carrito_detalle = []
    for item in items:
        carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
        if carta:
            total += carta.precio * item.cantidad
            carrito_detalle.append({
                "id": item.id,
                "carta_id": item.carta_id,
                "nombre": carta.nombre,
                "cantidad": item.cantidad,
                "precio": carta.precio
            })
    return {"carrito": carrito_detalle, "total": total}


# ruta para eliminar items del carrito
@router.delete("/{item_id}")
def eliminar_del_carrito(item_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    item = db.query(models.CarritoItem).filter(
        models.CarritoItem.id == item_id,
        models.CarritoItem.usuario_id == usuario_actual.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito")
    carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
    if carta:
        carta.stock += item.cantidad
    db.delete(item)
    db.commit()
    return {"mensaje": "Ítem eliminado del carrito"}