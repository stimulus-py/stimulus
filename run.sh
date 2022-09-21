#!/bin/sh

if [ -f /stimulus/user/config/requirements.txt ]; then
    pip install $PIP_FLAGS -r /stimulus/user/config/requirements.txt
fi

if [ "$DEBUG" = "ON" ]; then
    echo "Running with debug on"
    python -m debugpy --listen 0.0.0.0:3000 ./src/start_stimulus.py
elif [ "$DEBUG" "HOLD" ]; then
    echo "Running with debug hold"
    python -m debugpy --listen 0.0.0.0:3000 --wait-for-client ./src/start_stimulus.py
else
    python ./src/start_stimulus.py    
fi

