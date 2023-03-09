from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict

from app import oauth2
from .. import schemas, models
from ..database import get_db

router = APIRouter()

# @router.websocket("/ws")
# async def websocket_endpoint(webSocket: WebSocket, current_user: int = Depends(oauth2.get_socket_user)):
#     print("Hit websocket endpoint inside socket file")
#     print(current_user.id)
#     await webSocket.accept()
#     try:
#         while True:
#             data = await webSocket.receive_text()
#             print(data)
#             await webSocket.send_text(f"Message text was {data}")
#     except WebSocketDisconnect:
#         print("Disconnected Websocket. The end")
#     except Exception as e:
#         print("error is ", e)
#         webSocket.close()


class ConnectionManager_v0:
    def __init__(self):
        self.active_connections = defaultdict(list[WebSocket])

    async def connect(self, websocket: WebSocket, game_id: int, user_id: int):
        await websocket.accept()
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: int):
        self.active_connections[game_id].remove(websocket)
        if self.active_connections[game_id] == []:
            self.active_connections.pop(game_id)

    async def send_move(self, move: str, websocket: WebSocket, game_id: int, data: schemas.GameMoveIn, db: Session):
        data['player_color'] = "b" if data['player_color'] == "w" else "w"
        if len(self.active_connections[game_id]) >= 2:
            for socket in self.active_connections[game_id]:
                if socket != websocket:
                    await socket.send_json(move)
        update_move_in_db(data, db)


class ConnectionManager:

    def __init__(self):
        self.active_connections = defaultdict(lambda: defaultdict(WebSocket))

    async def connect(self, websocket: WebSocket, game_id: int, user_id: int):
        await websocket.accept()
        self.active_connections[game_id][user_id] = websocket

    def disconnect(self, game_id: int, user_id: int):
        if game_id in self.active_connections and user_id in self.active_connections[game_id]:
            self.active_connections[game_id].pop(user_id)
            if self.active_connections[game_id] == {}:
                self.active_connections.pop(game_id)

    async def send_move(self, game_id: int, user_id: int,  data: schemas.GameMoveIn, db: Session):
        # change player_color before sending response #do we even need to send player_color?
        data['player_color'] = "b" if data['player_color'] == "w" else "w"
        # more than 1 player is connected to the game
        if len(self.active_connections[game_id]) > 1:
            print("active connections > 1")
            for user in self.active_connections[game_id]:
                if user != user_id:
                    await self.active_connections[game_id][user].send_json(data)
                    print("Sent move to user : ", user, " websocket = ",
                          self.active_connections[game_id][user])
        update_move_in_db(data, db, user_id)

# print(f"joined room for game {game_id} for user {user_id}")
# print(f"game room for game {game_id} : ", self.active_connections[game_id])
# if self.active_connections[game_id] == {}: #[]
#     print(f"creating room for game {game_id} for user {user_id}")
# print("Closing connection", game_id, user_id)


manager = ConnectionManager()


def update_move_in_db(data: schemas.GameMoveIn, db: Session, user_id: int):
    try:
        game: models.Game = (
            db.query(models.Game)
            .filter(models.Game.id == data['id'])
            .first()
        )
        capture: models.Capture = (
            db.query(models.Capture)
            .filter(models.Capture.id == game.capture_id)
            .first()
        )

        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Game with id {id} does not exist")
        if user_id not in (game.white_player_id, game.black_player_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"You are not authorized to update game with id {id}")

        game.board = data['board']
        game.active_player = data['active_player']
        game.last_move_start = data['last_move_start']
        game.last_move_end = data['last_move_end']
        game.move_history = data['move_history']
        game.steps = data['steps']
        game.white_king_pos = data['white_king_pos']
        game.black_king_pos = data['black_king_pos']
        game.enpassant_position = data['enpassant_position']
        game.castle_eligibility = data['castle_eligibility']
        game.checked_king = data['checked_king']
        game.is_concluded = data['is_concluded']
        game.winner = data['winner']
        game.end_reason = data['end_reason']
        game.draw = data['draw']

        capture.p = data['Capture']['p']
        capture.r = data['Capture']['r']
        capture.n = data['Capture']['n']
        capture.b = data['Capture']['b']
        capture.q = data['Capture']['q']
        capture.k = data['Capture']['k']
        capture.P = data['Capture']['P']
        capture.R = data['Capture']['R']
        capture.N = data['Capture']['N']
        capture.B = data['Capture']['B']
        capture.Q = data['Capture']['Q']
        capture.K = data['Capture']['K']

        db.commit()

    except SQLAlchemyError as e:
        error = str(e.orig)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)


@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, current_user: int = Depends(oauth2.get_socket_user), db: Session = Depends(get_db)):
    await manager.connect(websocket, game_id, current_user.id)
    try:
        while True:
            data = await websocket.receive_json()
            print("recieved data from ", current_user.id)
            await manager.send_move(game_id, current_user.id, data, db)
    except WebSocketDisconnect:
        manager.disconnect(game_id, current_user.id)
        # print(f"User with id {current_user.id} disconnected from game")
