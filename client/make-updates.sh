#!/usr/bin/env bash

# Copyright (C) 2011-2012  Evol Online
# Author: Andrei Karas (4144), gumi

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

function finish() {
    retVal=$?
    echo
    if [ ${retVal} == "0" ]; then
        echo -e "\e[96m>> Done!\e[0m"
    fi
}

trap finish EXIT


echo -e "\e[105m======= Legacy =======\e[0m"

echo -e "\e[96m>> Building adler32...\e[0m"
rm -f adler32 2>/dev/null || :
$CC -lz adler32.c -o adler32

echo -e "\e[96m>> Creating directory tree...\e[0m"
mkdir -pv files
mkdir -pv $output
mkdir -pv $cdata/music

echo -e "\e[96m>> Removing leftovers...\e[0m"
rm -rv files/* 2>/dev/null || :
rm -v $output/Legacy.zip 2>/dev/null || :
rm -v $output/Legacy-music.zip 2>/dev/null || :
rm -v $output/resources.xml 2>/dev/null || :
rm -v $output/resources2.txt 2>/dev/null || : # Legacy: used by mana client

echo -e "\e[96m>> Entering client-data...\e[0m"
pushd $cdata &>/dev/null

echo -e "\e[96m>> Compressing files...\e[0m"
find -path ./music -prune -o -iregex ".+[.]\(xml\|png\|tmx\|ogg\|txt\|po\|tsx\)" -printf "%P\n" | zip -X -@ $dir/files/Legacy.zip
find -path ./sfx -prune -o -iregex ".+[.]\(ogg\)" -printf "%P\n" | zip -X -@ $dir/files/Legacy-music.zip
touch $dir/files/Legacy-music.zip

echo -e "\e[96m>> Calculating adler32 checksum...\e[0m"
pushd $dir/files &>/dev/null
sum=`../adler32 1 Legacy.zip`
musicsum=`../adler32 1 Legacy-music.zip`

echo -e "\e[96m>> Generating xml file...\e[0m"
echo "<?xml version=\"1.0\"?><updates>" >resources.xml
echo "<update type=\"data\" file=\"Legacy.zip\" hash=\"${sum}\"/>" >>resources.xml
echo "<update type=\"music\" required=\"no\" file=\"Legacy-music.zip\" hash=\"${musicsum}\" description=\"TMW music\"/>" >>resources.xml
echo "</updates>" >>resources.xml

echo -e "\e[96m>> Moving stuff around...\e[0m"
cp -v Legacy.zip $output/
cp -v Legacy-music.zip $output/
cp -v resources.xml $output/

echo -e "\e[96m>> Giving read permissions...\e[0m"
pushd $output &>/dev/null
chmod a+r Legacy.zip
chmod a+r Legacy-music.zip
chmod a+r resources.xml

echo
echo -e "\e[96m>> Checking updates...\e[0m"
check_update "$http_root/Legacy.zip"
check_update "$http_root/Legacy-music.zip"
check_update "$http_root/resources.xml"
check_update "$http_root/news.php"

popd &>/dev/null # $dir/files
popd &>/dev/null # $cdata
popd &>/dev/null # tools/client
