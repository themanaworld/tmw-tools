#!/usr/bin/env bash

cd xsd
DIR="$(pwd)/../../../client-data"
rm ../errors.txt

function check {
    xmllint --format --schema tmw.xsd "${DIR}"/"${1}" 2>&1 >/dev/null | \
        grep -v ": Skipping import of schema located at " | \
        grep -v ".xml validates" | \
        grep -v ".manaplus validates" >>../errors.txt
}

xmllint --format --schema XMLSchema.xsd tmw.xsd 2>&1 >/dev/null | \
    grep -v ": Skipping import of schema located at " | \
    grep -v ".xsd validates" >>../errors.txt

check avatars.xml
check badges.xml
check charcreation.xml
check deadmessages.xml
check effects.xml
check elementals.xml
check emotes.xml
check equipmentslots.xml
check equipmentwindow.xml
check evol.manaplus
check features.xml
check groups.xml
check homunculuses.xml
check horses.xml
check itemcolors.xml
check itemfields.xml
check items.xml
check maps.xml
check mercenaries.xml
check mods.xml
check monsters.xml
check npcdialogs.xml
check npcs.xml
check paths.xml
check pets.xml
check quests.xml
check skills.xml
check skillunits.xml
check sounds.xml
check stats.xml
check status-effects.xml
check units.xml
check weapons.xml

find -H "${DIR}/graphics" -type f -name "*.xml" -exec ./checkfile.sh {} \; >>../errors.txt
