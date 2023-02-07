from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends
from app import oauth2

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(webSocket: WebSocket, current_user: int = Depends(oauth2.get_socket_user)):
    print("Hit websocket endpoint inside socket file")
    print(current_user)
    await webSocket.accept()
    try:
        while True:
            data = await webSocket.receive_text()
            print(data)
            await webSocket.send_text(f"Message text was {data}")
    except WebSocketDisconnect:
        print("Disconnected Websocket. The end")
    except Exception as e:
        print("error is ", e)
        webSocket.close()