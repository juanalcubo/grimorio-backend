from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import models
from schemas import UsuarioSchema, CambiarEmailSchema, CambiarPasswordSchema
from auth import pwd_context, obtener_usuario_actual, crear_token, get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# RUTA PARA CREAR UN USUARIO
@router.post("/registrar/")
def registrar_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    password_hash = pwd_context.hash(usuario.password)
    nuevo_usuario = models.Usuario(email=usuario.email, password=password_hash)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado exitosamente!", "usuario": nuevo_usuario}


# RUTA PARA INICIAR SESIÓN Y OBTENER UN TOKEN JWT
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    if not db_usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not pwd_context.verify(form_data.password, db_usuario.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    token = crear_token({"sub": db_usuario.email, "usuario_id": db_usuario.id})
    return {"access_token": token, "token_type": "bearer", "usuario_id": db_usuario.id}


# RUTA PARA HACER ADMIN A UN USUARIO (SOLO ADMINS PUEDEN HACER ESTO)
@router.put("/{usuario_id}/hacer-admin")
def hacer_admin(usuario_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not usuario_actual.es_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.es_admin = True
    db.commit()
    return {"mensaje": "Usuario ahora es admin"}


# RUTA PARA CAMBIAR PASSWORD
@router.put("/cambiar-password")
def cambiar_password(datos: CambiarPasswordSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    if not pwd_context.verify(datos.password_actual, usuario_actual.password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    usuario_actual.password = pwd_context.hash(datos.password_nueva)
    db.commit()
    return {"mensaje": "Contraseña actualizada con éxito"}


# RUTA PARA CAMBIAR EMAIL
@router.put("/cambiar-email")
def cambiar_email(datos: CambiarEmailSchema, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    email_existente = db.query(models.Usuario).filter(models.Usuario.email == datos.email_nuevo).first()
    if email_existente:
        raise HTTPException(status_code=400, detail="El email ya está en uso")
    usuario_actual.email = datos.email_nuevo
    db.commit()
    return {"mensaje": "Email actualizado con éxito"}