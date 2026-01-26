from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, habitaciones, reservas, pagos

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Sistema Web de Reservas de Hotel - API REST"
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
app.include_router(reservas.router, prefix=settings.API_V1_PREFIX)
app.include_router(pagos.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "Sistema de Reservas de Hotel API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
