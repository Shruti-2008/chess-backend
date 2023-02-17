from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import models
from . import schemas
from .database import get_db
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

ACCESS_SECRET_KEY = settings.access_secret_key
REFRESH_SECRET_KEY = settings.refresh_secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRED_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRED_MINUTES = settings.refresh_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRED_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRED_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, ALGORITHM)
        id: str = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception
    
    return token_data

def verify_refresh_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, ALGORITHM)
        id: str = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials', headers={"WWW-Authenticate":"Bearer"}
    )
    token_data = verify_access_token(token, credentials_exception)
    # query database based on id and return user
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user 

def get_socket_user(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials', headers={"WWW-Authenticate":"Bearer"}
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user 

def get_refresh_user(token: str, db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate credentials', headers={"WWW-Authenticate":"Bearer"}
    )
    token_data = verify_refresh_token(token, credentials_exception)
    # query database based on id and return user
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user 