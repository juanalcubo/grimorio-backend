from fastapi import FastAPI
from database import engine
from dotenv import load_dotenv
import os
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

from routers.cartas import router as cartas_router
from routers.usuarios import router as usuarios_router
from routers.carrito import router as carrito_router
from routers.ordenes import router as ordenes_router

import models

app = FastAPI(title="Grimorio Backend/API")

app.include_router(cartas_router)
app.include_router(usuarios_router)
app.include_router(carrito_router)
app.include_router(ordenes_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

