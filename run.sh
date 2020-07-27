#!/bin/bash

prg=$0
if [ ! -e "$prg" ]; then
  case $prg in
    (*/*) exit 1;;
    (*) prg=$(command -v -- "$prg") || exit;;
  esac
fi
dir=$(
  cd -P -- "$(dirname -- "$prg")" && pwd -P
) || exit
prg="$dir"/launch.py

source "$dir"/env/bin/activate
echo "launching airshare widget..."
python $prg
deactivate

PID=`pgrep launch.py`
if [ ! -z "$PID" ]; then
  kill -9 $PID
fi

if [ -f "$dir"/tmp/temp.png ]; then
  rm "$dir"/tmp/temp.png
fi
