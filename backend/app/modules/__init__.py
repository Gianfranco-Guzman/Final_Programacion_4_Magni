def __getattr__(name: str):
    if name == "auth_router":
        from app.modules.auth import router as auth_router

        return auth_router
    raise AttributeError(name)


__all__ = ["auth_router"]
