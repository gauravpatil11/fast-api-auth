from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func

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


class Strategy(Base):
    __tablename__ = "strategies"
    __table_args__ = (
        UniqueConstraint("user_id", "strategy_name", name="uq_strategies_user_id_strategy_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    strategy_name = Column(String(255), nullable=False)
    legs = Column(JSON, nullable=False)
    multiplier = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
