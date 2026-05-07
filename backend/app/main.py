from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.base import create_all_tables
from app.db.seed import populate_seed_data
from app.modules.auth import router as auth_router
from app.modules.productos import router as productos_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Iniciando Food Store API...")
    create_all_tables()
    print("Tablas creadas")
    populate_seed_data()
    
    yield
    
    # Shutdown
    print("Deteniendo Food Store API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API de Food Store con autenticacion JWT",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(productos_router, prefix=f"{settings.api_prefix}/productos")


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Food Store API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

