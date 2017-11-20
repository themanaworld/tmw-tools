#!/usr/bin/env bash

# Copyright (C) 2011-2012  Evol Online
# Author: Andrei Karas (4144)

dir=`pwd`
output=~/www/updates
cdata=../../client-data

LDLIBS=-lz
prefix=/usr/local
CC=${CC:=gcc}

echo "======= Legacy-music ======="

echo ">> Building adler32..."
rm -f adler32 2>/dev/null || :
$CC -lz adler32.c -o adler32

echo ">> Creating directory tree..."
mkdir -pv files
mkdir -pv $output

echo ">> Removing leftovers..."
rm -v files/Legacy-music.zip 2>/dev/null || :

echo ">> Entering client-data..."
pushd $cdata
echo ">> Changing file dates..."
find -path ./sfx -prune -o -iregex ".+[.]\(ogg\)" -exec touch --date=2015-01-01 {} \;
echo ">> Compressing files..."
find -path ./sfx -prune -o -iregex ".+[.]\(ogg\)" -printf "%P\n" | zip -X -@ $dir/files/Legacy-music.zip
touch $dir/files/Legacy-music.zip
echo ">> Dumping git revision to file..."
git rev-parse HEAD >$dir/musiccommit.txt

pushd $dir/files
echo ">> Calculating adler32 checksum..."
sum=`../adler32 1 Legacy-music.zip`

echo ">> Generating xml file..."
echo "    <update type=\"music\" required=\"no\" file=\"Legacy-music.zip\" hash=\"${sum}\" description=\"TMW music\" />" >> xml_header.txt

cp xml_header.txt resources.xml
cat xml_footer.txt >>resources.xml

echo ">> Moving stuff around..."
cp Legacy-music.zip $output/
cp resources.xml $output/
popd
popd
