#!/bin/bash
COUNT=1000
for i in $(seq $COUNT); do
    # Run the Python script in the background using '&' and 'nohup'
    source /home/jthu/Documents/easy_comm/.venv/bin/activate
    nohup python async_client.py > /dev/null 2>&1 &
    sleep 0.01
done
echo "Started $COUNT Python instances."
