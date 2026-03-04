from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, habitaciones, reservas, pagos, tipos_habitacion, reportes, politicas_cancelacion, configuracion

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="RoyalPalms API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(habitaciones.router, prefix=settings.API_V1_PREFIX)
app.include_router(tipos_habitacion.router, prefix=settings.API_V1_PREFIX)
app.include_router(reservas.router, prefix=settings.API_V1_PREFIX)
app.include_router(pagos.router, prefix=settings.API_V1_PREFIX)
app.include_router(reportes.router, prefix=settings.API_V1_PREFIX)
app.include_router(politicas_cancelacion.router, prefix=settings.API_V1_PREFIX)
app.include_router(configuracion.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def Raiz():
    return {
        "message": "RoyalPalms API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def VerificarSalud():
    return {"status": "ok"}
