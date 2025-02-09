import os
import logging
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/moderation_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY in your environment.")

logger.info("Configuration loaded successfully.")
