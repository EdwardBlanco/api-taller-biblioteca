import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:1234@localhost:5432/postgres")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass
