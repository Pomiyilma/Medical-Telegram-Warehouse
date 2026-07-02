import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Build connection parameters string pulling values from your root .env file
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "medical_warehouse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the primary SQLAlchemy database core runtime pipeline
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Build a thread-safe transaction factory session sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency Provider: Safely yields an active database session worker 
    and automatically disconnects/closes the slot when the web request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        