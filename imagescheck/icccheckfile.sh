#!/usr/bin/env bash

identify -verbose $1 | egrep -i "profile|iCCP" >/dev/null

if [ "$?" == 0 ]; then
    export name="$1"
    export name=${name##../../client-data/}
    echo "ICC or iCCP profile found for image $name"
fi
