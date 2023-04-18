#!/usr/bin/env bash

# Copyright (C) 2011-2012  Evol Online
# Author: Andrei Karas (4144), gumi

dir=`pwd`
UPDATE_DIR=${UPDATE_DIR:=~/www/updates}
cdata=../../client-data
UPDATE_HTTP=${UPDATE_HTTP:="http://updates.themanaworld.org/updates"}
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
mkdir -pv $UPDATE_DIR
mkdir -pv $cdata/music
mkdir -pv $cdata/mods

echo -e "\e[96m>> Removing leftovers...\e[0m"
rm -rv files/* 2>/dev/null || :
rm -v $UPDATE_DIR/TMW.zip 2>/dev/null || :
rm -v $UPDATE_DIR/TMW-music.zip 2>/dev/null || :
rm -v $UPDATE_DIR/TMW-mods.zip 2>/dev/null || :
rm -v $UPDATE_DIR/resources.xml 2>/dev/null || :
rm -v $UPDATE_DIR/resources2.txt 2>/dev/null || : # Legacy: used by mana client

echo -e "\e[96m>> Entering client-data...\e[0m"
pushd $cdata &>/dev/null

if [ "$UPDATE_HTTP" == "none" ] ; then
    echo -e "\e[96m>> Changing last modified dates...\e[0m"
    find -iregex ".+[.]\(xml\|png\|tmx\|ogg\|txt\|po\|tsx\)" -exec touch --date=2015-01-01 {} \;
fi

echo -e "\e[96m>> Compressing files...\e[0m"
find -path ./music -prune -o -path ./mods -prune -o -iregex ".+[.]\(xml\|png\|tmx\|ogg\|txt\|po\|tsx\)" -printf "%P\n" | zip -X -@ $dir/files/TMW.zip
find -path ./sfx -prune -o -path ./mods -prune -o -iregex ".+[.]\(ogg\)" -printf "%P\n" | zip -X -@ $dir/files/TMW-music.zip
#find ./mods -printf "%P\n" | zip -X -@ $dir/files/TMW-mods.zip
find ./mods -type f | xargs zip -9 -r $dir/files/TMW-mods.zip
touch $dir/files/TMW-music.zip
touch $dir/files/TMW-mods.zip

echo -e "\e[96m>> Calculating adler32 checksum...\e[0m"
pushd $dir/files &>/dev/null
sum=`../adler32 1 TMW.zip`
musicsum=`../adler32 1 TMW-music.zip`
modsum=`../adler32 1 TMW-mods.zip`

echo -e "\e[96m>> Generating xml file...\e[0m"
echo "<?xml version=\"1.0\"?><updates>" >resources.xml
echo "<update type=\"data\" file=\"TMW.zip\" hash=\"${sum}\"/>" >>resources.xml
echo "<update type=\"music\" required=\"no\" file=\"TMW-music.zip\" hash=\"${musicsum}\" description=\"TMW music\"/>" >>resources.xml
echo "<update type=\"data\" required=\"no\" file=\"TMW-mods.zip\" hash=\"${modsum}\" description=\"TMW mods\"/>" >>resources.xml
echo "</updates>" >>resources.xml

echo -e "\e[96m>> Moving stuff around...\e[0m"
cp -v TMW.zip $UPDATE_DIR/
cp -v TMW-music.zip $UPDATE_DIR/
cp -v TMW-mods.zip $UPDATE_DIR/
cp -v resources.xml $UPDATE_DIR/

echo -e "\e[96m>> Giving read permissions...\e[0m"
pushd $UPDATE_DIR &>/dev/null
chmod a+r TMW.zip
chmod a+r TMW-music.zip
chmod a+r TMW-mods.zip
chmod a+r resources.xml

if [ "$UPDATE_HTTP" != "none" ] ; then
    echo
    echo -e "\e[96m>> Checking updates...\e[0m"
    check_update "$UPDATE_HTTP/TMW.zip"
    check_update "$UPDATE_HTTP/TMW-music.zip"
    check_update "$UPDATE_HTTP/TMW-mods.zip"
    check_update "$UPDATE_HTTP/resources.xml"
    check_update "$UPDATE_HTTP/news.php"
fi

popd &>/dev/null # $dir/files
popd &>/dev/null # $cdata
popd &>/dev/null # tools/client
