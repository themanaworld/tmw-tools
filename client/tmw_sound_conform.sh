#!/bin/bash
##Ledmitz (2026)
##This script checks for file conformity in quality and names when run from the "music" DIR.
##It updates maps with the proper music naming convention when run from the 'maps' DIR. Use it with caution.
##Titles may only contain letters(a-z), numbers(0-9) and underscores(_).
##Exceptions must be added in this script (i.e. magick-real.ogg). See "Changeable VARs".
##TODO: sfx support.

#Required apps check. command is used, since it's a common builtin with most all systems.
REQUIRED_APPS='awk basename cut grep sed sort tr wc'
    for APP in $REQUIRED_APPS; do
        REQ_APP_CHECK=$(command -v "$APP")
            if [[ "$REQ_APP_CHECK" == '' ]]; then
                echo -e "$APP must be installed in order to continue\nRequired Apps: $REQUIRED_APPS" >&2
                exit 1
            fi
    done

##Changeable VARs: IMPORTANT: Locations will vary, depending on how a developer organizes their own system and on what they
##are changing and where. For instance, the music DIR is not accessible from tmwa-server-data, at all. In all TMW cases, the
##MUSIC_DIR should point to the TMW music git repo and MAPS_DIR to the DIR in the tmwa-client-data git repo. However, this
##script leaves room for those with forks to specify all from a single serverdata parent, if desired.
#Music filename exceptions. Spaces are the separator. Exceptions may not contain spaces. Indicate wildcards with '*'.
#Files without extensions needn't be added, since they are ignored by default.
NAME_EXCEPTIONS='*.sh *.md magick-real.ogg'
#Music DIR (optional). If this is for official TMW work, it must point to the music git repo. Otherwise it can be contained in any \
#DIR named "music". Make sure you are on the correct git branch first.
MUSIC_DIR=""
#Maps DIR (optional). If this if for official TMW work, it must point to the maps DIR in the tmwa-client-data git repo. Otherwise it
#can be contained in any DIR named "maps". Make sure you are on the correct git branch first.
MAPS_DIR=""
####################
##Do not change VARs below here.
#This ONLY checks the name of the current DIR, so as to allow simple checks on music only, if desired. This DIR must be named "music"
#or "maps" to continue.
DIR_CHECK=$(basename "$PWD")
#Formats music name exceptions for use with grep.
NAME_EXCEPTIONS=$(echo "$NAME_EXCEPTIONS" | sed 's/\./\\./g' | sed 's/*/.*/g' | sed 's/ /\\\|/g')
#echo "NAME_EXCEPTIONS: $NAME_EXCEPTIONS"
#Checks for UTF-8 character map, just to be fancy. Info will be symbolized with "-".
CHARMAP_CHECK=$(locale -c charmap | grep 'UTF-8')
    if [[ "$CHARMAP_CHECK" == 'UTF-8' ]]; then
        CHECKMARK='✓'
        XMARK='🗴'
    else
        CHECKMARK='/'
        XMARK='x'
    fi
    REFUSEMARK='!'

##Music: Provides a prompt.
    if [[ "$DIR_CHECK" != 'music' ]] && [[ "$MUSIC_DIR" != '' ]]; then
        cd "$MUSIC_DIR" || exit
        DIR_CHECK=$(basename "$PWD")
    elif [[ "$DIR_CHECK" == 'music' ]] && [[ "$MUSIC_DIR" != '' ]]; then
        echo -e "This step will check conformity of files in the music DIR. If you're working from git, ensure you're \
on the correct branch. \
\n\t\Continue from $MUSIC_DIR: 1 \
\n\tContinue from $PWD: 2 \
\n\tQuit: Any other key"
        read -p 'Please select how to proceed:' ANS
            if [[ "$ANS" == '1' ]]; then
                cd "$MUSIC_DIR" || exit
            elif [[ "$ANS" == '2' ]]; then
                :
            else
                exit 0
            fi
    elif [[ "$DIR_CHECK" == 'music' ]] && [[ "$MUSIC_DIR" == '' ]]; then
        :
    elif [[ "$DIR_CHECK" == 'maps' ]]; then
       :
    else
        echo 'Error: You must be in the "music" or "maps" directory in order to use this script.' >&2
        exit 1
    fi
    if [[ "$DIR_CHECK" == 'maps' ]]; then
        :
    else
        if [ -d '.git' ]; then
            GIT_BRANCH=$(git branch --show-current)
            echo -e "Git branch: $GIT_BRANCH \
\n\tYes: 1 \
\n\tNo: Any other key"
            read -p 'Is this correct?' ANS
                if [[ "$ANS" == '1' ]]; then
                    :
                else
                    echo 'Select the correct branch before continuing.'
                    exit 0
                fi
        fi
    fi
    
##Name convention check. Must be in a "music" DIR.
if [[ "$DIR_CHECK" == 'music' ]]; then
    #Name syntax.
    INVALID_NAME_COUNT='0'
    #Incorrect file type.
    INVALID_FILE_COUNT='0'
    #Ideal oggs.
    PASS_COUNT='0'
    #Corrected file extension syntax (the only automatic changes to "music" DIR). 
    CORRECTED_EXT_COUNT='0'
    
        for TRACK in *; do
            #Checks for titles containing invalid characters in files with extensions ranging from 2 to 4 characters(common audio
            #extensions+).
            CON_CHECK=$(echo "$TRACK" | grep -v "$NAME_EXCEPTIONS" | grep -E '^.*\.[A-Za-z0-9]{2,4}$' | \
                         sed -e '/^[a-z0-9_]\+\.ogg$/d')
                if [[ "$CON_CHECK" != '' ]]; then
                    if [[ $(echo "$TRACK" | grep '^.*\.[Oo][Gg][Gg]$') != '' ]]; then
                        if [[ $(echo "$TRACK" | grep '^[a-z0-9_]\+\.[Oo][Gg][Gg]$') != '' ]]; then
                                #Corrects file extensions only.
                                NEW_NAME=${TRACK//\.[Oo][Gg][Gg]/\.ogg}
                                if [ -f "$NEW_NAME" ]; then
                                    echo "0: $XMARK $TRACK: Cannot rename to $NEW_NAME. File exists."
                                else
                                    mv -f "$TRACK" "$NEW_NAME"
                                        if [ -f "$NEW_NAME" ]; then
                                            echo "0: - $TRACK: Renamed to $NEW_NAME."
                                            CORRECTED_EXTS="$CORRECTED_NAMES $NEW_NAME"
                                            CORRECTED_EXT_COUNT=$((CORRECTED_EXT_COUNT + 1))
                                            #Updates license automatically.
                                            sed -i "s/$TRACK/$NEW_NAME/g" 'music-license.md'
                                        else
                                            #Fatal errors could be due to a script error, read only system or failing hardware.
                                            echo "Error(fatal): $XMARK $TRACK: Copy failed. Ensure you are not on a read-only system." >&2
                                            exit 1
                                        fi
                                fi
                        else
                            INVALID_NAMES="$INVALID_NAMES $TRACK"
                            INVALID_NAME_COUNT=$((INVALID_NAME_COUNT +1))
                            FAIL_NAMES="$FAIL_NAMES $TRACK"
                            BADFAIL_NAMES="$BADFAIL_NAMES $TRACK"
                            REFUSE_NAMES="$REFUSE_NAMES $TRACK"
                            echo "0: $REFUSEMARK $TRACK: Refused!: Invalid name found."
                        fi
                    else
                        INVALID_FILES="$INVALID_FILES $TRACK"
                        INVALID_FILE_COUNT=$((INVALID_FILE_COUNT + 1))
                        FAIL_NAMES="$FAIL_NAMES $TRACK"
                        BADFAIL_NAMES="$BADFAIL_NAMES $TRACK"
                        REFUSE_NAMES="$REFUSE_NAMES $TRACK"
                        echo "0: $REFUSEMARK $TRACK: Refused!: Invalid file found."
                    fi
                fi
        done
        
    if [[ "$INVALID_FILE_COUNT" != '0' ]]; then
        echo "--Only oggs are valid files. Valid characters are a-z, 0-9 and _. Don't run this script from 'maps' or 'tools' \
DIR until corrected. Exceptions can be added directly to this script, if required.--"
    fi
    
##Ogg and attributes check (Ideally, it should be an ogg with stereo channels @ 44100Hz with 160000bps, but because ogg is
##natively VBR, the checks are less strict). Mono tracks of conforming quality will only show info and negate a pass or fail.
        OGG_COUNT='0'
        FALSEOGG_COUNT='0'
        NONSTEREO_COUNT='0'
        WRONGHZ_COUNT='0'
        WRONGBPS_COUNT='0'
        MONOCANDIDATE_COUNT='0'
        
        #Checks all oggs, including those that still have file extensions that are not all lower case yet due to
        #other reasons(some-track.OGG).
        for TRACK in *.[Oo][Gg][Gg]; do
            OGG_COUNT=$((OGG_COUNT + 1))
            OGG_VERIFY=$(file "$TRACK" | awk -F ',' '{print $1}' | awk '{print $2}') #Should read as 'Ogg'
                if [[ "$OGG_VERIFY" != 'Ogg' ]]; then
                    #Get file info on falsely named oggs.
                    FALSEOGG_NAMES="$FALSEOGG_NAMES $TRACK"
                    FALSEOGG_COUNT=$((FALSEOGG_COUNT + 1))
                    FAIL_NAMES="$FAIL_NAMES $TRACK"
                    BADFAIL_NAMES="$BADFAIL_NAMES $TRACK"
                    REFUSE_NAMES="$REFUSE_NAMES $TRACK"
                    echo "$OGG_COUNT: $REFUSEMARK $TRACK: Refused!: Not ogg: $(file "$TRACK" | cut -d' ' -f2-)"
                else
                    #Get info on verified oggs.
                    STEREO_VERIFY=$(file "$TRACK" | awk  -F  ', ' '{print $3}') #Should read as 'stereo'
                    HZ_VERIFY=$(file "$TRACK" | awk  -F  ', ' '{print $4}' | awk '{print $1}') #Should read as 44100
                    BPS_VERIFY=$(file "$TRACK" | awk  -F  ', ' '{print $5}' | awk '{print $1}' | tr -d '~') #Should read as 160000
                        if [[ "$STEREO_VERIFY" != 'stereo' ]]; then
                            NONSTEREO_NAMES="$NONSTEREO_NAMES $TRACK"
                            NONSTEREO_COUNT=$((NONSTEREO_COUNT + 1))
                        fi
                        if [[ "$HZ_VERIFY" != '44100' ]]; then
                            WRONGHZ_NAMES="$WRONGHZ_NAMES $TRACK"
                            WRONGHZ_COUNT=$((WRONGHZ_COUNT + 1))
                        fi
                        if [[ "$BPS_VERIFY" -lt '150000' ]] || [[ "$BPS_VERIFY" -gt '170000' ]]; then
                            if [[ "$BPS_VERIFY" -ge '40000' ]] && [[ "$BPS_VERIFY" -le '64000' ]]; then
                                if [[ "$STEREO_VERIFY" != 'mono' ]]; then
                                    #Candidates for mono encoding.
                                    MONOCANDIDATE_NAMES="$MONOCANDIDATE_NAMES $TRACK"
                                    MONOCANDIDATE_COUNT=$((MONOCANDIDATE_COUNT + 1))
                                fi
                            else
                                #Non-conforming bps.
                                WRONGBPS_NAMES="$WRONGBPS_NAMES $TRACK"
                                WRONGBPS_COUNT=$((WRONGBPS_COUNT + 1))
                            fi
                        fi
                        #Additional Hz warning text.
                        if [[ "$HZ_VERIFY" -le '22050' ]]; then
                            FAIL_NAMES="$FAIL_NAMES $TRACK"
                            HZ_WARNING="\n$XMARK $HZ_VERIFY is a very low sampling rate. This would only be acceptable \
in tracks that contain only bass sounds, voice or when emulating an old recording. Only re-encode if the original project files are \
obtainable and have a higher sampling rate."
                        elif [[ "$HZ_VERIFY" -gt '44100' ]]; then
                            if [[ "$HZ_VERIFY" -gt '48000' ]]; then
                                FAIL_NAMES="$FAIL_NAMES $TRACK"
                                BADFAIL_NAMES="$BADFAIL_NAMES $TRACK"
                                HZ_WARNING="\n$XMARK $HZ_VERIFY is a very high sampling rate. Re-encode @ 44100 Hz."
                            else #Checks for 44101 - 48000 Hz
                                HZ_WARNING="\n- A $HZ_VERIFY Hz sampling rate is higher than required, but acceptable."
                            fi
                        elif [[ "$HZ_VERIFY" -ge '22050' ]] && [[ "$HZ_VERIFY" -lt '44100' ]]; then
                            FAIL_NAMES="$FAIL_NAMES $TRACK"
                            HZ_WARNING="\n$XMARK A $HZ_VERIFY Hz sampling rate is lower than ideal. Re-encode if the original \
project files are obtainable and have a higher sampling rate."
                        else
                            HZ_WARNING=''
                        fi
                        #Additional non-stereo warning text. Additional mono conformity check is below.
                        if  [[ "$STEREO_VERIFY" != 'mono' ]] && [[ "$STEREO_VERIFY" != 'stereo' ]]; then
                            #More than 2 channels.
                            FAIL_NAMES="$FAIL_NAMES $TRACK"
                            STEREO_WARNING=" $XMARK Maximum channels exceeded. Re-encode to stereo."
                        elif [[ "$STEREO_VERIFY" == 'mono' ]]; then
                            #Only 1 channel.
                            STEREO_WARNING="\n- Mono may be fine for ambience in some cases. If this is a music track, re-encode if \
original project files are obtainable and have higher bps."
                        elif [[ "$STEREO_VERIFY" == 'stereo' ]] && [[ "$BPS_VERIFY" -ge '40000' ]] && [[ "$BPS_VERIFY" -le '69000' ]]; then
                            #Candidate for mono. Already counted.
                            STEREO_WARNING="\n- $BPS_VERIFY may be acceptable for mono. Should this be in mono?"
                        else
                            STEREO_WARNING=''
                        fi
                        #Low quality check.
                        if [[ "$HZ_VERIFY" -lt '44100' ]] || [[ "$BPS_VERIFY" -lt '150000' ]]; then
                            if [[ "$STEREO_VERIFY" == 'mono' ]]; then
                                if [[ "$BPS_VERIFY" -gt '69000' ]]; then
                                    #Excedes quality for mono.
                                    FAIL_NAMES="$FAIL_NAMES $TRACK"
                                    echo -e "$OGG_COUNT: $XMARK $TRACK: Warning: $STEREO_VERIFY @ $HZ_VERIFY Hz with \
$BPS_VERIFY/bps. Re-encode to mono @ $HZ_VERIFY Hz with 64000/bps.$HZ_WARNING$STEREO_WARNING"
                                elif [[ "$BPS_VERIFY" -ge '40000' ]] && [[ "$BPS_VERIFY" -le '69000' ]]; then
                                    #Conforms to quality for mono (info only).
                                    echo  -e "$OGG_COUNT: - $TRACK: $STEREO_VERIFY @ $HZ_VERIFY Hz with $BPS_VERIFY/bps. \
$HZ_WARNING$STEREO_WARNING"
                                fi
                            else
                                #Low quality stereo+.
                                FAIL_NAMES="$FAIL_NAMES $TRACK"
                                echo -e "$OGG_COUNT: $XMARK $TRACK: Warning: $STEREO_VERIFY @ $HZ_VERIFY Hz with \
$BPS_VERIFY/bps. Only re-encode if original project files are obtainable and have higher bps.$HZ_WARNING$STEREO_WARNING"
                            fi
                        #High quality check.
                        elif [[ "$HZ_VERIFY" -gt '44100' ]] || [[ "$BPS_VERIFY" -gt '170000' ]]; then
                            if [[ "$BPS_VERIFY" -gt '170000' ]]; then
                                #High bps.
                                FAIL_NAMES="$FAIL_NAMES $TRACK"
                                echo -e "$OGG_COUNT: $XMARK $TRACK: Warning: $STEREO_VERIFY @ $HZ_VERIFY Hz with \
$BPS_VERIFY/bps. Re-encode to 160000/bps.$HZ_WARNING$STEREO_WARNING"
                            else
                                #High Hz.
                                echo -e "$OGG_COUNT: - $TRACK: Warning: $STEREO_VERIFY @ $HZ_VERIFY Hz with $BPS_VERIFY/bps.\
$HZ_WARNING$STEREO_WARNING"
                            fi
                        else
                            #Ideal oggs are given a pass here.
                            PASS_COUNT=$((PASS_COUNT + 1))
                            echo -e "$OGG_COUNT: $CHECKMARK $TRACK: $STEREO_VERIFY @ $HZ_VERIFY Hz with $BPS_VERIFY/bps. \
$HZ_WARNING$STEREO_WARNING"
                        fi
                fi
        done
##Summary
    #Count tracks and iterations of each track.
    #Oggs that should be rectified, when possible.
    FAIL_COUNT=$(echo "$FAIL_NAMES" | wc -w)
        for NAME in $FAIL_NAMES; do
            NAME_COUNT=$(echo "$FAIL_NAMES" | grep -Fo "$NAME" | wc -w)
            NAME="$NAME($NAME_COUNT)"
            FAIL_NAMES2="$FAIL_NAMES2 $NAME"
        done
    #Oggs that should be rectified. Overly poor/extreme quality, renaming/exceptions required, wrong file-type, etc.
    BADFAIL_COUNT=$(echo "$BADFAIL_NAMES" | wc -w)
        for NAME in $BADFAIL_NAMES; do
            NAME_COUNT=$(echo "$BADFAIL_NAMES" | grep -Fo "$NAME" | wc -w)
            NAME="$NAME($NAME_COUNT)"
            BADFAIL_NAMES2="$BADFAIL_NAMES2 $NAME"
        done
    #Refuse to continue until rectified. Must be "0". Non-ogg tracks, files that require exceptions.
    REFUSE_COUNT=$(echo "$REFUSE_NAMES" | wc -w)
        for NAME in $REFUSE_NAMES; do
            NAME_COUNT=$(echo "$REFUSE_NAMES" | grep -Fo "$NAME" | wc -w)
            NAME="$NAME($NAME_COUNT)"
            REFUSE_NAMES2="$REFUSE_NAMES2 $NAME"
        done
    #Removes duplicate entries of tracks.
    FAIL_NAMES=$(echo "$FAIL_NAMES2" | tr ' ' '\n' | sort -u  | tr '\n' ' ')
    BADFAIL_NAMES=$(echo "$BADFAIL_NAMES2" | tr ' ' '\n' | sort -u | tr '\n' ' ')
    REFUSE_NAMES=$(echo "$REFUSE_NAMES2" | tr ' ' '\n' | sort -u | tr '\n' ' ')
    #Hark!
    echo "--Fails are individual failed tests, not failed files. Files can fail more than once. i.e. failed-track.mp3(2).--"
    echo '________________________'
    echo "Invalid files: $INVALID_FILE_COUNT ($INVALID_FILES )"
    echo "Corrected ogg extensions: $CORRECTED_EXT_COUNT ($CORRECTED_EXTS )"
    echo '________________________'
    echo "Total oggs: $OGG_COUNT"
    echo "False oggs: $FALSEOGG_COUNT ($FALSEOGG_NAMES )"
    echo "Verified oggs: $((OGG_COUNT - FALSEOGG_COUNT))"
    echo "Invalid names: $INVALID_NAME_COUNT ($INVALID_NAMES )"
    echo "Non-stereo: $NONSTEREO_COUNT ($NONSTEREO_NAMES )"
    echo "Mono candidates: $MONOCANDIDATE_COUNT ($MONOCANDIDATE_NAMES )"
    echo "Invalid Hz: $WRONGHZ_COUNT ($WRONGHZ_NAMES )"
    echo "Invalid bps: $WRONGBPS_COUNT ($WRONGBPS_NAMES )"
    echo '________________________'
    echo "Passes: $PASS_COUNT"
    echo "Fails(total): $FAIL_COUNT ($FAIL_NAMES)"
    echo "Fails(bad): $BADFAIL_COUNT ($BADFAIL_NAMES)"
    echo "Refusals(fatal): $REFUSE_COUNT ($REFUSE_NAMES)"
    echo '________________________'
    echo "--Make changes as needed, update exceptions, rerun until content and not refused.--"
    echo "--Passes are marked with \"$CHECKMARK\", fails with \"$XMARK\", refusals with \"!\", info with \"-\".--"
    
    if [[ "$REFUSE_COUNT" != '0' ]]; then
        echo -e "\e[31mRefused! Correct refusals and re-run." >&2
        exit 1
    else
        echo -e "\e[32mSuccess! Continue to maps."
    fi
fi


##Map: Auto-correct names. Warning: Writes to files.
NAME_EXCEPTIONS=$(echo "$NAME_EXCEPTIONS" | sed 's/\\|/\\|\n/g' | grep '.*\.ogg' | tr -d '\n')
#echo "NAME_EXCEPTIONS: $NAME_EXCEPTIONS"

if [[ "$DIR_CHECK" == 'music' ]] && [[ "$MAPS_DIR" != '' ]]; then
    cd "$MAPS_DIR" || exit
    DIR_CHECK=$(basename "$PWD")
elif [[ "$DIR_CHECK" == 'maps' ]] && [[ "$MAPS_DIR" != '' ]]; then
    echo -e "Warning: Do not run in maps, unless you are not \"Refused!\" and have \"Success!\" in music. This step will \
correct music names in maps in the \"maps\" DIR. If you're working from git, ensure you're on the correct branch. Valid \
characters are a-z, 0-9 and _. Exceptions can be added directly to this script, if required. \
\nWarning: This will write to files. \
\n\t\Continue from $MAPS_DIR: 1 \
\n\tContinue from $PWD: 2 \
\n\tQuit: Any other key"
    read -p 'Please select how to proceed:' ANS
        if [[ "$ANS" == '1' ]]; then
            cd "$MAPS_DIR" || exit
        elif [[ "$ANS" == '2' ]]; then
            :
        else
            exit 0
        fi
elif [[ "$DIR_CHECK" == 'maps' ]] && [[ "$MAPS_DIR" == '' ]]; then
    echo -e "Warning: Do not run in maps, unless you are not \"Refused!\" and have \"Success!\" in music. This step will \
correct music names in maps in the \"maps\" DIR. If you're working from git, ensure you're on the correct branch. Valid \
characters are a-z, 0-9 and _. Exceptions can be added directly to this script, if required. \
\nWarning: This will write to files. \
\n\tContinue from $PWD: 1 \
\n\tQuit: Any other key"
    read -p 'Please select how to proceed:' ANS
        if [[ "$ANS" == '1' ]]; then
            :
        else
            exit 0
        fi
else
    echo 'Error: You must be in the "music" or "maps" directory in order to use this script.' >&2
    exit 1
fi
if [ -d '.git' ]; then
    GIT_BRANCH=$(git branch --show-current)
    echo -e "Git branch: $GIT_BRANCH \
\n\tYes: 1 \
\n\tNo: Any other key"
    read -p 'Is this correct?' ANS
        if [[ "$ANS" == '1' ]]; then
            :
        else
            echo 'Select the correct branch before continuing.'
            exit 0
        fi
fi

if [[ "$DIR_CHECK" == 'maps' ]]; then
    for MAP in *.tmx; do
        echo "$MAP"
        OLD_TITLE=$(grep 'music' "$MAP" | grep -Eo "[A-Za-z0-9 _\.\-]+\.ogg")
                if [[ $(grep "$NAME_EXCEPTIONS" "$MAP") != '' ]]; then
                    echo "Exception found: $OLD_TITLE. Skipping..."
                    echo '________________________'
                else
                    #Checks for no music and corrects title syntax.
                    if [[ "$OLD_TITLE" != '' ]]; then
                        NEW_TITLE=$(echo  "$OLD_TITLE" | \
                                    sed 's/\./_/g' | \
                                    sed -e 's/.[Oo][Gg][Gg]$/.ogg/g' | \
                                    sed 's/ /_/g' | \
                                    sed 's/-/_/g' | \
                                    sed -E 's/([a-z])([A-Z])+/\1_\L\2/g' | \
                                    sed -E 's/([a-z])([0-9])+/\1_\2/g' | \
                                    sed -E 's/([A-Z])/\L\1/g')
                        sed -i "s/$OLD_TITLE/$NEW_TITLE/g" "$MAP"
                    else
                        NEW_TITLE="$OLD_TITLE"
                    fi
                VERIFIED_TITLE=$(grep 'music' "$MAP" | grep -Eo "[A-Za-z0-9 _\-]+.ogg")    
                echo "Old title: $OLD_TITLE"
                echo "New title: $NEW_TITLE"
                echo '________________________'
                    if [[ "$VERIFIED_TITLE" != "$NEW_TITLE" ]]; then
                        echo "Error(fatal): New and verified titles do not match. $VERIFIED_TITLE != $NEW_TITLE" >&2
                        exit 1
                    fi
                NEW_TITLE=''
                VERIFIED_TITLE=''
                fi
    done
fi
