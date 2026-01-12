"""FastAPI application for product search."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config

from .routes import router

# Create FastAPI application
app = FastAPI(
    title="The Bradery - Product Search API",
    description="API pour la recherche de produits dans le catalogue The Bradery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "message": "The Bradery Product Search API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.API_HOST, 
        port=int(config.API_PORT), 
        reload=config.IS_LOCAL_ENV
    )