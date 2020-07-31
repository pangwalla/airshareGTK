#!/bin/bash -e

####################################
# Short installation script
# + Creates python virtual environment
# + Sources it
# + Configures .desktop file
# + Moves it to appropriate directory
#####################################

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
SCRIPT_PATH="$SCRIPT_DIR"/run.sh
ICON="$SCRIPT_DIR"/assets/Airshare.svg



if which virtualenv &>/dev/null; then
    virtualenv "$SCRIPT_DIR"/env > /dev/null
    echo "Installing python virtual env"
else
    echo -e "Quitting... \nPlease install virtualenv via your local package manager"
    exit 1
fi

source "$SCRIPT_DIR"/env/bin/activate
echo "Installing dependencies"
pip install -r "$SCRIPT_DIR"/requirements.txt > /dev/null

sed -i 's|Exec=.*$|Exec='"${SCRIPT_PATH}"'|g' airshare.desktop
sed -i 's|Icon=.*$|Icon='"${ICON}"'|g' airshare.desktop

cp "$SCRIPT_DIR"/airshare.desktop ~/.local/share/applications/

echo -e "\nInstallation finished."
