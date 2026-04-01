
from sqlalchemy import Column, Integer, String, Boolean
from auth.database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, index=True)   
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))                    

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

