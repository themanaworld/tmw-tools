#!/usr/bin/env bash

export DIR="../../client-data"

find -H $DIR -type f -name "*.png" -exec ./icccheckfile.sh {} \;
