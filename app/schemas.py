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
    # created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    token_type: str
    access_token: str


class TokenData(BaseModel):
    id: Optional[str]


class RefreshTokenIn(BaseModel):
    refresh_token: str


class TokenOut(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str


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
    winner: int
    white_player: EmailStr
    black_player: EmailStr


class GameOverview(Game):
    no_of_moves: Optional[int]
    end_reason: int
    created_at: datetime

    class Config:
        orm_mode = True


class GameDetails(Game):
    board: str
    white_player: str
    black_player: str
    winner: int
    end_reason: int
    checked_king: Optional[str]
    last_move_start: List[int] = None
    last_move_end: List[int] = None
    move_history: List[str]
    steps: List[str]
    Capture: CaptureIn

    class Config:
        orm_mode = True


class GameStartIn(BaseModel):
    # opponent: EmailStr
    opponent_id: int


class GameMoveIn(BaseModel):
    id: int
    board: str
    player_color: str
    active_player: str         # can we change it to int? is it even required in GameIn?
    last_move_start: List[int]
    last_move_end: List[int]
    move_history: List[str]    # can we change it to jut str in GameIn?
    steps: List[str]
    # either or . both white and black not required no?
    white_king_pos: List[int]
    black_king_pos: List[int]
    enpassant_position: List[int]
    # again just white or black, both not required
    castle_eligibility: List[bool]
    checked_king: Optional[str]
    is_concluded: bool
    winner: Optional[int]      # can be changed to int maybe
    end_reason: Optional[int]
    draw: Optional[int]
    captures: CaptureIn         # just white or black not both


class GameMoveOut(BaseModel):
    id: int
    board: str
    player_color: str
    active_player: str  # int
    last_move_start: Optional[List[int]]  # = None
    last_move_end: Optional[List[int]]  # = None
    move_history: List[str]  # str
    steps: List[str]
    white_king_pos: List[int]  # either or
    black_king_pos: List[int]
    enpassant_position: List[int]
    castle_eligibility: List[bool]  # either or
    checked_king: Optional[str]
    is_concluded: bool
    winner: Optional[int]  # int
    end_reason: Optional[int]
    draw: Optional[int]
    Capture: CaptureIn  # either or

    class Config:
        orm_mode = True


class ActiveGameOut(GameMoveOut):
    white_player: str
    black_player: str

    class Config:
        orm_mode = True
