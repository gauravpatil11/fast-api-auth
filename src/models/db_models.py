from sqlalchemy import Boolean, Column, DateTime, Integer, String

from src.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    password_reset_otp_hash = Column(String(64), nullable=True)
    password_reset_otp_expires_at = Column(DateTime(timezone=False), nullable=True)
    password_reset_otp_created_at = Column(DateTime(timezone=False), nullable=True)
