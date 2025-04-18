from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.auth import router as auth_router

app = FastAPI(
    title="ПВЗ API",
    description="API для сервиса управления ПВЗ и приемкой товаров",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "API работает!"}


# docker-compose exec app alembic revision --autogenerate -m "Initial migration"
# docker-compose exec app alembic upgrade head

# docker-compose exec db psql -U postgres -d pvz_db
