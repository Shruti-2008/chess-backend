from array import array
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str]

class Player(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class Game(BaseModel):
    id: int
    no_of_moves: Optional[int]
    winner: str
    white_player: EmailStr
    black_player: EmailStr
    # move_history: List[str]
    # created_at: datetime
    
    class Config:
        orm_mode = True

