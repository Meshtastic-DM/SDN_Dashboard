# Meshtastic Utility Scripts

This directory contains utility scripts for managing and troubleshooting Meshtastic connections.

## Available Scripts

### 1. Health Check Script (`check_meshtastic_health.py`)

Diagnoses connection issues with Meshtastic nodes.

**Usage:**
```bash
cd backend
python scripts/check_meshtastic_health.py
```

**What it does:**
- Discovers all active Meshtastic ports
- Tests connection to each node
- Reports health status and any issues
- Provides troubleshooting recommendations

**Example Output:**
```
============================================================
Meshtastic Node Health Check
============================================================

Step 1: Discovering active Meshtastic ports...
Discovered 3 Meshtastic node(s) on ports: [4403, 4404, 4405]
✅ Found 3 active port(s): [4403, 4404, 4405]

Step 2: Testing connections...
  Testing connection to port 4403... ✅ OK - Owner: Node1, 5 nodes in mesh
  Testing connection to port 4404... ✅ OK - Owner: Node2, 5 nodes in mesh
  Testing connection to port 4405... ❌ Connection failed or no data returned

============================================================
Summary
============================================================
Healthy nodes: 2
Unhealthy nodes: 1

⚠️  Unhealthy nodes detected!
   Ports: [4405]

Recommended actions:
  1. Check logs of affected nodes
  2. Restart nodes if showing 'Broken pipe' errors
  3. Kill zombie processes: pkill -f meshtastic
  4. Restart your Meshtastic simulator
```

### 2. Cleanup Script (`cleanup_meshtastic.sh`)

Safely kills all Meshtastic processes to recover from broken pipe errors.

**Usage:**
```bash
# On Linux/WSL
bash backend/scripts/cleanup_meshtastic.sh

# Or make it executable first
chmod +x backend/scripts/cleanup_meshtastic.sh
./backend/scripts/cleanup_meshtastic.sh
```

**What it does:**
- Searches for all running Meshtastic processes
- Shows you what will be killed
- Asks for confirmation before proceeding
- Kills processes gracefully (with force kill fallback)
- Provides next steps after cleanup

**Example Output:**
```
================================================
Meshtastic Process Cleanup
================================================

Searching for Meshtastic processes...
Found Meshtastic processes:
user  1234  0.1  0.2  123456  12345 ?  Sl  10:00  0:01 python meshtasticator.py
user  1235  0.1  0.2  123456  12345 ?  Sl  10:00  0:01 meshtastic --tcp 127.0.0.1:4403

Total processes: 2

Do you want to kill these processes? (y/N): y
Killing Meshtastic processes...
✅ All processes killed successfully

Next steps:
  1. Restart your Meshtastic simulator/nodes
  2. Verify ports are listening: ss -tulnp | grep program
  3. Test with: python backend/scripts/check_meshtastic_health.py
```

## Troubleshooting "Broken Pipe" Errors

When you see errors like:
```
Error sending packet to radio!! ([Errno 32] Broken pipe)
BrokenPipeError: [Errno 32] Broken pipe
```

**Quick fix:**
1. Run the cleanup script to kill stuck processes
2. Restart your Meshtastic simulator
3. Run the health check to verify recovery

**Step by step:**
```bash
# 1. Clean up broken processes
bash backend/scripts/cleanup_meshtastic.sh

# 2. Restart your Meshtastic simulator
# (Use your specific command, e.g.,)
# python ~/Meshtastic/Meshtasticator/meshtasticator.py

# 3. Wait a few seconds, then check health
python backend/scripts/check_meshtastic_health.py

# 4. If healthy, test the dashboard
curl http://localhost:8000/api/meshtastic/discover
```

## Common Issues

### "No Meshtastic ports discovered"
- **Cause**: Simulator not running or ports not forwarded
- **Fix**: Start your Meshtastic simulator and verify with `wsl ss -tulnp | grep program`

### "Connection failed or no data returned"  
- **Cause**: Node is listening but not responding (broken pipe, crashed, etc.)
- **Fix**: Use cleanup script to kill and restart the affected node

### "WSL command not found" (Windows only)
- **Cause**: WSL not installed or not in PATH
- **Fix**: Ensure WSL is properly set up: `wsl echo test`

## Advanced Usage

### Health Check with Custom Port Range
Edit `check_meshtastic_health.py` and modify:
```python
ports = discover_meshtastic_ports(min_port=5000, use_wsl=True)  # Start from port 5000
```

### Manual Process Kill
```bash
# Find Meshtastic processes
ps aux | grep meshtastic

# Kill specific PID
kill <PID>

# Or kill all at once
pkill -f meshtastic
```

### Check Specific Port
```bash
# Test if port is listening
ss -tulnp | grep ':4403'

# Test connection
meshtastic --tcp 127.0.0.1:4403 --info
```

## Integration with Dashboard

The SDN Dashboard backend automatically uses the improved connection handling:
- Automatic retry logic (2 attempts)
- 8-second timeout per attempt
- Graceful handling of broken connections
- Detailed error logging

These scripts are for **manual troubleshooting** of the external Meshtastic simulator processes, not the dashboard itself.
