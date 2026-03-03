from fastapi import APIRouter, WebSocket, Request, HTTPException
from app.services.texting_service import send_text_message

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

@router.post("/send")
async def send_text(request: Request, destination: str, text: str):
    """API endpoint to send a text message via the Meshtastic interface"""
    try:
        send_text_message(request.app, destination, text)
        return {"status": "success", "message": f"Text message sent to {destination}"}
    except Exception as e:
        print(f"Error in send_text endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))