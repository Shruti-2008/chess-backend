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
        )

        games = query.all()
        return games
    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# return active game of user


@router.get("/active", response_model=schemas.GameMoveOut | None)
def get_ongoing_game(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        game = (
            db.query(models.Game)
            .join(models.Capture, models.Game.capture_id == models.Capture.id)
            .with_entities(
                models.Game.id,
                models.Game.white_player_id,
                models.Game.black_player_id,
                models.Game.board,
                models.Game.active_player,
                models.Game.last_move_start,
                models.Game.last_move_start,
                models.Game.last_move_end,
                models.Game.move_history,
                models.Game.white_king_pos,
                models.Game.black_king_pos,
                models.Game.castle_eligibility,
                models.Game.is_concluded,
                models.Game.winner,
                models.Game.win_reason,
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
        # if not game:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No ongoing games for user with id {current_user.id}")
        return game

    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

# return move history of selected concluded game


@router.get("/{id}", response_model=schemas.GameDetails)
def get_game(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    white, black = aliased(models.User), aliased(models.User)
    game = (
        db.query(models.Game, white, black)
        .join(white, white.id == models.Game.white_player_id)
        .join(black, black.id == models.Game.black_player_id)
        .with_entities(
            models.Game.id,
            models.Game.winner,
            white.email.label('white_player'),
            black.email.label('black_player'),
            func.array_length(models.Game.move_history,
                              1).label('no_of_moves'),
            models.Game.move_history,
            models.Game.white_player_id,
            models.Game.black_player_id)
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

# create a new game


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.GameMoveOut)
def create_game(request: schemas.GameStartIn, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # if not db.query(models.User).filter(models.User.id == request.opponent_id).first():
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Opponent does not exist")
    try:
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
            .with_entities(
                models.Game.id,
                models.Game.white_player_id,
                models.Game.black_player_id,
                models.Game.board,
                models.Game.active_player,
                models.Game.last_move_start,
                models.Game.last_move_start,
                models.Game.last_move_end,
                models.Game.move_history,
                models.Game.white_king_pos,
                models.Game.black_king_pos,
                models.Game.castle_eligibility,
                models.Game.is_concluded,
                models.Game.winner,
                models.Game.win_reason,
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


# response_model=schemas.GameMoveOut
# not in use
@router.post("/{id}", status_code=status.HTTP_201_CREATED, )
def makeMove(id: int, move: schemas.GameMoveIn, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # game = (
    #     db.query(models.Game)
    #     .join(models.Capture, models.Game.capture_id == models.Capture.id)
    #     .with_entities(
    #         models.Game.id,
    #         models.Game.white_player_id,
    #         models.Game.black_player_id,
    #         models.Game.board,
    #         models.Game.active_player,
    #         models.Game.last_move_start,
    #         models.Game.last_move_start,
    #         models.Game.last_move_end,
    #         models.Game.move_history,
    #         models.Game.white_king_pos,
    #         models.Game.black_king_pos,
    #         models.Game.castle_eligibility,
    #         models.Game.is_concluded,
    #         models.Game.winner,
    #         models.Game.win_reason,
    #         models.Capture
    #     )
    #     .filter(models.Game.id == id)
    #     .first()
    # )

    game = (
        db.query(models.Game)
        .filter(models.Game.id == id)
        .first()
    )
    capture = (
        db.query(models.Capture)
        .filter(models.Capture.id == game.capture_id)
        .first()
    )

    game.board = move.board
    game.active_player = move.active_player
    game.last_move_start = move.last_move_start
    game.last_move_end = move.last_move_end
    game.move_history = move.move_history
    game.white_king_pos = move.white_king_pos
    game.black_king_pos = move.black_king_pos
    game.castle_eligibility = move.castle_eligibility
    game.is_concluded = move.is_concluded
    game.winner = move.winner
    game.win_reason = move.win_reason

    capture.p = move.captures.p
    capture.r = move.captures.r
    capture.n = move.captures.n
    capture.b = move.captures.b
    capture.q = move.captures.q
    capture.k = move.captures.k
    capture.P = move.captures.P
    capture.R = move.captures.R
    capture.N = move.captures.N
    capture.B = move.captures.B
    capture.Q = move.captures.Q
    capture.K = move.captures.K

    db.commit()

    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game with id {id} does not exist")
    if current_user.id not in (game.white_player_id, game.black_player_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You are not authorized to update game with id {id}")
    return game


# @router.get("/{id}", response_model=schemas.Game)
# def get_game(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
#     game = db.query(models.Game).filter(models.Game.id == id).first()
#     if not game:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id {id} does not exist")
#     else:
#         game_dict = game.__dict__
#         if not (game_dict['white_player_id'] == current_user.id or game_dict['black_player_id'] == current_user.id):
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"You are unauthorized to view this data")
#     return game
