from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
import time

from app.config import config
from app.routes import query_routes, schema_routes

from app.logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Sync ChromaDB schema from live SQLite on every startup."""
    print("\n" + "="*55)
    print("  🚀  Text-to-SQL backend starting up...")
    print("="*55)
    logger.info("=== SERVER STARTUP: Syncing ChromaDB schema from SQLite ===")
    print("  ⏳  Syncing ChromaDB schema from SQLite...")
    try:
        from app.vectorstore.vectordb import sync_tables_to_schema
        synced = sync_tables_to_schema()
        logger.info(f"=== Startup sync complete: {synced} table(s) upserted into ChromaDB ===")
        print(f"  ✅  Schema sync complete — {synced} table(s) ready.")
    except Exception as e:
        logger.warning(f"=== Startup schema sync failed (non-fatal): {e} ===")
        print(f"  ⚠️  Schema sync failed (non-fatal): {e}")
    print("  🌐  API live at http://localhost:8000")
    print("  📖  Docs at    http://localhost:8000/docs")
    print("="*55 + "\n")
    yield  # server runs
    print("\n" + "="*55)
    print("  🛑  Server shut down.")
    print("="*55 + "\n")


app = FastAPI(title=config.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("\n" + "="*50)
    logger.warning("⚠️ BAD REQUEST (422 Validation Error)")
    logger.warning(f"URL: {request.url}")
    logger.warning(f"Errors: {exc.errors()}")
    if hasattr(exc, 'body'):
        logger.warning(f"Body: {exc.body}")
    logger.warning("="*50 + "\n")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": getattr(exc, 'body', None)},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("\n" + "="*50)
    logger.warning(f"⚠️ HTTP EXCEPTION ({exc.status_code})")
    logger.warning(f"URL: {request.url}")
    logger.warning(f"Detail: {exc.detail}")
    logger.warning("="*50 + "\n")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("\n" + "="*50)
    logger.info(f"➡️ INCOMING REQUEST: {request.method} {request.url.path}")
    client_host = request.client.host if request.client and hasattr(request.client, 'host') else 'Unknown'
    logger.info(f"Client API: {client_host}")
    if request.url.query:
        logger.info(f"Query Params: {request.url.query}")
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        status_code = response.status_code
        if 200 <= status_code < 300:
            logger.info(f"✅ SUCCESS ({status_code}) - Time: {process_time:.4f}s")
        elif 400 <= status_code < 500:
            logger.warning(f"⚠️ BAD REQUEST ({status_code}) - Time: {process_time:.4f}s")
        elif status_code >= 500:
            logger.error(f"❌ SERVER ERROR ({status_code}) - Time: {process_time:.4f}s")
        else:
            logger.info(f"ℹ️ RESPONSE ({status_code}) - Time: {process_time:.4f}s")
            
        logger.info("="*50 + "\n")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error("\n" + "="*50)
        logger.error(f"❌ UNHANDLED EXCEPTION - Time: {process_time:.4f}s")
        logger.error(f"Error details: {str(e)}")
        logger.error("="*50 + "\n")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "details": str(e)}
        )

app.include_router(query_routes.router)
app.include_router(schema_routes.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "message": "Text-to-SQL API is running successfully."}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=config.PORT, reload=True)
