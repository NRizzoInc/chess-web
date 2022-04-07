#!/bin/bash
# this script enables user to run the code in this repo using the virtual environment

# Get paths to everything
virtualEnvironName="web-games-venv"
rootDir="$(readlink -fm $0/..)"
virtualEnvironDir="${rootDir}/${virtualEnvironName}"
srcPath="${rootDir}/src"
backendPath="${srcPath}/backend"
executePath="${backendPath}/main.py"
setupScript="${rootDir}/install/setup.sh"

# check OS... (decide how to call python)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # windows
    venvPath="${virtualEnvironDir}/Scripts/python.exe"
else
    # linux
    venvPath="${virtualEnvironDir}/bin/python" # NOTE: don't use ".exe"
fi

# use "$@" to pass on all parameter the same way to python script
ARGS=$@

# check if venv is setup, if not inform user to run install
if [[ -f ${venvPath} ]]; then
    echo "Using virtual environment ${venvPath}"
else
    echo "Virtual environment not setup. Run ${setupScript}"
    exit
fi


echo "Starting Program ${executePath}"
# use -u to run python unbuffered (service wont print to syslog otherwise)
"${venvPath}" -u "${executePath}" $ARGS
