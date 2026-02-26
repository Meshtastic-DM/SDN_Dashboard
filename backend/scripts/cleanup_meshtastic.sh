#!/bin/bash
# Meshtastic Process Cleanup Script
# Kills all Meshtastic processes to recover from broken pipe errors

echo "================================================"
echo "Meshtastic Process Cleanup"
echo "================================================"
echo ""

echo "Searching for Meshtastic processes..."
PROCESSES=$(ps aux | grep -E 'meshtastic|Meshtasticator' | grep -v grep)

if [ -z "$PROCESSES" ]; then
    echo "✅ No Meshtastic processes found"
    exit 0
fi

echo "Found Meshtastic processes:"
echo "$PROCESSES"
echo ""

# Count processes
COUNT=$(echo "$PROCESSES" | wc -l)
echo "Total processes: $COUNT"
echo ""

# Ask for confirmation
read -p "Do you want to kill these processes? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Killing Meshtastic processes..."
    
    # Kill meshtastic CLI processes
    pkill -f "meshtastic" 2>/dev/null
    
    # Kill Meshtasticator processes
    pkill -f "Meshtasticator" 2>/dev/null
    
    # Give them a moment to terminate
    sleep 2
    
    # Check if any remain
    REMAINING=$(ps aux | grep -E 'meshtastic|Meshtasticator' | grep -v grep)
    
    if [ -z "$REMAINING" ]; then
        echo "✅ All processes killed successfully"
    else
        echo "⚠️  Some processes remain, attempting force kill..."
        pkill -9 -f "meshtastic" 2>/dev/null
        pkill -9 -f "Meshtasticator" 2>/dev/null
        sleep 1
        echo "✅ Force kill completed"
    fi
    
    echo ""
    echo "Next steps:"
    echo "  1. Restart your Meshtastic simulator/nodes"
    echo "  2. Verify ports are listening: ss -tulnp | grep program"
    echo "  3. Test with: python backend/scripts/check_meshtastic_health.py"
else
    echo "Cancelled - no processes killed"
fi

echo ""
