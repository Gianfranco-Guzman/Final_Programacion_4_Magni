import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.Config.config import get_settings
from app.db.base import create_all_tables
from app.db.seed import populate_seed_data
from app.modules.auth.router import router as auth_router
from app.modules.admin.router import router as admin_router
from app.modules.direcciones.router import router as direcciones_router
from app.modules.productos.router import router as productos_router
from app.modules.categorias.router import router as categoria_router
from app.modules.ingredientes.router import router as ingrediente_router
from app.modules.formas_pago.router import router as formas_pago_router
from app.modules.estadisticas.router import router as estadisticas_router
from app.modules.pedidos.router import router as pedidos_router
from app.modules.pagos.router import router as pagos_router
from app.modules.uploads.router import router as uploads_router

settings = get_settings()


class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start = time.perf_counter()

        async def send_with_timing(message):
            if message["type"] == "http.response.start":
                duration = time.perf_counter() - start
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time", f"{duration:.4f}s".encode()))
                message = {**message, "headers": headers}
                method = scope.get("method", "")
                path = scope.get("path", "")
                print(f"[TIMING] {method} {path} -> {message['status']} ({duration * 1000:.1f}ms)")
            await send(message)

        await self.app(scope, receive, send_with_timing)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Iniciando Food Store API...")
    try:
        create_all_tables()
        print("Tablas creadas")
        populate_seed_data()
        print("Seed data poblado")
    except Exception as e:
        print(f"[AVISO] BD no disponible: {e}")
        print("La app arranca igual — algunos endpoints fallarán hasta que PostgreSQL esté corriendo.")       #sirve para que arranque aunque la base de datos no este disponible
    
    yield
    
    print("Deteniendo Food Store API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API de Food Store con autenticacion JWT",
    lifespan=lifespan,
)

app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
app.include_router(direcciones_router, prefix=settings.api_prefix)
app.include_router(productos_router, prefix=f"{settings.api_prefix}/productos")
app.include_router(categoria_router, prefix=f"{settings.api_prefix}/categorias")
app.include_router(ingrediente_router, prefix=f"{settings.api_prefix}/ingredientes")
app.include_router(formas_pago_router, prefix=f"{settings.api_prefix}/formas-pago")
app.include_router(estadisticas_router, prefix=settings.api_prefix)
app.include_router(pedidos_router, prefix=f"{settings.api_prefix}/pedidos")
app.include_router(pagos_router, prefix=settings.api_prefix)
app.include_router(uploads_router, prefix=settings.api_prefix)


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

