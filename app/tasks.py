from celery import Celery
import json
import logging
import base64
from openai import OpenAI
from app.config import CELERY_BROKER_URL
from app.cache import set_cached_moderation
celery_app = Celery("tasks", broker=CELERY_BROKER_URL)
client = OpenAI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task
def run_moderation_task(text: str):
    """
    Celery task to process text moderation asynchronously using OpenAI's omni-moderation-latest.
    """
    try:
        from app.routes.moderation import get_db_connection
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=[{"type": "text", "text": text}]
        )
        result = response.results[0] 
        set_cached_moderation(text, result)
        conn, cursor = get_db_connection()
        cursor.execute("INSERT INTO moderation_results (text, result) VALUES (%s, %s)", (text, json.dumps(result)))
        conn.commit()
        conn.close()
        logger.info(f"✅ Text moderation completed: {text}")
        return result
    except Exception as e:
        logger.error(f"❌ Error in text moderation task: {e}")
        return {"error": "Failed to moderate text"}


@celery_app.task
def run_image_moderation_task(base64_image: str):
    """
    Celery task to process image moderation asynchronously using OpenAI's omni-moderation-latest.
    """
    try:
        from app.routes.moderation import get_db_connection
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]
        )
        result = response.results[0]     
        set_cached_moderation(base64_image, result)
        conn, cursor = get_db_connection()
        cursor.execute("INSERT INTO moderation_results (text, result) VALUES (%s, %s)", (base64_image, json.dumps(result)))
        conn.commit()
        conn.close()
        logger.info("✅ Image moderation completed.")
        return result
    except Exception as e:
        logger.error(f"❌ Error in image moderation task: {e}")
        return {"error": "Failed to moderate image"}
