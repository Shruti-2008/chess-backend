from app import oauth2
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from typing import List

router = APIRouter(
    prefix="/users", tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db:Session = Depends(get_db)):
    
    #check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if(existing_user):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with email {user.email} already exists")
    #hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist")
    
    return user

@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users

