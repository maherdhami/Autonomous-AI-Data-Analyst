import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.core.firebase import init_firebase
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Setup
setup_cors(app)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, max_requests=120, window_seconds=60)

# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing FastAPI Autonomous AI Data Analyst Server...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_firebase()
    logger.info("Server startup sequence completed.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI server.")

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "error": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
