import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from app.services.texting_service import publish_text_to_websocket
from app.services.node_service import update_nodes_db
import asyncio
import os
import serial.tools.list_ports

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
    
    if decoded.get("portnum") == "TELEMETRY_APP":
        #print(f"Received telemetry packet: {decoded}")
        update_nodes_db(interface)

def get_meshtastic_port():
    ports: meshtastic.serial_interface.List[str] = meshtastic.util.findPorts(True)
    return ports

def start_meshtastic_client(app, devPath=None):
    """Function to start the Meshtastic client and listen for packets"""
    # If no port specified, try to detect it
    if not devPath:
        ports = get_meshtastic_port()
        if len(ports) == 0:
            raise ValueError("No Meshtastic-compatible serial ports found. Please connect a device or specify the port using the MESHTASTIC_PORT environment variable.")
            return
        elif len(ports) > 1:
            print(f"Multiple potential Meshtastic ports found: {ports}")
            return
    try:
        # Create interface with specified port
        if devPath:
            interface = meshtastic.serial_interface.SerialInterface(devPath=devPath)
        else:
            interface = meshtastic.serial_interface.SerialInterface()
        
        interface.app = app  # Attach app reference for WebSocket publishing
        pub.subscribe(on_receive, "meshtastic.receive")
        print(f"✓ Meshtastic client started on {devPath} and listening for packets...")
        update_nodes_db(interface)  # Initial fetch of nodes to populate database
    except SystemExit as e:
        # Catch sys.exit() calls from Meshtastic library
        print(f"⚠️  Meshtastic client failed to start (SystemExit: {e})")
        print(f"   Check that {devPath} is the correct port and device is connected.")
        raise ValueError(f"Meshtastic client failed to start: {e}")
    except Exception as e:
        print(f"⚠️  Error starting Meshtastic client: {e}")
        print(f"   Application will continue without Meshtastic integration.")
        raise ValueError(f"Meshtastic client failed to start: {e}")