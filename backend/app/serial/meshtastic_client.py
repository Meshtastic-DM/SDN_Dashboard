import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from app.services.texting_service import publish_text_to_websocket
from app.services.node_service import update_nodes_db
import asyncio

def on_receive(packet, interface):
    """Callback function to handle incoming Meshtastic packets"""
    # print(f"Received packet: {packet}")
    # Extract relevant information from the packet
    if packet.get("decoded") is None:
        return  # Ignore packets that can't be decoded
    decoded = packet["decoded"]
    if decoded.get("portnum") == "TEXT_MESSAGE_APP":
        source = packet.get("from")
        destination = packet.get("to")
        text = decoded.get("text"),
        rssi = packet.get("rxRssi")
        # Create a message dict to send to the frontend
        message = {
            "source": source,
            "destination": destination,
            "text": text,
            "timestamp": packet.get("timestamp"),
            "rssi": rssi,
        }

        # Publish the message to the frontend via WebSocket
        publish_text_to_websocket(interface.app, message)

def start_meshtastic_client(app,port = None,baudrate = None):
    """Function to start the Meshtastic client and listen for packets"""
    app.state.text_message_broadcaster.set_loop(asyncio.get_running_loop())
    if port and baudrate:
        interface = meshtastic.serial_interface.SerialInterface(port=port, baudrate=baudrate)
    else:
        interface = meshtastic.serial_interface.SerialInterface()
    interface.app = app  # Attach app reference for WebSocket publishing
    pub.subscribe(on_receive, "meshtastic.receive")
    print("Meshtastic client started and listening for packets...")
    update_nodes_db(interface)  # Initial fetch of nodes to populate database