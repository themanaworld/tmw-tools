#!/usr/bin/env bash

# Copyright (C) 2011-2012  Evol Online
# Author: Andrei Karas (4144)

dir=`pwd`
output=~/www/updates
cdata=../../client-data
http_root="http://updates.themanaworld.org/updates"

LDLIBS=-lz
prefix=/usr/local
CC=${CC:=gcc}

function check_update() {
    test_command=`           \
        curl -sL             \
        -w "%{http_code}\n"  \
        "$1"                 \
        -o /dev/null         \
        --connect-timeout 3  \
        --max-time 5`

    if [ ${test_command} == "200" ] ;
    then
       echo -e "hit $1 (\e[92m$test_command OK\e[0m)";
    else
       echo -e "\e[31m!!FAILED!!\e[0m $1 ($test_command)";
       exit 1;
    fi
}


echo "======= Legacy-music ======="

echo ">> Building adler32..."
rm -f adler32 2>/dev/null || :
$CC -lz adler32.c -o adler32

echo ">> Creating directory tree..."
mkdir -pv files
mkdir -pv $output

echo ">> Removing leftovers..."
rm -v files/Legacy-music.zip 2>/dev/null || :
rm -v $output/Legacy-music.zip 2>/dev/null || :

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
cp -v Legacy-music.zip $output/
cp -v resources.xml $output/

echo ">> Giving read permissions..."
pushd $output
chmod a+r Legacy-music.zip
chmod a+r resources.xml

echo ">> Checking updates..."
check_update "$http_root/Legacy-music.zip"
check_update "$http_root/resources.xml"

popd # $dir/files
popd # $cdata
popd # tools/client
