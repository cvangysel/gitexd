#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
KEY="$DIR/keys/$GIT_SSH_KEY"
chmod go-rxw $KEY
ssh -i $KEY $1 $2 $3 $4