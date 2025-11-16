"""
Crew Copilot - FastAPI Main Application
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Crew Copilot API",
    description="AI-powered crew pay intelligence platform",
    version="0.1.0"
)

# CORS - allow Railway domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.railway.app",  # Allow Railway subdomains
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
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add real DB check
        "agents": "ready"
    }

# Import routes (add these later)
# from api.v1 import crew, calculations, claims
# app.include_router(crew.router, prefix="/api/v1")
# app.include_router(calculations.router, prefix="/api/v1")
# app.include_router(claims.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
