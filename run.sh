#!/bin/bash

source env/bin/activate
echo "launching airshare widget..."
python launch.py
deactivate

PID=`pgrep launch.py`
kill -9 $PID

if [ -f tmp/temp.png ]; then
  rm tmp/temp.png
fi
