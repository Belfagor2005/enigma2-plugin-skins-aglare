#!/bin/bash

if [ -f /var/lib/dpkg/status ]; then
   STATUS=/var/lib/dpkg/status
   OSTYPE=DreamOs
else
   STATUS=/var/lib/opkg/status
   OSTYPE=OE20
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
	echo "You have Python3 image"
	PYTHON=PY3
else
	echo "You have Python2 image"
	PYTHON=PY2
fi

if [ $OSTYPE = "DreamOs" ]; then
   echo "# Your image is OE2.5/2.6 #"
   echo ""
else
   echo "# Your image is OE2.0 #"
   echo ""
fi


# # Identify the box type from the hostname file
FILE="/etc/image-version"
box_type=$(head -n 1 /etc/hostname)
distro_value=$(grep '^distro=' "$FILE" | awk -F '=' '{print $2}')
distro_version=$(grep '^version=' "$FILE" | awk -F '=' '{print $2}')
python_vers=$(python --version 2>&1)

echo "^^INFORMATION BOX^^:
BOX MODEL: $box_type
OO SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: $distro_value
IMAGE VERSION: $distro_version"
sleep 8
exit 0
