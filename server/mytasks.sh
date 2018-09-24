#!/bin/bash

# Detect automatically the base dir of the rvt2
if hash greadlink 2>/dev/null ; then
  # OSX
  READLINK=greadlink
else
  # Linux
  READLINK=readlink
fi
if [ -z "$MYTASKSHOME" ]; then
    MYTASKSHOME=$(dirname $($READLINK -f "$0"))
    if [ ! -e "$MYTASKSHOME/$0" ]; then
        echo 'I cannot automatically find the root directory of MYTASKS. Please, define the variable MYTASKSHOME'
        exit 1
    fi
fi

# check if a virtual environment inside the project exists. If not, create it
MYPYTHON="$MYTASKSHOME/.venv/bin/python"
if [ ! -e "$MYPYTHON" ]; then
    (
        cd $MYTASKSHOME
        env PIPENV_VENV_IN_PROJECT=1 pipenv --python /usr/bin/python3
        #env PIPENV_VENV_IN_PROJECT=1 pipenv --three
        pipenv install
    )
fi

if [ -z "$1" ]; then
    (
        cd $MYTASKSHOME
        export FLASK_ENV="depelopment"
        export FLASK_APP="manage"
        export FLASK_DEBUG=True
        if [ -e config.py ]; then
            export APP_SETTINGS="config.MytasksConfig"
        fi
        .venv/bin/flask run
    )
else
    (
        cd $MYTASKSHOME
        export FLASK_APP="manage"
        if [ -e config.py ]; then
            export APP_SETTINGS="config.MytasksConfig"
        fi
        .venv/bin/flask "$@"
    )
fi
