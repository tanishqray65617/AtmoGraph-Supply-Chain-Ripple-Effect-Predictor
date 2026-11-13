from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import graph, ingest

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AtmoGraph Graph Neural Network & NLP Supply Chain Risk Visualization Engine"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach REST Routers
app.include_router(graph.router, prefix=f"{settings.API_V1_STR}", tags=["Graph Topology"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}", tags=["News Ingestion"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "graph_nodes_loaded": True
    }
