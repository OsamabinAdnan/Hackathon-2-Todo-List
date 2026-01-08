from sqlmodel import create_engine, Session, SQLModel
from app.config.settings import settings

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,  # This now uses the property that accesses NEON_DB_URL
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
    echo=True if settings.ENVIRONMENT == "development" else False
)

def init_db():
    """Initialize the database by creating all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting database sessions."""
    with Session(engine) as session:
        yield session