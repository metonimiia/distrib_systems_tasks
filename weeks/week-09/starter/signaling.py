from collections import defaultdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Simple WebRTC Signaling")

# room_id -> set of connected sockets
rooms: dict[str, set[WebSocket]] = defaultdict(set)


@app.get("/")
def root():
    return {"status": "ok", "message": "Signaling server is running"}


@app.websocket("/ws/{room_id}")
async def ws_signaling(websocket: WebSocket, room_id: str):
    await websocket.accept()
    rooms[room_id].add(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            # Пересылаем сигнал всем участникам комнаты, кроме отправителя.
            for peer in list(rooms[room_id]):
                if peer is websocket:
                    continue
                await peer.send_text(message)
    except WebSocketDisconnect:
        pass
    finally:
        rooms[room_id].discard(websocket)
        if not rooms[room_id]:
            rooms.pop(room_id, None)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
