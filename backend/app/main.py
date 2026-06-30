from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ContaFlow API",
    description="API pentru automatizarea procesării documentelor contabile",
    version="1.0.0",
)

app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])


@app.get("/")
def health_check():
    return {"status": "online", "message": "API is running", "database": "connected"}
