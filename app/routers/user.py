from operator import and_, or_
from app import oauth2
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import case, or_, and_, func
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

@router.get("/stats", response_model=List[schemas.UserStats]) #response_model=schemas.UserOut
def get_user(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # user = db.query(models.User).filter(models.User.id == id).first()
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist")
    
    # if id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You are unauthorized to view this data")

    stats = db.query(case(
        (models.Game.winner == 't', 'tie'),
        (or_(and_(models.Game.winner == 'w', models.Game.white_player_id == current_user.id),and_(models.Game.winner == 'b', models.Game.black_player_id == current_user.id)), 'won'),
        else_='lost'
    ).label('result'), func.count().label('count')).filter(and_(or_(models.Game.black_player_id ==  current_user.id, models.Game.white_player_id == current_user.id), models.Game.is_concluded)).group_by('result').all()
    return stats

@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).filter(models.User.id != current_user.id).all()
    return users

