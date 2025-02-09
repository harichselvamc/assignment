import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from app.config import DATABASE_URL


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS moderation_results (
                id SERIAL PRIMARY KEY,
                text TEXT,
                result JSONB
            )
            """)
            self.conn.commit()

            logger.info("✅ Database connection successful, and table initialized.")

        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.conn = None
            self.cursor = None 
    def get_connection(self):
        """Returns the current connection and cursor."""
        if self.conn is None or self.cursor is None:
            self.connect()
        return self.conn, self.cursor
db = Database()
