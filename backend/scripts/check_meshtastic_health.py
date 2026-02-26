#!/usr/bin/env python3
"""
Meshtastic Health Check Script
Checks the health of Meshtastic nodes and reports connection status.
Usage: python check_meshtastic_health.py
"""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.meshtastic_service import discover_meshtastic_ports, fetch_meshtastic_info


def check_port_listening(port: int) -> bool:
    """Check if a port is listening using ss command."""
    try:
        result = subprocess.run(
            f"wsl ss -tulnp | grep ':{port}'",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0 and str(port) in result.stdout
    except:
        return False


def test_connection(port: int) -> tuple[bool, str]:
    """Test connection to a Meshtastic node."""
    print(f"  Testing connection to port {port}...", end=" ")
    
    # Check if port is listening
    if not check_port_listening(port):
        return False, "Port not listening"
    
    # Try to fetch data
    node_data = fetch_meshtastic_info(port=port, timeout=8, retries=1)
    
    if node_data:
        owner = node_data.get("owner", "Unknown")
        node_count = len(node_data.get("nodes", {}))
        return True, f"OK - Owner: {owner}, {node_count} nodes in mesh"
    else:
        return False, "Connection failed or no data returned"


def main():
    """Main health check routine."""
    print("=" * 60)
    print("Meshtastic Node Health Check")
    print("=" * 60)
    print()
    
    # Discover active ports
    print("Step 1: Discovering active Meshtastic ports...")
    ports = discover_meshtastic_ports(min_port=4403, use_wsl=True)
    
    if not ports:
        print("❌ No Meshtastic ports discovered!")
        print()
        print("Troubleshooting steps:")
        print("  1. Ensure Meshtastic simulator/nodes are running")
        print("  2. Check WSL is accessible: wsl echo test")
        print("  3. Run manually: wsl ss -tulnp | grep program")
        return
    
    print(f"✅ Found {len(ports)} active port(s): {ports}")
    print()
    
    # Test each port
    print("Step 2: Testing connections...")
    healthy_nodes = []
    unhealthy_nodes = []
    
    for port in ports:
        success, message = test_connection(port)
        if success:
            print(f"✅ {message}")
            healthy_nodes.append(port)
        else:
            print(f"❌ {message}")
            unhealthy_nodes.append(port)
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Healthy nodes: {len(healthy_nodes)}")
    print(f"Unhealthy nodes: {len(unhealthy_nodes)}")
    
    if unhealthy_nodes:
        print()
        print("⚠️  Unhealthy nodes detected!")
        print(f"   Ports: {unhealthy_nodes}")
        print()
        print("Recommended actions:")
        print("  1. Check logs of affected nodes")
        print("  2. Restart nodes if showing 'Broken pipe' errors")
        print("  3. Kill zombie processes: pkill -f meshtastic")
        print("  4. Restart your Meshtastic simulator")
    else:
        print()
        print("✅ All nodes are healthy!")
    
    print()


if __name__ == "__main__":
    main()
