#!/usr/bin/env bash

export DIR="../../client-data"

find -H $DIR -type f -name "*.png" -exec ./checkfile.sh $DIR/LICENSE $DIR ART_LICENSE {} \;
find -H $DIR/sfx -type f -name "*.ogg" -exec ./checkfile.sh $DIR/LICENSE $DIR/ART_LICENSE {} \;
find -H $DIR -type f -name "*.tmx" -exec ./checkfile.sh $DIR/LICENSE $DIR/ART_LICENSE {} \;
find -H $DIR -type f -name "*.jpg" -exec ./checkfile.sh $DIR/LICENSE $DIR/ART_LICENSE {} \;

