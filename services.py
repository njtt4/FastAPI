from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Union
from jose import jwt
from fastapi_login import LoginManager

from sqlalchemy.orm import Session
from models import User as UserDB

SECRET_KEY = "25c7d867bbdde3b7c4c1f0207a139765362c3c0d0d366baf53acd507a73182cd"
ALGORITHM = "HS256"


class NotAuthenticatedException(Exception):
    pass


manager = LoginManager(secret=SECRET_KEY, token_url="/login", use_cookie=True)
manager.cookie_name = "auth"
manager.not_authenticated_exception = NotAuthenticatedException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username:str):
    return db.query(UserDB).filter(UserDB.email == username).first()


def authenticate_user(username: str, password: str, db):
    user = get_user(db, username)
    if not user:
        return False

    if not user.verify_password(password=password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None]= None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def is_authenticated(request):
    token = request.cookies.get("auth")
    if token == "None" or token is None:
        return False
    return True