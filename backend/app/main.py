from fastapi import FastAPI

from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ContaFlow API",
    description="API pentru automatizarea procesării documentelor contabile",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {"status": "online", "message": "API is running", "database": "connected"}
