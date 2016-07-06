#!/bin/bash

export DIR="../../client-data"

find $DIR -type f -name "*.png" -exec ./checkfile.sh $DIR/LICENSE {} \;
find $DIR/sfx -type f -name "*.ogg" -exec ./checkfile.sh $DIR/LICENSE {} \;
