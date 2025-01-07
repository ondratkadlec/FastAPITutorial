from sqlalchemy import Column, String, Integer, TIMESTAMP, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    time_updated = Column(TIMESTAMP(timezone=True), nullable=False, onupdate=func.now())

