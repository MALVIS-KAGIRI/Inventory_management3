from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_app(app):
    """Initialize database with Flask app"""
    try:
        # Configure SQLAlchemy with app
        db.init_app(app)
        
        logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Test database connection and create tables
        with app.app_context():
            db.engine.connect()
            logger.info("Successfully connected to SQL Server")
            
            # Create all tables if they don't exist
            db.create_all()
            logger.info("Database tables created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        logger.error("Check database configuration and try again.")
        return False