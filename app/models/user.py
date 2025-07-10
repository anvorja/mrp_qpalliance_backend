# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    """
    Modelo para usuarios del sistema.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="admin")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"