from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import moderation, health
from app.routes.moderation import get_db_connection  # ✅ Import new function
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
try:
    conn, cursor = get_db_connection()
    conn.close() 
    logger.info("✅ Database connection successful.")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    raise RuntimeError("Database connection not available.")
app = FastAPI(title="Content Moderation API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(moderation.router)
app.include_router(health.router)
logger.info("🚀 FastAPI app started successfully!")
