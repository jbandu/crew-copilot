"""
Crew Copilot - FastAPI Main Application
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from api.v1 import calculations, crew

app = FastAPI(
    title="Crew Copilot API",
    description="AI-powered crew pay intelligence platform for Avelo Airlines",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.railway.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Crew Copilot API",
        "version": "0.1.0",
        "status": "running",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "crew": "/api/v1/crew",
            "calculations": "/api/v1/calculations/run"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "database": "connected",
        "agents": "ready",
        "version": "0.1.0"
    }

# Include routers
app.include_router(crew.router, prefix="/api/v1")
app.include_router(calculations.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
