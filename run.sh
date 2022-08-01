#!/bin/sh

if [ -f /stimulus/user/config/requirements.txt ]; then
    pip install $PIP_FLAGS -r /stimulus/user/config/requirements.txt
fi

python ./src/start_stimulus.py
