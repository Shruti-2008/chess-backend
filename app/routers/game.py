from http.client import HTTPException
from operator import and_, or_
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, with_expression, aliased
from sqlalchemy import or_, and_, func

from app import schemas
from ..database import get_db
from .. import models, oauth2
from typing import List

router = APIRouter(
    prefix="/games", tags=["Games"]
)

@router.get("/{game_id}", response_model=schemas.Game)
def get_game(game_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id {game_id} does not exist")
    else:
        game_dict = game.__dict__
        if not (game_dict['white_player_id'] == current_user.id or game_dict['black_player_id'] == current_user.id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You are unauthorized to view this data")
    return game

@router.get("/", response_model=List[schemas.Game])
def get_games_history(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    white, black = aliased(models.User), aliased(models.User)
    query = db.query(models.Game, white, black) \
      .join(white, white.id == models.Game.white_player_id) \
      .join(black, black.id == models.Game.black_player_id) \
      .with_entities(models.Game.id, models.Game.winner, white.email.label('white_player'), black.email.label('black_player'), func.array_length(models.Game.move_history, 1).label('no_of_moves')) \
    .filter(and_(or_(models.Game.white_player_id == current_user.id, models.Game.black_player_id == current_user.id), models.Game.is_concluded == True))

    games = query.all()
    return games
    # return []