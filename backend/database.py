"""
database.py - SQLAlchemy database setup
"""
import os
import pathlib
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime

BASE_DIR = pathlib.Path(__file__).parent.parent
DB_PATH = BASE_DIR / "bus_crowd.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class TicketDB(Base):
    __tablename__ = "tickets"

    id                 = Column(Integer, primary_key=True, index=True)
    ticket_id          = Column(String, unique=True, index=True)
    bus_id             = Column(String, index=True)
    route_id           = Column(String, index=True)
    trip_id            = Column(String, index=True)
    boarding_stop_seq  = Column(Integer)
    dest_stop_seq      = Column(Integer)
    timestamp          = Column(DateTime, default=datetime.utcnow)
    passenger_count    = Column(Integer, default=1)
    fare               = Column(Float, default=0.0)
    bus_capacity       = Column(Integer, default=50)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
