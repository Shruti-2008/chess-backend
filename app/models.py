from .database import Base
from sqlalchemy import Column, Integer, String, BOOLEAN, ForeignKey, SmallInteger, ARRAY
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, query_expression, Mapped


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True, nullable=False)
    p = Column(SmallInteger, nullable=False, server_default='0')
    r = Column(SmallInteger, nullable=False, server_default='0')
    n = Column(SmallInteger, nullable=False, server_default='0')
    b = Column(SmallInteger, nullable=False, server_default='0')
    q = Column(SmallInteger, nullable=False, server_default='0')
    k = Column(SmallInteger, nullable=False, server_default='0')
    P = Column(SmallInteger, nullable=False, server_default='0')
    R = Column(SmallInteger, nullable=False, server_default='0')
    N = Column(SmallInteger, nullable=False, server_default='0')
    B = Column(SmallInteger, nullable=False, server_default='0')
    Q = Column(SmallInteger, nullable=False, server_default='0')
    K = Column(SmallInteger, nullable=False, server_default='0')


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, nullable=False)
    white_player_id = Column(Integer, ForeignKey(User.id), nullable=False)
    black_player_id = Column(Integer, ForeignKey(User.id), nullable=False)
    board = Column(String, nullable=False,
                   server_default="rnbqkbnr#pppppppp#8#8#8#8#PPPPPPPP#RNBQKBNR")
    active_player = Column(String, nullable=False, server_default="w")
    last_move_start = Column(ARRAY(Integer), server_default="{}")
    last_move_end = Column(ARRAY(Integer), server_default="{}")
    move_history = Column(ARRAY(String), nullable=False, server_default="{}")
    white_king_pos = Column(ARRAY(Integer), server_default="{0,4}")
    black_king_pos = Column(ARRAY(Integer), server_default="{7,4}")
    # white queenside, white kingside, black queenside, black kingside
    castle_eligibility = Column(
        ARRAY(BOOLEAN), server_default="{TRUE,TRUE,TRUE,TRUE}")
    capture_id = Column(Integer, ForeignKey(Capture.id),
                        nullable=False, unique=True)
    is_concluded = Column(BOOLEAN, nullable=False, server_default='FALSE')
    # 1-> White #2->Black #3->Draw
    winner = Column(Integer)
    # 1-> Checkmate #2-> StaleMate #3-> Resignation #4->Agreement
    end_reason = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    # no_of_moves : Mapped[Integer] = query_expression()
    checked_king = Column(String)
    enpassant_position = Column(ARRAY(Integer), server_default="{}")
    # 1-> White offered draw #2->Black offered draw #3-> White rejected draw #4-> Black rejected draw #5-> White accepted draw #6 -> Black accepted draw
    draw = Column(Integer)
    steps = Column(ARRAY(String), nullable=False, server_default="{}")

    white_player = relationship("User", foreign_keys='Game.white_player_id')
    black_player = relationship("User", foreign_keys='Game.black_player_id')
    captures = relationship("Capture", foreign_keys='Game.capture_id')


class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, nullable=False)
    refresh = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
