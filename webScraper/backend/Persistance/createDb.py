from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# PostgreSQL connection for pgAdmin
# Default connection: postgresql://username:password@host:port/database
engine = create_engine(
    "postgresql://postgres:password@localhost:5432/webscraper",
    echo=True
)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass