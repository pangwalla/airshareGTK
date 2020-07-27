#!/bin/bash

# virtualenv env
# source env/bin/activate
# pip install -r requirements.txt

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
prg="$dir"/run.sh
icon="$dir"/assets/Airshare.svg

sed -i 's|Exec=.*$|Exec='"${prg}"'|g' airshare.desktop
sed -i 's|Icon=.*$|Icon='"${icon}"'|g' airshare.desktop

cp airshare.desktop ~/.local/share/applications/

echo ""
echo ""
echo "Installation finished"
