def publish_text_to_websocket(app, message:dict):
    """Utility function to publish text message updates to the frontend via WebSocket"""
    broadcaster = app.state.text_message_broadcaster  # Use separate broadcaster for texts
    broadcaster.publish(message)
    print(f"Published text message to WebSocket: {message}")