from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))

    owner = relationship("User")
