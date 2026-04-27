from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models
from auth import obtener_usuario_actual, get_db

router = APIRouter(prefix="/ordenes", tags=["ordenes"])


# RUTA PARA CREAR UNA ORDEN
@router.post("/")
def crear_orden(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    items = db.query(models.CarritoItem).filter(models.CarritoItem.usuario_id == usuario_actual.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    try:
        # Calcular el total
        total = 0
        for item in items:
            carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
            total += carta.precio * item.cantidad

        # Crear la orden
        nueva_orden = models.Orden(
            usuario_id=usuario_actual.id,
            fecha=datetime.utcnow().isoformat(),
            total=total
        )
        db.add(nueva_orden)
        db.flush()

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

        # Descontar el stock
        for item in items:
            carta = db.query(models.Carta).filter(models.Carta.id == item.carta_id).first()
            carta.stock -= item.cantidad

        # Limpiar el carrito
        for item in items:
            db.delete(item)

        db.commit()
        return {"mensaje": "Orden creada con éxito", "orden_id": nueva_orden.id, "total": total}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la orden: {str(e)}")


# RUTA PARA VER HISTORIAL DE ÓRDENES
@router.get("/historial/{usuario_id}")
def historial_ordenes(usuario_id: int, pagina: int = 1, por_pagina: int = 20, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if usuario_actual.id != usuario_id and not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este historial")

    offset = (pagina - 1) * por_pagina
    ordenes = db.query(models.Orden).filter(models.Orden.usuario_id == usuario_id).limit(por_pagina).offset(offset).all()
    total_ordenes = db.query(models.Orden).filter(models.Orden.usuario_id == usuario_id).count()

    historial = []
    for orden in ordenes:
        items = db.query(models.OrdenItem).filter(models.OrdenItem.orden_id == orden.id).all()
        historial.append({
            "orden": orden,
            "items": items
        })

    return {
        "historial_ordenes": historial,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": total_ordenes,
        "total_paginas": (total_ordenes + por_pagina - 1) // por_pagina
    }