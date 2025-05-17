#!/bin/bash

# Function to clean up and release wake lock on exit
cleanup() {
    echo "Releasing wake lock and exiting..."

    # For Linux (using systemd-inhibit)
    if pgrep -x "systemd-inhibit" >/dev/null; then
        pkill -f "systemd-inhibit"
    fi

    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM EXIT

# Linux with systemd
stay_awake=false
for arg in "$@"; do
    if [ "$arg" = "--stay-awake" ]; then
        stay_awake=true
        break
    fi
done

if $stay_awake; then
    echo "Acquiring wake lock..."
    systemd-inhibit --what=sleep:idle --who="$0" --why="Running sequential Python scripts" --mode=block sleep infinity &
    INHIBIT_PID=$!
    echo "Wake lock acquired (PID: $INHIBIT_PID)"
fi

echo "Starting study."

# Run Python scripts in sequence with sleep between them
echo "Caching The Islands..."
python3 cache.py
echo "Caching completed"

echo "Finding paricipants..."
python3 find_participants.py 100 18 75
echo "Participants found"

echo "Getting participants info..."
python3 collect_participant_info.py
echo "Participant info collected"

echo "Giving initial tasks..."
python3 do_task.py ruler
echo "Initial tasks are underway"

echo "Sleeping to let tasks complete..."
sleep 60

echo "Collecting initial task results..."
python3 collect_latest_result.py
echo "Initial tasks results collected"

echo "Giving cannabis task..."
python3 do_task.py cannabis
echo "Cannabis is being consumed"

echo "Waiting for 45 minutes..."
sleep 2700

echo "Giving ruler task..."
python3 do_task.py ruler
echo "Rulers are being dropped"

echo "Collecting results..."
python3 collect_latest_result.py
echo "Results collected"

echo "Sleeping..."
sleep 6000

echo "Giving ruler task..."
python3 do_task.py ruler
echo "Rulers are being dropped"

echo "Collecting results..."
python3 collect_latest_result.py
echo "Results collected"

echo "All scripts executed successfully"
