from Components.Converter.Converter import Converter
from Components.Element import cached


class AglareRouteInfo(Converter, object):
    Info = 0
    Lan = 1
    Wifi = 2
    Modem = 3

    def __init__(self, type):
        Converter.__init__(self, type)
        if type == 'Info':
            self.type = self.Info
        elif type == 'Lan':
            self.type = self.Lan
        elif type == 'Wifi':
            self.type = self.Wifi
        elif type == 'Modem':
            self.type = self.Modem

    @cached
    def getBoolean(self):
        info = False
        for line in open('/proc/net/route'):
            if self.type == self.Lan and line.split()[0] == 'eth0' and line.split()[3] == '0003':
                info = True
            elif self.type == self.Wifi and (line.split()[0] == 'wlan0' or line.split()[0] == 'ra0') and line.split()[3] == '0003':
                info = True
            elif self.type == self.Modem and line.split()[0] == 'ppp0' and line.split()[3] == '0003':
                info = True

        return info

    boolean = property(getBoolean)

    @cached
    def getText(self):
        info = ''
        for line in open('/proc/net/route'):
            if self.type == self.Info and line.split()[0] == 'eth0' and line.split()[3] == '0003':
                info = 'lan'
            elif self.type == self.Info and (line.split()[0] == 'wlan0' or line.split()[0] == 'ra0') and line.split()[3] == '0003':
                info = 'wifi'
            elif self.type == self.Info and line.split()[0] == 'ppp0' and line.split()[3] == '0003':
                info = '3g'

        return info

    text = property(getText)

    def changed(self, what):
        Converter.changed(self, what)


"""
<screen name="RouteInfoScreen" position="center,center" size="1280,720" title="Network Information">
    <!-- Widget per visualizzare lo stato della connessione LAN -->
    <widget name="lanStatus" source="ServiceEvent" render="Label" position="50,100" size="1180,50" font="Bold; 26" backgroundColor="background" transparent="1" noWrap="1" zPosition="1" foregroundColor="green" valign="center">
        <convert type="AglareRouteInfo">Lan</convert>
    </widget>

    <!-- Widget per visualizzare lo stato della connessione Wi-Fi -->
    <widget name="wifiStatus" source="ServiceEvent" render="Label" position="50,160" size="1180,50" font="Bold; 26" backgroundColor="background" transparent="1" noWrap="1" zPosition="1" foregroundColor="yellow" valign="center">
        <convert type="AglareRouteInfo">Wifi</convert>
    </widget>

    <!-- Widget per visualizzare lo stato della connessione Modem -->
    <widget name="modemStatus" source="ServiceEvent" render="Label" position="50,220" size="1180,50" font="Bold; 26" backgroundColor="background" transparent="1" noWrap="1" zPosition="1" foregroundColor="blue" valign="center">
        <convert type="AglareRouteInfo">Modem</convert>
    </widget>

    <!-- Widget per visualizzare informazioni generali sulla connessione -->
    <widget name="networkInfo" source="ServiceEvent" render="Label" position="50,280" size="1180,50" font="Bold; 26" backgroundColor="background" transparent="1" noWrap="1" zPosition="1" foregroundColor="red" valign="center">
        <convert type="AglareRouteInfo">Info</convert>
    </widget>
</screen>
"""