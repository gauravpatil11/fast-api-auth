from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.dependencies import get_current_admin, get_current_user, get_db, get_user, get_user_by_email
from auth.utils import get_password_hash
from .schemas import User, UserUpdate
from .models import User as UserModel

router = APIRouter()

@router.get("/profile", response_model=User)
def get_profile(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=User)
def update_profile(
    profile_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if profile_data.username and profile_data.username != current_user.username:
        existing_user = get_user(db, profile_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        current_user.username = profile_data.username

    if profile_data.email and profile_data.email != current_user.email:
        existing_email = get_user_by_email(db, profile_data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = profile_data.email

    if profile_data.password:
        current_user.hashed_password = get_password_hash(profile_data.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/userlist", response_model=list[User])
def get_user_list(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin),
):
    return db.query(UserModel).all()
