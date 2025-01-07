#!/bin/bash
#DESCRIPTION=SRVID-TWOJEIP
HEADER="
#################################################################################
### Script is designed to download and replace the 'oscam.srvid' file.
### The '.srvid' generator is used via the online web page: HTTP://KOS.TWOJEIP.NET
### Script written by s3n0, 2021-02-17: https://github.com/s3n0
#################################################################################
"

#################################################################################

# Function to find the Oscam configuration directory
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

#################################################################################

echo "$HEADER"

# The URL for the .srvid file, adjust if necessary
URL="http://kos.twojeip.net/download.php?download[]=pack-hdplus&download[]=pack-mtv&download[]=pack-skylink&download[]=pack-austriasat&download[]=pack-orfdigital&download[]=pack-skygermany"

# Find the Oscam configuration directory
OSCAM_CFGDIR=$(find_oscam_cfg_dir)

# Validate that the Oscam configuration directory is found
if [ -z "$OSCAM_CFGDIR" ]; then
    echo "ERROR: Oscam configuration directory not found!"
    exit 1
fi

# Backup the current oscam.srvid file
cp -f "${OSCAM_CFGDIR}/oscam.srvid" "/tmp/oscam.srvid_backup"
echo "Backup of current oscam.srvid created at /tmp/oscam.srvid_backup."

# Start downloading the new oscam.srvid file
echo -e "Downloading file...\n- from: ${URL}\n- to: ${OSCAM_CFGDIR}/oscam.srvid"

# Validate the URL before attempting to download
if wget --spider "${URL}" 2>/dev/null; then
    wget -q -O "${OSCAM_CFGDIR}/oscam.srvid" "${URL}"
    if [ $? -eq 0 ]; then
        echo "...Download completed successfully!"
    else
        echo "...ERROR: Failed to download the file!"
        exit 1
    fi
else
    echo "...ERROR: The online URL ${URL} does not exist!"
    exit 1
fi
exit 0
