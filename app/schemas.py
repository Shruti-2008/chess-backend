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

# same as user. can be deleted


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
    end_reason: int


class GameOverview(Game):
    no_of_moves: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


class GameDetails(Game):
    board: str
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
    active_player: str
    last_move_start: List[int]
    last_move_end: List[int]
    move_history: List[str]
    steps: List[str]
    white_king_pos: List[int]
    black_king_pos: List[int]
    enpassant_position: List[int]
    castle_eligibility: List[bool]
    checked_king: Optional[str]
    is_concluded: bool
    winner: Optional[int]
    end_reason: Optional[int]
    draw: Optional[int]
    Capture: CaptureIn


class GameMoveOut(BaseModel):
    id: int
    board: str
    player_color: str
    active_player: str
    last_move_start: Optional[List[int]]
    last_move_end: Optional[List[int]]
    move_history: List[str]
    steps: List[str]
    white_king_pos: List[int]
    black_king_pos: List[int]
    enpassant_position: List[int]
    castle_eligibility: List[bool]
    checked_king: Optional[str]
    is_concluded: bool
    winner: Optional[int]
    end_reason: Optional[int]
    draw: Optional[int]
    Capture: CaptureIn

    class Config:
        orm_mode = True


class ActiveGameOut(GameMoveOut):
    white_player: str
    black_player: str

    class Config:
        orm_mode = True
