from fastapi import APIRouter, Depends, HTTPException, status
from operator import and_, or_
from sqlalchemy import or_, and_, func, case
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError

from app import schemas
from ..database import get_db
from .. import models, oauth2
from typing import List

router = APIRouter(
    prefix="/games", tags=["Games"]
)

# return list of concluded games of the user


@router.get("/", response_model=List[schemas.GameOverview])
def get_games_history(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        white, black = aliased(models.User), aliased(models.User)
        query = (
            db.query(models.Game, white, black)
            .join(white, white.id == models.Game.white_player_id)
            .join(black, black.id == models.Game.black_player_id)
            .with_entities(
                models.Game.id,
                models.Game.winner,
                models.Game.end_reason,
                white.email.label('white_player'),
                black.email.label('black_player'),
                func.array_length(models.Game.move_history,
                                  1).label('no_of_moves'),
                models.Game.created_at
            )
            .filter(
                and_(
                    or_(
                        models.Game.white_player_id == current_user.id,
                        models.Game.black_player_id == current_user.id
                    ),
                    models.Game.is_concluded == True
                )
            )
            .order_by(models.Game.created_at.desc())
        )

        games = query.all()
        return games
    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# return active game of user


@router.get("/active", response_model=schemas.ActiveGameOut | None)
def get_ongoing_game(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        white, black = aliased(models.User), aliased(models.User)

        game = (
            db.query(models.Game)
            .join(models.Capture, models.Game.capture_id == models.Capture.id)
            .join(white, white.id == models.Game.white_player_id)
            .join(black, black.id == models.Game.black_player_id)
            .with_entities(
                models.Game.id,
                models.Game.white_player_id,
                models.Game.black_player_id,
                white.email.label('white_player'),
                black.email.label('black_player'),
                models.Game.board,
                models.Game.active_player,
                models.Game.last_move_start,
                models.Game.last_move_end,
                models.Game.move_history,
                models.Game.steps,
                models.Game.white_king_pos,
                models.Game.black_king_pos,
                models.Game.enpassant_position,
                models.Game.castle_eligibility,
                models.Game.checked_king,
                models.Game.is_concluded,
                models.Game.winner,
                models.Game.end_reason,
                models.Game.draw,
                models.Capture,
                (case(
                    (models.Game.white_player_id == current_user.id, 'w'),
                    else_='b'
                )).label("player_color"),
            )
            .filter(
                and_(
                    models.Game.is_concluded == 'f',
                    or_(
                        models.Game.white_player_id == current_user.id,
                        models.Game.black_player_id == current_user.id
                    )
                )
            )
            .first()
        )
        return game

    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# return details of selected game


@router.get("/{id}", response_model=schemas.ActiveGameOut)
def get_game(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        white, black = aliased(models.User), aliased(models.User)
        game = (
            db.query(models.Game, white, black)
            .join(white, white.id == models.Game.white_player_id)
            .join(black, black.id == models.Game.black_player_id)
            .join(models.Capture, models.Game.capture_id == models.Capture.id)
            .with_entities(
                models.Game.id,
                models.Game.board,
                white.email.label('white_player'),
                black.email.label('black_player'),
                models.Game.active_player,
                models.Game.white_king_pos,
                models.Game.black_king_pos,
                models.Game.enpassant_position,
                models.Game.castle_eligibility,
                models.Game.is_concluded,
                models.Game.winner,
                models.Game.end_reason,
                models.Game.checked_king,
                func.array_length(models.Game.move_history,
                                  1).label('no_of_moves'),
                models.Game.last_move_start,
                models.Game.last_move_end,
                models.Game.move_history,
                models.Game.steps,
                models.Game.draw,
                models.Capture,
                models.Game.white_player_id,
                models.Game.black_player_id,
                (case(
                    (models.Game.white_player_id == current_user.id, 'w'),
                    else_='b'
                )).label("player_color"),
            )
            .filter(models.Game.id == id)
            .first()
        )

        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Game with id {id} does not exist")
        else:
            if current_user.id not in (game.white_player_id, game.black_player_id):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail=f"You are unauthorized to view this data")
        return game

    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# create a new game


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ActiveGameOut)
def create_game(request: schemas.GameStartIn, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if not db.query(models.User).filter(models.User.id == request.opponent_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Opponent does not exist")
    else:
        try:
            white, black = aliased(models.User), aliased(models.User)

            capture = models.Capture()
            db.add(capture)
            db.commit()
            game = models.Game()
            game.black_player_id = request.opponent_id
            game.white_player_id = current_user.id
            game.capture_id = capture.id
            db.add(game)
            db.commit()

            result = (
                db.query(models.Game)
                .join(models.Capture, models.Game.capture_id == models.Capture.id)
                .join(white, white.id == models.Game.white_player_id)
                .join(black, black.id == models.Game.black_player_id)
                .with_entities(
                    models.Game.id,
                    models.Game.white_player_id,
                    models.Game.black_player_id,
                    white.email.label('white_player'),
                    black.email.label('black_player'),
                    models.Game.board,
                    models.Game.active_player,
                    models.Game.last_move_start,
                    models.Game.last_move_end,
                    models.Game.move_history,
                    models.Game.steps,
                    models.Game.white_king_pos,
                    models.Game.black_king_pos,
                    models.Game.enpassant_position,
                    models.Game.castle_eligibility,
                    models.Game.checked_king,
                    models.Game.is_concluded,
                    models.Game.winner,
                    models.Game.end_reason,
                    models.Game.draw,
                    models.Capture,
                    (case(
                        (models.Game.white_player_id == current_user.id, 'w'),
                        else_='b')).label("player_color"))
                .filter(models.Game.id == game.id)
                .first()
            )
            return result

        except SQLAlchemyError as e:
            error = str(e.orig)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error)
