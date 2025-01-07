#!/bin/sh
## lululla script reset lan
# Salva i DNS attuali se non già fatto
if [ ! -f /etc/resolv-backup.conf ]; then
    grep "nameserver.*" /etc/resolv.conf >> /etc/resolv-backup.conf
fi

# Imposta i DNS di Cloudfire
rm -f /etc/resolv.conf
echo "nameserver 1.1.1.1" > /etc/resolv.conf
echo "nameserver 1.0.0.1" >> /etc/resolv.conf
echo ""
echo "* NETWORK RESTARTED *"
echo "* CLOUDFIRE DNS APPEND TO NAMESERVER *"
echo "> done"

# Disattiva l'interfaccia di rete
ifconfig eth0 down
sleep 2

# Riattiva l'interfaccia di rete
ifconfig eth0 up
sleep 2

# Rinnova DHCP
udhcpc -i eth0

# Riavvia il servizio di rete, se applicabile
if [ -x /etc/init.d/networking ]; then
    /etc/init.d/networking restart
elif command -v systemctl >/dev/null 2>&1; then
    systemctl restart networking
fi

# Forza il routing verso il gateway principale
route del default
route add default gw 192.168.1.1 eth0  # Cambia l'IP con quello del tuo router
echo "Tabella di routing aggiornata."

# Verifica connessione Internet
ping -c 4 8.8.8.8
if [ $? -eq 0 ]; then
    echo "Connessione ristabilita con successo."
else
    echo "Problema di connessione. Verifica la configurazione di rete."
    echo "> Il dispositivo verrà riavviato ora, attendere prego..."
    sleep 3s
    killall -9 enigma2 || echo "Enigma2 non in esecuzione."
fi



