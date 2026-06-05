from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Construction Project Intelligence API",
    description="AI-powered assistant for RFIs, contracts, change orders, blueprints, and site reports.",
    version="0.1.0",
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Construction Project Intelligence Platform API is running",
        "docs": "/docs"
    }
