from operator import and_, or_
from app import oauth2
from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import case, or_, and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from typing import List

router = APIRouter(
    prefix="/users", tags=["Users"]
)

# register a new user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TokenOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # check if user already exists
        existing_user = db.query(models.User).filter(
            models.User.email == user.email).first()
        if (existing_user):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User with email {user.email} already exists")
        # hash the password
        hashed_password = utils.hash(user.password)
        user.password = hashed_password

        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = oauth2.create_access_token(
            data={"user_id": new_user.id})
        refresh_token = oauth2.create_refresh_token(
            data={"user_id": new_user.id})

        token = models.Tokens()
        token.refresh = refresh_token
        db.add(token)
        db.commit()

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# return user stats


@router.get("/stats", response_model=List[schemas.UserStats])
def get_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        stats = (
            db.query(
                case(
                    (models.Game.winner == 3, 'draw'),
                    (or_(
                        and_(
                            models.Game.winner == 1,
                            models.Game.white_player_id == current_user.id
                        ),
                        and_(
                            models.Game.winner == 2,
                            models.Game.black_player_id == current_user.id
                        )
                    ), 'won'),
                    else_='lost'
                ).label('result'),
                func.count().label('count')
            )
            .filter(
                and_(
                    or_(
                        models.Game.black_player_id == current_user.id,
                        models.Game.white_player_id == current_user.id
                    ),
                    models.Game.is_concluded
                )
            )
            .group_by('result')
            .all()
        )
        return stats
    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# return list of available users


@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    try:
        subQuery = (
            db.query(models.User.id)
            .distinct()
            .join(
                models.Game,
                or_(
                    models.Game.black_player_id == models.User.id,
                    models.Game.white_player_id == models.User.id
                ))
            .filter(models.Game.is_concluded == 'f')
            .subquery()
        )
        userQuery = (
            db.query(models.User)
            .filter(
                and_(
                    models.User.id != current_user.id,
                    models.User.id.not_in(subQuery)
                )
            )
        )
        users = userQuery.all()
        return users
    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)
