#!/bin/bash

SCRIPT_PATH=$0
if [ ! -e "$SCRIPT_PATH" ]; then
  case $SCRIPT_PATH in
    (*/*) exit 1;;
    (*) SCRIPT_PATH=$(command -v -- "$SCRIPT_PATH") || exit;;
  esac
fi
SCRIPT_DIR=$(
  cd -P -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P
) || exit
SCRIPT_PATH="$SCRIPT_DIR"/launch.py

source "$SCRIPT_DIR"/env/bin/activate
echo "launching airshare widget..."
python $SCRIPT_PATH
deactivate

PID=`pgrep launch.py`
if [ ! -z "$PID" ]; then
  kill -9 $PID
fi

if [ -f "$SCRIPT_DIR"/tmp/temp.png ]; then
  rm "$SCRIPT_DIR"/tmp/temp.png
fi
