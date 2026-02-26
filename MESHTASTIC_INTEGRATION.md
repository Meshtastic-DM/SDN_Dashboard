# Meshtastic Integration Guide

## Overview
The SDN Dashboard includes **instant port discovery** for Meshtastic mesh network nodes using the `ss` command. This discovers all active nodes in milliseconds without port scanning overhead.

## How It Works

### Discovery Method: `ss` Command
Instead of slow port scanning, the system uses Linux's `ss` (socket statistics):

```bash
# On Windows (via WSL)
wsl ss -tulnp

# On Linux
ss -tulnp
```

**Sample output:**
```
tcp  LISTEN  0  5  0.0.0.0:4405  0.0.0.0:*  users:(("program",pid=1236,fd=11))
tcp  LISTEN  0  5  0.0.0.0:4404  0.0.0.0:*  users:(("program",pid=1219,fd=11))
tcp  LISTEN  0  5  0.0.0.0:4403  0.0.0.0:*  users:(("program",pid=1199,fd=11))
```

The system:
1. ⚡ Runs `ss -tulnp` (instant, ~50ms)
2. 🔍 Filters for "program" processes (Meshtastic nodes)
3. 📊 Extracts port numbers >= 4403
4. 🔌 Queries only those ports with `meshtastic --info`

**Benefits:**
- ✅ **Instant discovery** - No matter how many nodes
- ✅ **Zero port scanning** - No timeouts or delays
- ✅ **Accurate filtering** - Only actual Meshtastic processes
- ✅ **Scales infinitely** - 10 nodes or 1000 nodes, same speed

## Setup

### 1. Prerequisites
- Python virtual environment with `meshtastic` package installed:
  ```bash
  pip install meshtastic
  ```

### 2. WSL Configuration (Windows Only)
Since you're using WSL with port forwarding, ensure:
- WSL is accessible from Windows
- Ports are forwarded (already done if you can connect to nodes)
- `ss` command is available in WSL (it's installed by default)

Test discovery manually:
```bash
wsl ss -tulnp | grep program
```

### 3. Start Your Meshtastic Nodes
Ensure your Meshtastic nodes are running and accessible via TCP:
```bash
# Example: Start a node on port 4403
meshtastic --tcp 127.0.0.1:4403
```

## Features

### Extended Node View
Access the Extended Node View from the sidebar to see:

#### System Information
- Node number and device ID
- Firmware version
- Hardware model (PORTDUINO, etc.)
- Device role (CLIENT, ROUTER, etc.)
- Reboot count

#### Owner Node Details
- Node ID and names (long/short)
- MAC address
- Battery level with visual indicators
- Uptime duration
- Channel utilization
- GPS coordinates (if available)

#### Mesh Nodes
View all nodes in the mesh network with:
- Node identification (ID, names, hardware)
- **Hops Away** - Direct connection or multi-hop distance
- **SNR (Signal-to-Noise Ratio)** - Signal quality indicator
  - Good: ≥ -5 dB
  - Medium: -12 to -5 dB
  - Poor: < -12 dB
- GPS position

#### Configuration (Collapsible Sections)
- **Device Preferences** - Node settings, broadcast intervals, GPIO pins
- **LoRa Configuration** - Radio settings, modem preset, hop limits, region
- **Module Preferences** - MQTT, telemetry, audio, and other module configs

## API Endpoints

### Auto-Discovery (Default & Recommended)
```
GET http://localhost:8000/api/meshtastic/nodes
```

Uses `ss` command to instantly discover all active Meshtastic nodes.

**Query Parameters:**
- `min_port` (optional) - Minimum port number (default: 4403)
- `use_wsl` (optional) - Use WSL on Windows (default: true)

**Examples:**
```bash
# Auto-discover all nodes (instant)
curl http://localhost:8000/api/meshtastic/nodes

# Discover nodes on ports >= 5000
curl http://localhost:8000/api/meshtastic/nodes?min_port=5000

# Use native Linux (no WSL)
curl http://localhost:8000/api/meshtastic/nodes?use_wsl=false
```

**Response:**
```json
{
  "count": 4,
  "nodes": [...],
  "discoveryMode": "auto"
}
```

### Manual Port Selection
```
GET http://localhost:8000/api/meshtastic/nodes?ports=4403,4404,4405
```

Specify exact ports (comma-separated). Discovery is skipped.

**Response:**
```json
{
  "count": 3,
  "nodes": [...],
  "discoveryMode": "manual"
}
```

### Port Discovery Only
```
GET http://localhost:8000/api/meshtastic/discover
```

Fast port discovery without fetching full node data (~50ms).

**Query Parameters:**
- `min_port` (optional) - Minimum port (default: 4403)
- `use_wsl` (optional) - Use WSL (default: true)

**Example:**
```bash
curl http://localhost:8000/api/meshtastic/discover
```

**Response:**
```json
{
  "activePorts": [4403, 4404, 4405, 4406],
  "count": 4,
  "method": "ss command"
}
```

### Single Node Query
```
GET http://localhost:8000/api/meshtastic/node/{port}
```

**Example:**
```
GET http://localhost:8000/api/meshtastic/node/4403
```

## UI Features

### Auto-Refresh
- Manual refresh button available (click to fetch latest data)

### Visual Indicators
- 🔋 Battery status with color coding
- 📶 Signal strength indicators
- 🔌 Connection status badges
- 📍 GPS coordinates when available

### Collapsible Sections
Click on preference sections to expand/collapse detailed configuration information.

## Troubleshooting

### No Nodes Discovered
1. **Test `ss` command manually**:
   ```bash
   wsl ss -tulnp | grep program
   ```
   You should see lines with port numbers (e.g., `:4403`, `:4404`)

2. **Verify nodes are running**: Check your Meshtastic simulator is active

3. **Check WSL access**: Ensure WSL commands work from Windows:
   ```bash
   wsl echo "test"
   ```

4. **Try manual port specification**:
   ```
   GET /api/meshtastic/nodes?ports=4403,4404
   ```

### "Error sending packet to radio!! ([Errno 32] Broken pipe)"
This error occurs when the Meshtastic TCP connection is interrupted or closed unexpectedly.

**Causes:**
- Network interruption or timeout
- Meshtastic simulator/device restarted or crashed
- Too many simultaneous connections
- TCP socket closed while heartbeat thread is still active

**Solutions:**
1. **Restart the Meshtastic simulator/nodes**:
   ```bash
   # Kill existing processes
   pkill -f meshtastic
   
   # Or find and kill specific PIDs
   ps aux | grep meshtastic
   kill <PID>
   
   # Restart your nodes
   # (use your specific startup command)
   ```

2. **Check for connection conflicts**:
   - Only one client should maintain persistent connections
   - The FastAPI backend uses CLI commands (stateless, no persistent connections)
   - Ensure no other scripts are holding open connections

3. **Connection recovery**:
   The backend now includes automatic retry logic:
   - 2 retry attempts per failed connection
   - 8-second timeout per attempt
   - Graceful handling of broken pipes
   
   If you continue seeing errors in the Meshtastic process logs, they won't affect the dashboard queries.

4. **Long-term fix** (for external Meshtastic processes):
   Add connection recovery in your Meshtastic integration:
   ```python
   import meshtastic
   from meshtastic.tcp_interface import TCPInterface
   
   def get_connection_with_retry(host, retries=3):
       for attempt in range(retries):
           try:
               return TCPInterface(hostname=host)
           except BrokenPipeError:
               if attempt < retries - 1:
                   time.sleep(2)
                   continue
               raise
   ```

5. **Check simulator health**:
   ```bash
   # Check if ports are still listening
   wsl ss -tulnp | grep program
   
   # Test connection manually
   meshtastic --tcp 127.0.0.1:4403 --info
   ```

**Note**: These errors come from the Meshtastic library's heartbeat thread, not your backend code. The dashboard's improved error handling will gracefully skip unavailable nodes and continue with successful connections.

### "Error running ss command"
- **On Linux**: Ensure `ss` is installed (it should be by default)
- **On Windows**: Ensure WSL is properly set up
- **Fallback**: Use manual mode with known ports

### Node Data Not Fetching
- **Check meshtastic CLI**: Test manually:
  ```bash
  meshtastic --tcp 127.0.0.1:4403 --info
  ```
- **Timeout issues**: Nodes may be busy or unresponsive
- **WSL port forwarding**: Ensure ports are properly forwarded to Windows

### Performance Issues
The `ss` command approach is already optimal (~50ms). If still slow:
- Check network latency to WSL
- Verify meshtastic CLI is in PATH
- Consider caching node data on frontend

## Development

### File Structure
```
backend/app/
  └── meshtastic_service.py    # Discovery & data fetching
  └── main.py                   # API endpoints

frontend/sdn-dashboard/src/
  └── components/
      ├── ExtendedNodeView.jsx  # React component
      └── ExtendedNodeView.css  # Styles
  └── pages/
      └── DashboardPage.jsx     # Integration
```

### Key Functions

**`discover_meshtastic_ports()`** - Uses `ss` command for instant discovery
```python
# Returns: [4403, 4404, 4405, 4406]
ports = discover_meshtastic_ports(min_port=4403, use_wsl=True)
```

**`fetch_all_nodes()`** - Auto-discovery + data fetching
```python
# Auto mode (uses ss discovery)
nodes = fetch_all_nodes(auto_discover=True)

# Manual mode (specific ports)
nodes = fetch_all_nodes(node_ports=[4403, 4404], auto_discover=False)
```

### Testing Discovery

Test port discovery from command line:
```bash
# Windows (via WSL)
wsl ss -tulnp | grep program

# Python test
python -c "from app.meshtastic_service import discover_meshtastic_ports; print(discover_meshtastic_ports())"
```

### Customization
- Change `min_port` in API calls to start from different port
- Modify regex pattern in `discover_meshtastic_ports()` to match different process names
- Adjust `use_wsl` parameter for native Linux environments
- Frontend refresh is manual only (no auto-polling to avoid connection conflicts)
