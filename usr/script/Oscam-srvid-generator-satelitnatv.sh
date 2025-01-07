#!/bin/bash
#DESCRIPTION=SRVID-SATELINATV
HEADER="
#################################################################################
###     Shell script written by s3n0, 2021-03-02, https://github.com/s3n0     ###
#################################################################################
###  Shell script to parse data from the web page https://www.satelitnatv.sk  ###
###         and then generate the 'oscam.srvid' file from parsed data         ###
#################################################################################
###  !!! The mentioned web-site www.satelitnatv.sk unfortunately provides !!! ###
###  !!!    only DVB services from Slovakia and the Czech Republic        !!! ###
#################################################################################
"

find_oscam_cfg_dir()
{
    RET_VAL=""
    DIR_LIST="/etc /var /usr /config"
    for FOLDER in $DIR_LIST; do
        FILEPATH=$(find "${FOLDER}" -iname "oscam.conf" -print -quit)
        if [ -f "$FILEPATH" ]; then
            RET_VAL="${FILEPATH%/*.conf}"
            break
        fi
    done

    if [ -z "$RET_VAL" ]; then
        OSCAM_BIN=$(find /usr/bin -iname 'oscam*' -print -quit)
        if [ -z "$OSCAM_BIN" ]; then
            echo -e "ERROR: Oscam binary file was not found in '/usr/bin'.\nThe script will be terminated."
            exit 1
        else
            RET_VAL="$($OSCAM_BIN -V | grep -i 'configdir' | awk '{print substr($2,0,length($2)-1)}')"
        fi
    fi

    if [ -z "$RET_VAL" ]; then
        echo "WARNING: Oscam configuration directory not found!"
    fi
    echo "$RET_VAL"
}

create_srvid_file()
{
    # INPUT ARGUMENTS:
    # $1 = URL of the package list of channels with their data (e.g., http://www.satelitnatv.sk/PROVIDER-NAME)
    # $2 = Provider name (that exact name will be inserted into the '.srvid' output file)
    # $3 = CAIDs (comma-separated) needed for the provider
    
    echo "Downloading data from: ${1}"
    if ! wget -q -O /tmp/satelitnatv.html --no-check-certificate "${1}"; then
        echo "ERROR: Failed to download data from ${1}"
        exit 1
    fi
    
    sed -i 's/<tr>/\n/g' /tmp/satelitnatv.html  # Replace <tr> tags with newline characters
    LIST=$(sed -n 's/.*<strong><a href=\/.*\/?id=[0-9]\{4\}\([0-9]*\)>\(.*\)<\/a><\/strong>.*/\1 \2/p' /tmp/satelitnatv.html)

    FILE_NAME=$(echo "${1##*.sk}" | tr -d "/")  # Generate a filename from the URL
    FILE_OUTPUT="/tmp/oscam__${FILE_NAME}.srvid"
    rm -f "$FILE_OUTPUT"

    while IFS= read -r LINE; do
        SRN=$(echo "$LINE" | cut -d " " -f 2-)
        SID=$(echo "$LINE" | cut -d " " -f -1 | awk '{print $1 + 0}')  # Remove leading zeros
        SIDHEX=$(printf "%04X" $SID)  # Convert SID to hexadecimal
        echo "${3}:${SIDHEX}|${2}|${SRN}" >> "$FILE_OUTPUT"
    done <<< "$LIST"
    
    if [ -f "$FILE_OUTPUT" ]; then
        echo "The new file was created: ${FILE_OUTPUT}\n"
        rm -f /tmp/satelitnatv.html
    else
        echo "ERROR: File was not created: ${FILE_OUTPUT}"
        echo -e "Function arguments:\n${1} ${2} ${3}\n"
    fi
}

echo "$HEADER"

# If the oscam config directory is not found, default to "/tmp" to avoid errors
OSCAM_CFGDIR=$(find_oscam_cfg_dir)
[ -z "$OSCAM_CFGDIR" ] && { echo "WARNING: The output directory for the 'oscam.srvid' file was changed to '/tmp'!"; OSCAM_CFGDIR="/tmp"; }

OSCAM_SRVID="${OSCAM_CFGDIR}/oscam.srvid"

# Create temporary ".srvid" files from different sources
create_srvid_file "https://www.satelitnatv.sk/frekvencie/skylink-sk-19e/" "Skylink" "0D96,0624,FFFE"
create_srvid_file "https://www.satelitnatv.sk/frekvencie/freesat-sk/" "FreeSAT" "0D97,0653,0B02"
create_srvid_file "https://www.satelitnatv.sk/frekvencie/antik-sat-sk/" "AntikSAT" "0B00"

# Backup the original 'oscam.srvid' file
fileSRC="${OSCAM_CFGDIR}/oscam.srvid"
fileDST="/tmp/oscam_-_backup_$(date '+%Y-%m-%d_%H-%M-%S').srvid"
if [ -f "$fileSRC" ]; then
    mv "$fileSRC" "$fileDST"
    echo -e "The original file was backed up: ${fileSRC} >>> ${fileDST}\n"
fi

# Merge all generated ".srvid" files into one file and move to the Oscam config directory
echo "$HEADER" > "$OSCAM_SRVID"
echo -e "### File creation date: $(date '+%Y-%m-%d %H:%M:%S')\n" >> "$OSCAM_SRVID"
cat /tmp/oscam__* >> "$OSCAM_SRVID"
rm -f /tmp/oscam__*
if [ -f "$OSCAM_SRVID" ]; then
    echo "All generated '.srvid' files have been merged into one and moved to: ${OSCAM_SRVID}"
else
    echo "ERROR: The final '.srvid' file could not be created."
fi

exit 0
