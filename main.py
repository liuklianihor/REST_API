from fastapi import FastAPI
from app.api.books import router as books_router


def build_app() -> FastAPI:
    app = FastAPI(title="Library API")
    app.include_router(books_router)

    @app.get("/")
    async def healthcheck():
        return {"message": "Library API is running"}

    return app


app = build_app()
