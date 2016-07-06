#!/bin/bash

identify -verbose $1 | grep profile >/dev/null

if [ "$?" == 0 ]; then
    export name="$1"
    export name=${name##../../client-data/}
    echo "ICC profile found for image $name"
fi
