from fastapi import FastAPI
from .routers import note


def create_app() -> FastAPI:
    app = FastAPI(title="BiliNote")
    app.include_router(note.router, prefix="/api")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.get("/")
    async def root():
        return {"message": "Welcome to BiliNote API"}

    return app
