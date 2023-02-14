from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str]

class UserStats(BaseModel):
    result: str
    count: int

    class Config:
        orm_mode = True

class CaptureIn(BaseModel):
    p: int
    r: int
    n: int
    b: int
    q: int
    k: int
    P: int
    R: int
    N: int
    B: int
    Q: int
    K: int

    class Config:
        orm_mode = True

class Player(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class Game(BaseModel):
    id: int
    winner: str
    white_player: EmailStr
    black_player: EmailStr

class GameOverview(Game):
    no_of_moves: Optional[int]
    created_at: datetime
    class Config:
        orm_mode = True

class GameDetails(Game):
    move_history: List[str]
    class Config:
        orm_mode = True

class GameStartIn(BaseModel):
    # opponent: EmailStr
    opponent_id: int

class GameMoveIn(BaseModel):
    #id: int
    board : str
    player_color: str
    active_player : str         # can we change it to int? is it even required in GameIn?
    last_move_start : List[int]
    last_move_end : List[int]
    move_history : List[str]    # can we change it to jut str in GameIn?
    white_king_pos : List[int]  # either or . both white and black not required no?
    black_king_pos : List[int]
    castle_eligibility : List[bool] # again just white or black, both not required
    is_concluded : bool
    winner : Optional[str]      # can be changed to int maybe
    win_reason : Optional[str]
    captures: CaptureIn         # just white or black not both


class GameMoveOut(BaseModel):
    id: int
    board : str
    player_color: str
    active_player : str #int
    last_move_start : List[int] = None
    last_move_end : List[int] = None
    move_history : List[str] # str
    white_king_pos : List[int] #either or
    black_king_pos : List[int]
    castle_eligibility : List[bool] #either or
    is_concluded : bool
    winner : Optional[str] #int
    win_reason : Optional[str]
    Capture: CaptureIn #either or

    class Config:
        orm_mode = True
    