# app/meshtastic_service.py
"""Service to fetch and parse Meshtastic node information."""
import subprocess
import json
import re
from typing import Dict, Any, List, Optional


def fetch_meshtastic_info(host: str = "127.0.0.1", port: int = 4403) -> Optional[Dict[str, Any]]:
    """
    Fetch Meshtastic node information via CLI.
    
    Args:
        host: TCP host address
        port: TCP port number
    
    Returns:
        Parsed node information dictionary or None if failed
    """
    try:
        # Run meshtastic CLI command
        cmd = f"meshtastic --tcp {host}:{port} --info"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"Error fetching from {host}:{port}: {result.stderr}")
            return None
            
        return parse_meshtastic_output(result.stdout)
    
    except subprocess.TimeoutExpired:
        print(f"Timeout connecting to {host}:{port}")
        return None
    except Exception as e:
        print(f"Exception fetching Meshtastic data: {e}")
        return None


def parse_meshtastic_output(output: str) -> Dict[str, Any]:
    """
    Parse the meshtastic --info output into structured data.
    
    Args:
        output: Raw CLI output string
    
    Returns:
        Structured dictionary with parsed information
    """
    data = {
        "owner": None,
        "myInfo": {},
        "metadata": {},
        "nodes": {},
        "preferences": {},
        "modulePreferences": {},
        "channels": [],
        "primaryChannelUrl": None
    }
    
    lines = output.split('\n')
    current_section = None
    buffer = ""
    
    for line in lines:
        # Skip connection messages and warnings
        if line.startswith("Connected to") or line.startswith("***"):
            continue
            
        # Detect sections
        if line.startswith("Owner:"):
            data["owner"] = line.replace("Owner:", "").strip()
        elif line.startswith("My info:"):
            current_section = "myInfo"
            buffer = line.replace("My info:", "").strip()
        elif line.startswith("Metadata:"):
            if current_section == "myInfo" and buffer:
                data["myInfo"] = safe_parse_json(buffer)
            current_section = "metadata"
            buffer = line.replace("Metadata:", "").strip()
        elif line.startswith("Nodes in mesh:"):
            if current_section == "metadata" and buffer:
                data["metadata"] = safe_parse_json(buffer)
            current_section = "nodes"
            buffer = ""
        elif line.startswith("Preferences:"):
            if current_section == "nodes" and buffer:
                data["nodes"] = safe_parse_json(buffer)
            current_section = "preferences"
            buffer = ""
        elif line.startswith("Module preferences:"):
            if current_section == "preferences" and buffer:
                data["preferences"] = safe_parse_json(buffer)
            current_section = "modulePreferences"
            buffer = ""
        elif line.startswith("Channels:"):
            if current_section == "modulePreferences" and buffer:
                data["modulePreferences"] = safe_parse_json(buffer)
            current_section = "channels"
            buffer = ""
        elif line.startswith("Primary channel URL:"):
            if current_section == "channels":
                # Process any buffered channel data
                pass
            data["primaryChannelUrl"] = line.replace("Primary channel URL:", "").strip()
            current_section = None
        elif line.strip().startswith("Index"):
            # Parse channel info
            channel_match = re.search(r'Index (\d+): (\w+) (.+)', line)
            if channel_match:
                idx, name, rest = channel_match.groups()
                channel_data = safe_parse_json("{" + rest.split("{", 1)[1] if "{" in rest else "{}")
                data["channels"].append({
                    "index": int(idx),
                    "name": name,
                    **channel_data
                })
        else:
            # Accumulate JSON data
            if current_section and line.strip():
                buffer += line.strip()
    
    # Process any remaining buffer
    if current_section == "modulePreferences" and buffer:
        data["modulePreferences"] = safe_parse_json(buffer)
    
    return data


def safe_parse_json(json_str: str) -> Dict[str, Any]:
    """Safely parse JSON string, return empty dict on failure."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return {}


def fetch_all_nodes(node_ports: List[int] = [4403, 4404, 4405, 4406, 4407]) -> List[Dict[str, Any]]:
    """
    Fetch information from multiple Meshtastic nodes.
    
    Args:
        node_ports: List of TCP ports to query
    
    Returns:
        List of node information dictionaries
    """
    all_nodes = []
    
    for port in node_ports:
        node_data = fetch_meshtastic_info(port=port)
        if node_data:
            node_data["port"] = port
            all_nodes.append(node_data)
    
    return all_nodes


def format_node_for_display(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format node data for frontend display with human-readable values.
    
    Args:
        node_data: Raw node data from parse_meshtastic_output
    
    Returns:
        Formatted data for display
    """
    my_info = node_data.get("myInfo", {})
    metadata = node_data.get("metadata", {})
    nodes = node_data.get("nodes", {})
    
    # Extract owner node info
    my_node_num = my_info.get("myNodeNum")
    owner_node = None
    mesh_nodes = []
    
    for node_id, node_info in nodes.items():
        formatted_node = {
            "id": node_id,
            "num": node_info.get("num"),
            "user": node_info.get("user", {}),
            "position": node_info.get("position", {}),
            "deviceMetrics": node_info.get("deviceMetrics", {}),
            "snr": node_info.get("snr"),
            "hopsAway": node_info.get("hopsAway"),
            "isFavorite": node_info.get("isFavorite", False)
        }
        
        if node_info.get("num") == my_node_num:
            owner_node = formatted_node
        else:
            mesh_nodes.append(formatted_node)
    
    return {
        "port": node_data.get("port"),
        "owner": node_data.get("owner"),
        "myInfo": my_info,
        "metadata": metadata,
        "ownerNode": owner_node,
        "meshNodes": mesh_nodes,
        "nodeCount": len(nodes),
        "preferences": node_data.get("preferences", {}),
        "modulePreferences": node_data.get("modulePreferences", {}),
        "channels": node_data.get("channels", []),
        "primaryChannelUrl": node_data.get("primaryChannelUrl")
    }
