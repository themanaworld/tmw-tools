#!/bin/bash

export DIR="../../client-data"

find $DIR -type f -name "*.png" -exec ./icccheckfile.sh {} \;
