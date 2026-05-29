def __getattr__(name: str):
    if name in {"engine", "create_all_tables", "get_session"}:
        from app.db.base import engine, create_all_tables, get_session

        return {
            "engine": engine,
            "create_all_tables": create_all_tables,
            "get_session": get_session,
        }[name]

    if name == "populate_seed_data":
        from app.db.seed import populate_seed_data

        return populate_seed_data

    raise AttributeError(name)


__all__ = ["engine", "create_all_tables", "get_session", "populate_seed_data"]
