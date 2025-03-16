import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.models import Base
from sqlalchemy import create_engine
from src.config import DATABASE_URL, logger

print(f"Attempting to connect to database using: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    logger.info("Database initialized successfully")
except Exception as e:
    print(f"Error initializing database: {str(e)}")
    logger.error(f"Database initialization failed: {str(e)}")