from fastapi import APIRouter, WebSocket, Request

router = APIRouter(prefix="/api/texting", tags=["texting"])

@router.websocket("/ws/texts")
async def ws_texts(ws: WebSocket):
    await ws.accept()
    broadcaster = ws.app.state.text_message_broadcaster  # Use separate broadcaster for texts
    broadcaster.register(ws)
    try:
        while True:
            await ws.receive_text()  # Keep connection open, ignore incoming messages
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        broadcaster.unregister(ws)