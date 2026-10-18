
from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.routes.investigate import router as investigate_router
import httpx
from app.database import Base, engine
import app.models

app = FastAPI(
    title="SRE Logs Agent",
    description="AI-powered application log analysis and incident investigation",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)
app.include_router(upload_router)
app.include_router(investigate_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "SRE Logs Agent"
    }

@app.get("/health/ollama", tags=["Health"])
async def ollama_health_check():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get("http://localhost:11434/api/tags")

        if response.status_code == 200:
            return {"status": "healthy", "service": "Ollama"}

        return {"status": "unhealthy", "service": "Ollama"}

    except httpx.RequestError:
        return {"status": "unhealthy", "service": "Ollama"}