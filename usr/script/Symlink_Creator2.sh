#!/bin/bash
## DESCRIPTION=This script created by Levi45\nThis script will create symlink
LINE="======================================================================="
# Configurazione delle variabili
usrlibpath="/usr/lib"
libpath="/lib"
# images="Immagine"

############################## Funzione per creare i collegamenti simbolici ####################
create_symlinks() {
    local target_lib="$1"
    shift
    for version in "$@"; do
        ln -s "$target_lib" "$usrlibpath/libcrypto.so.$version" > /dev/null 2>&1
        ln -s "$usrlibpath/$target_lib" "$libpath/libcrypto.so.$version" > /dev/null 2>&1
    done
}

######### checking Package: libssl & libcrypto ###########
if [ -f /etc/apt/apt.conf ] ; then
    images="OE2.5 IMAGES:"
    lib_files="/var/lib/dpkg/status"
    list_files="/var/lib/dpkg/info"
elif [ -f /etc/opkg/opkg.conf ] ; then
    images="OE2.0 IMAGES:"
    lib_files="/var/lib/opkg/status"
    list_files="/var/lib/opkg/info"
else
    echo "Sorry, your device does not have the opkg/dpkg folder :("
    exit 1
fi


sleep 3
opkg update > /dev/null 2>&1

############################## libssl ####################
if grep -qs 'Package: libssl3' "$lib_files" ; then
    echo "$images libssl3"
    ln -s libssl.so.3 $usrlibpath/libssl.so.1.1 > /dev/null 2>&1
    ln -s libssl.so.3 $usrlibpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s libssl.so.3 $usrlibpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s libssl.so.3 $usrlibpath/libssl.so.0.9.7 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.1.1 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.0.9.7 > /dev/null 2>&1
elif grep -qs 'Package: libssl1.1' "$lib_files" ; then
    echo "$images libssl1.1"
    ln -s libssl.so.1.1 $usrlibpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s libssl.so.1.1 $usrlibpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s libssl.so.1.1 $usrlibpath/libssl.so.0.9.7 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.1 $libpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.1 $libpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.1 $libpath/libssl.so.0.9.7 > /dev/null 2>&1
elif grep -qs 'Package: libssl1.0.0' "$lib_files" ; then
    echo "$images libssl1.0.0"
    ln -s libssl.so.1.0.0 $usrlibpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s libssl.so.1.0.0 $usrlibpath/libssl.so.0.9.7 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.0.0 $libpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.0.0 $libpath/libssl.so.0.9.7 > /dev/null 2>&1
elif grep -qs 'Package: libssl1.0.2' "$lib_files" ; then
    echo "$images libssl1.0.2"
    ln -s libssl.so.1.0.2 $usrlibpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s libssl.so.1.0.2 $usrlibpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s libssl.so.1.0.2 $usrlibpath/libssl.so.0.9.7 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.0.2 $libpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.0.2 $libpath/libssl.so.0.9.8 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.1.0.2 $libpath/libssl.so.0.9.7 > /dev/null 2>&1
elif grep -qs 'Package: libssl0.9.8' "$lib_files" ; then
    echo "$images libssl0.9.8"
    ln -s libssl.so.0.9.8 $usrlibpath/libssl.so.0.9.7 > /dev/null 2>&1
    ln -s libssl.so.0.9.8 $usrlibpath/libssl.so.1.0.0 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.0.9.8 $libpath/libssl.so.0.9.7 > /dev/null 2>&1
    ln -s $usrlibpath/libssl.so.0.9.8 $libpath/libssl.so.1.0.0 > /dev/null 2>&1
else ## Try to Download libssl from feed
    if [ -n "$(opkg list | grep libssl3)" ]; then
        echo "installing libssl3"
        if [ -f /etc/apt/apt.conf ] ; then
            apt-get install --reinstall libssl3 > /dev/null 2>&1
        elif [ -f /etc/opkg/opkg.conf ] ; then
            opkg install --force-overwrite --force-depends libssl3 > /dev/null 2>&1
        fi
        ln -s libssl.so.3 $usrlibpath/libssl.so.1.1 > /dev/null 2>&1
        ln -s libssl.so.3 $usrlibpath/libssl.so.1.0.0 > /dev/null 2>&1
        ln -s libssl.so.3 $usrlibpath/libssl.so.0.9.8 > /dev/null 2>&1
        ln -s libssl.so.3 $usrlibpath/libssl.so.0.9.7 > /dev/null 2>&1
        ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.1.1 > /dev/null 2>&1
        ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.1.0.0 > /dev/null 2>&1
        ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.0.9.8 > /dev/null 2>&1
        ln -s $usrlibpath/libssl.so.3 $libpath/libssl.so.0.9.7 > /dev/null 2>&1
    else
        echo "libssl3 package not available in the feed."
    fi
fi
############################## Gestione delle librerie libcrypto ####################
if grep -qs 'Package: libcrypto3' $lib_files ; then
    echo "$images libcrypto3"
    create_symlinks "libcrypto.so.3" "1.1" "1.0.0" "0.9.8" "0.9.7"

elif grep -qs 'Package: libcrypto1.1' $lib_files ; then
    echo "$images libcrypto1.1"
    create_symlinks "libcrypto.so.1.1" "1.0.0" "0.9.8" "0.9.7"

elif grep -qs 'Package: libcrypto1.0.0' $lib_files ; then
    echo "$images libcrypto.1.0.0"
    create_symlinks "libcrypto.so.1.0.0" "0.9.8" "0.9.7"

elif grep -qs 'Package: libcrypto1.0.2' $lib_files ; then
    echo "$images libcrypto.1.0.2"
    create_symlinks "libcrypto.so.1.0.2" "1.0.0" "0.9.8" "0.9.7"

elif grep -qs 'Package: libcrypto0.9.8' $lib_files ; then
    echo "$images libcrypto.0.9.8"
    create_symlinks "libcrypto.so.0.9.8" "0.9.7" "1.0.0"

elif [ -f "$usrlibpath/libcrypto.so.3" ] ; then
    echo "$images libcrypto3"
    create_symlinks "libcrypto.so.3" "1.1" "1.0.0" "0.9.8" "0.9.7"

elif [ -f "$usrlibpath/libcrypto.so.1.1" ] ; then
    echo "$images libcrypto1.1"
    create_symlinks "libcrypto.so.1.1" "1.0.0" "0.9.8" "0.9.7"

elif [ -f "$usrlibpath/libcrypto.so.1.0.0" ] ; then
    echo "$images libcrypto.1.0.0"
    create_symlinks "libcrypto.so.1.0.0" "0.9.8" "0.9.7"

elif [ -f "$usrlibpath/libcrypto.so.1.0.2" ] ; then
    echo "$images libcrypto.1.0.2"
    create_symlinks "libcrypto.so.1.0.2" "1.0.0" "0.9.8" "0.9.7"

elif [ -f "$usrlibpath/libcrypto.so.0.9.8" ] ; then
    echo "$images libcrypto.0.9.8"
    create_symlinks "libcrypto.so.0.9.8" "0.9.7" "1.0.0"

else
    # Tentativo di scaricare libcrypto dal feed
    opkg update
    if opkg list | grep -q libcrypto3 ; then
        echo "Installo libcrypto3"
        if [ -f /etc/apt/apt.conf ] ; then
            apt-get install --reinstall libcrypto3 -y > /dev/null 2>&1
        elif [ -f /etc/opkg/opkg.conf ] ; then
            opkg install --force-overwrite --force-depends libcrypto3 > /dev/null
        fi
        create_symlinks "libcrypto.so.3" "1.1" "1.0.0" "0.9.8" "0.9.7"
    else
        echo "libcrypto3 non è disponibile nel feed"
    fi
fi

exit 0
