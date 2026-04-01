from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None


