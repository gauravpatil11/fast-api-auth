from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib   # ✅ NEW

SECRET_KEY = "cc172b2385e5fc857b2a05e8d7293aac8b07082f05af72f8d1db9b2494b94f32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    password = hashlib.sha256(password.encode()).hexdigest()   # ✅ MUST be here
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    plain_password = hashlib.sha256(plain_password.encode()).hexdigest()  # ✅ MUST
    return pwd_context.verify(plain_password, hashed_password)

# 🔑 JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt