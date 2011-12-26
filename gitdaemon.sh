#!/bin/bash
#python -m gitdaemon
PYTHONPATH=$(pwd)
twistd -noy gitdaemon/gitdaemon.tac
echo $PYTHONPATH
