#!/bin/bash

export DIR="../../client-data"

echo Checking png files
find $DIR -type f -name "*.png" -exec ./checkfile.sh $DIR/LICENSE {} \;

echo Checking ogg files
find $DIR/sfx -type f -name "*.ogg" -exec ./checkfile.sh $DIR/LICENSE {} \;
