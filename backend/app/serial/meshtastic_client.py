import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from app.services.db_update_service import update_nodes_db,update_message_db, get_messages_by_req_id_and_source
import asyncio
import os
import serial.tools.list_ports
import time
from datetime import datetime

def publish_text_to_websocket(app, message:dict):
    """Utility function to publish text message updates to the frontend via WebSocket"""
    broadcaster = app.state.text_message_broadcaster  # Use separate broadcaster for texts
    broadcaster.publish(message)
    print(f"Published text message to WebSocket: {message}")


def on_receive(packet, interface):
    """Callback function to handle incoming Meshtastic packets"""
    # print(f"Received packet: {packet}")
    # Extract relevant information from the packet
    if packet.get("decoded") is None:
        return  # Ignore packets that can't be decoded
    decoded = packet["decoded"]
    if decoded.get("portnum") == "TEXT_MESSAGE_APP":
        source_hex = hex(packet.get("from"))
        destination_hex = hex(packet.get("to"))
        # Convert hex to bytes for database (strip '0x' prefix)
        source_bytes = bytes.fromhex(source_hex[2:])
        destination_bytes = bytes.fromhex(destination_hex[2:])
        text = decoded.get("text")  # Remove trailing comma - it was creating a tuple!
        rssi = packet.get("rxRssi")
        id = packet.get("id")
        channel = packet.get("channel")
        timestamp_now = time.time()
        
        # Create a message dict for database (with bytes and datetime)
        message_db = {
            "source": source_bytes,
            "destination": destination_bytes,
            "text": text,
            "timestamp": datetime.fromtimestamp(timestamp_now),
            "rssi": rssi,
            "id": id,
            "channel": channel,
            "conversation": source_hex,
            "sent_by_me": False
        }
        
        # Create a message dict for WebSocket (with hex strings and float timestamp)
        message_ws = {
            "source": source_hex,
            "destination": destination_hex,
            "text": text,
            "timestamp": timestamp_now,
            "rssi": rssi,
            "id": id,
            "channel": channel,
            "conversation": source_hex
        }
        
        update_message_db(interface, message_db)  # Update the database with the new message
        # Publish the message to the frontend via WebSocket
        publish_text_to_websocket(interface.app, message_ws)
    
    elif decoded.get("portnum") == "TELEMETRY_APP":
        #print(f"Received telemetry packet: {decoded}")
        update_nodes_db(interface)

    elif decoded.get("portnum") == "ROUTING_APP":
        #print(f"Received routing packet: {packet}")
        routing = decoded.get("routing") or {}

        # This is the ID of the original packet being ACKed/NAKed
        req_id = decoded.get("requestId") or routing.get("request_id")
        
        # Convert source to bytes for database lookup
        if interface and interface.myInfo:
            source_int = interface.myInfo.my_node_num
            source_bytes = source_int.to_bytes(4, byteorder='big')
        else:
            return
            
        message = get_messages_by_req_id_and_source(req_id, source_bytes)  # Fetch message from database to update ACK status and timestamp
        if message is None:
            return
        # If present => NAK (delivery failed / no route / timeout etc.)
        error_reason = routing.get("errorReason") or routing.get("error_reason")

        status = "NAKED" if error_reason != "NONE" else "ACKED"

        message.ack_status = status
        message.ack_timestamp = datetime.fromtimestamp(time.time())
        update_message_db(interface, message.__dict__)  # Update message in database with new ACK status and timestamp
        # Push receipt update to frontend
        receipt_msg = {
            "type": "receipt",
            "request_id": req_id,
            "status": status,
            "from": hex(packet.get("from")) if packet.get("from") is not None else None,
            "timestamp": time.time(),
            "reason": str(error_reason) if error_reason is not None else None,
        }
        print(f"Message {req_id} was {status} by {receipt_msg['from']} at {receipt_msg['timestamp']} (reason: {receipt_msg['reason']})")


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
        
        app.state.meshtastic_interface = interface  # Store interface in app state for access in callbacks
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



def send_text_message_client(interface, destination, text):
    """Function to send a text message via the Meshtastic interface"""
    if not interface:
        print("⚠️  Cannot send message: Meshtastic interface not initialized.")
        return
    try:
        # Convert destination from string format (!6c7438c8) to integer
        if isinstance(destination, str):
            destination_int = int(destination.strip('!'), 16)
        else:
            destination_int = destination
            
        sent= interface.sendText(text, destinationId=destination_int, wantAck=True)
        interface.app.state.pending[sent.id] = {
            "destination": destination,
            "text": text,
            "status": "pending",
            "timestamp": time.time()
        }
        
        # Convert IDs to bytes for database
        source_bytes = interface.myInfo.my_node_num.to_bytes(4, byteorder='big')
        destination_bytes = destination_int.to_bytes(4, byteorder='big')
        
        message = {
            "id": sent.id,
            "source": source_bytes,
            "destination": destination_bytes,
            "text": text,
            "timestamp": datetime.fromtimestamp(time.time()),
            "conversation": hex(destination_int),
            "sent_by_me": True,
            "ack_status": "pending",
            "ack_timestamp": None
        }
        update_message_db(interface, message)  # Add sent message to database immediately
        print(f"✓ Sent message to {destination}: {text}")
    except Exception as e:
        print(f"⚠️  Error sending message: {e}")
        raise ValueError(f"Failed to send text message: {e}")
    
