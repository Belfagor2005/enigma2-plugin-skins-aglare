#!/bin/sh
## DESCRIPTION=This script created by Levi45\nInstall wget
## Installin File

PYTHON_VERSION=$(python -c "import platform; print(platform.python_version())")

if [ -f /etc/apt/apt.conf ]; then
    STATUS='/var/lib/dpkg/status'
    OS='DreamOS'
    if ! command -v wget &> /dev/null; then
        echo "Installing wget on DreamOS"
        sudo apt update && sudo apt install -y wget
    else
        echo "wget is already installed on DreamOS"
    fi
elif [ -f /etc/opkg/opkg.conf ]; then
    STATUS='/var/lib/opkg/status'
    OS='Opensource'
    # Installazione di wget per Opensource (OPKG)
    if ! command -v wget &> /dev/null; then
        echo "Installing wget on Opensource"
        sudo opkg update && sudo opkg install wget
    else
        echo "wget is already installed on Opensource"
    fi
fi

sync
echo "#########################################################"
echo "#                           Levi45                      #"
echo "#########################################################"
echo "#                 Wget INSTALLED SUCCESSFULLY           #"
echo "#########################################################"
echo "#                    SATELLITE-FORUM.COM                #"
echo "#########################################################"
exit 0
