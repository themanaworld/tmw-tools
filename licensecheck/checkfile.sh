#!/usr/bin/env bash

export name="$2"
export name=${name##../../client-data/}

grep " $name " $1 >/dev/null
if [ "$?" != 0 ]; then
    echo "Missing license for $name"
fi
