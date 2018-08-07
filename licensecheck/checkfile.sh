#!/usr/bin/env bash

export name="$3"
export name=${name##../../client-data/}

grep "$name" $1 >/dev/null
if [ "$?" != 0 ]; then
    grep "$name " $2 >/dev/null
    if [ "$?" != 0 ]; then
        echo "Missing license for $name"
    fi
fi
