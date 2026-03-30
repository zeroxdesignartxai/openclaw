from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import query, result, admin


def create_app() -> FastAPI:
    app = FastAPI(title="Direct Answer Engine", version="1.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(query.router_api, prefix="/api")
    app.include_router(result.router, prefix="/api")
    app.include_router(admin.router, prefix="/api/admin")
    return app


app = create_app()
