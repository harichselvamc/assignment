from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
import os
import shutil
import json
import logging
import base64
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from app.models import TextModerationRequest
from app.tasks import run_moderation_task, run_image_moderation_task
from app.cache import get_cached_moderation, set_cached_moderation  # Assuming these are async functions

# Initialize router
router = APIRouter()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Temporary directory for images
TEMP_IMAGE_DIR = "temp_images"
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)  # Ensure temp directory exists

# Database connection settings
DB_HOST = os.getenv("POSTGRES_HOST", "db")  # Ensure it uses the correct Docker service name
DB_NAME = os.getenv("POSTGRES_DB", "moderation_db")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database with retry logic.
    Returns a tuple: (connection, cursor).
    """
    retries = 5
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                cursor_factory=RealDictCursor
            )
            cursor = conn.cursor()
            return conn, cursor
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection failed (Attempt {attempt+1}/{retries}): {e}")
            time.sleep(5)

    raise HTTPException(status_code=500, detail="Database connection error")

def create_moderation_results_table():
    """
    Ensures the moderation_results table exists in the database.
    """
    try:
        conn, cursor = get_db_connection()

        # SQL to create the moderation_results table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_results (
            id SERIAL PRIMARY KEY,
            result JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

        conn.close()
        logger.info("Successfully ensured moderation_results table exists.")
    except Exception as e:
        logger.error(f"Error creating moderation_results table: {e}")
        raise HTTPException(status_code=500, detail="Database table creation error")

# Ensure the table is created at startup
create_moderation_results_table()

@router.post("/api/v1/moderate/text")
async def moderate_text(request: TextModerationRequest, background_tasks: BackgroundTasks):
    """
    Handles text moderation requests.
    - Checks cache first.
    - If not cached, processes in the background using Celery.
    """
    text = request.text.strip()

    try:
        # Check cache for previous moderation results
        cached_result = await get_cached_moderation(text)  # Only await if get_cached_moderation is async

        # If it's None or doesn't exist, it means there's no cached result
        if cached_result:
            return json.loads(cached_result)

        # Process text moderation asynchronously
        background_tasks.add_task(run_moderation_task, text)

        logger.info(f"Text moderation request received: {text}")
        return {"message": "Processing", "text": text}

    except Exception as e:
        logger.error(f"Error processing text moderation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/v1/moderate/image")
async def moderate_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Handles image moderation requests.
    - Saves image temporarily.
    - Converts to Base64 for caching.
    - If not cached, processes in the background using Celery.
    """
    try:
        # Save uploaded image to a temporary directory
        file_location = os.path.join(TEMP_IMAGE_DIR, file.filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert image to Base64 for caching
        with open(file_location, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Check cache for previous moderation results
        cached_result = await get_cached_moderation(base64_image)
        if cached_result:
            return json.loads(cached_result)

        # Process image moderation asynchronously
        background_tasks.add_task(run_image_moderation_task, base64_image)

        logger.info(f"Image received for moderation: {file.filename}")
        return {"message": "Processing", "file_path": file_location}

    except Exception as e:
        logger.error(f"Error processing image moderation: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")


@router.get("/api/v1/moderation/{moderation_id}")
async def get_moderation_result(moderation_id: int):
    """
    Retrieves a specific moderation result from the database.
    """
    try:
        conn, cursor = get_db_connection()

        cursor.execute("SELECT result FROM moderation_results WHERE id = %s", (moderation_id,))
        result = cursor.fetchone()

        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        return {"moderation_result": result["result"]}  # Fetch JSONB column correctly

    except Exception as e:
        logger.error(f"Database error while fetching moderation result: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/api/v1/stats")
async def get_stats():
    """
    Returns statistics on the total number of moderation requests processed.
    """
    try:
        conn, cursor = get_db_connection()

        cursor.execute("SELECT COUNT(*) FROM moderation_results")
        result = cursor.fetchone()

        conn.close()

        total_moderations = result["count"] if result else 0

        return {"total_moderations": total_moderations}

    except Exception as e:
        logger.error(f"Database error while fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Database error")
