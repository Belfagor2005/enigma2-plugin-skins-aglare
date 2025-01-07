#!/bin/bash
if [ -f /etc/apt/sources.list.d/plexdream.list ]; then
	rm /etc/apt/sources.list.d/plexdream.list
fi
if [ -f /etc/apt/sources.list.d/plugins-boxpirates.list ]; then
	if [ $(grep "boxpirates.dynvpn.de" /etc/apt/sources.list.d/plugins-boxpirates.list|wc -l) -gt 0 ]; then
		if [ $(uname -m) == "aarch64" ]; then
    		echo deb [trusted=yes] http://plugins.boxpirates.to/apt64/ ./ > /etc/apt/sources.list.d/plugins-boxpirates.list
		else
    		echo deb [trusted=yes] http://plugins.boxpirates.to/apt/ ./ > /etc/apt/sources.list.d/plugins-boxpirates.list
		fi
	fi
else
	if [ $(uname -m) == "aarch64" ]; then
    	echo deb [trusted=yes] http://plugins.boxpirates.to/apt64/ ./ > /etc/apt/sources.list.d/plugins-boxpirates.list
	else
    	echo deb [trusted=yes] http://plugins.boxpirates.to/apt/ ./ > /etc/apt/sources.list.d/plugins-boxpirates.list
	fi
fi
apt-get update
apt-get -f -y --assume-yes install enigma2-plugin-extensions-plexdream
sleep 3
echo ""
echo "************************"
read -p "Gui neustarten? (j/n): " response </dev/tty
if [ "$response" == "j" ]; then
    echo "enigma2 wird neugestartet"
    systemctl restart enigma2
else
    echo "damit das Plugin aktiv wird müssen Sie enigma2 neustarten"
fi
echo "... install finish"
exit 0
