
from app.core.database import SessionLocal
from app.models.node import Node


def update_nodes_db(iface):
    """Function to fetch all nodes from the Meshtastic network and update the database"""
    nodes = iface.nodes
    db = SessionLocal()
    try:
        for node_id, node_data in nodes.items():
            # Convert node_id from string format '!6c7438c8' to bytes
            node_id_bytes = bytes.fromhex(node_id.strip('!'))
            
            # Check if node already exists in database
            existing_node = db.query(Node).filter(Node.id == node_id_bytes).first()
            
            # Extract data from node_data
            user_info = node_data.get('user', {})
            device_metrics = node_data.get('deviceMetrics', {})
            
            if existing_node:
                # Update existing node
                existing_node.long_name = user_info.get('longName')
                existing_node.hw_model = user_info.get('hwModel')
                existing_node.public_key = user_info.get('publicKey')
                existing_node.snr = node_data.get('snr')
                existing_node.battery_level = device_metrics.get('batteryLevel')
                existing_node.status = 'online' if node_data.get('lastHeard') else 'offline'
                existing_node.hops_away = node_data.get('hopsAway')
                print(f"Updated node: {node_id}")
            else:
                # Create new node
                new_node = Node(
                    id=node_id_bytes,
                    long_name=user_info.get('longName'),
                    hw_model=user_info.get('hwModel'),
                    public_key=user_info.get('publicKey'),
                    snr=node_data.get('snr'),
                    battery_level=device_metrics.get('batteryLevel'),
                    status='online' if node_data.get('lastHeard') else 'offline',
                    hops_away=node_data.get('hopsAway')
                )
                db.add(new_node)
                print(f"Created new node: {node_id}")
        
        db.commit()
        print(f"Successfully processed {len(nodes)} nodes")
    except Exception as e:
        db.rollback()
        print(f"Error updating nodes database: {e}")
    finally:
        db.close() 
