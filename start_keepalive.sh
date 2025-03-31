#!/bin/bash

# Make sure the script is executable
chmod +x keep_alive.py

# Run the keep-alive script in the background
nohup python3 keep_alive.py > keep_alive_output.log 2>&1 &

echo "Keep-alive service started in the background"
echo "You can check the logs in keep_alive_standalone.log or keep_alive_output.log"