# -*- coding: utf-8 -*-
# ArBoxInfo
# Copyright (c)Tikhon 2019
# v.1.0
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option)any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from Components.Converter.Poll import Poll
from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Tools.Directories import fileExists
from os import popen
import re
import os


class AglareBoxInfo(Poll, Converter, object):
    Boxtype = 0
    CpuInfo = 1
    HddTemp = 2
    TempInfo = 3
    FanInfo = 4
    Upinfo = 5
    CpuLoad = 6
    CpuSpeed = 7
    SkinInfo = 8
    TimeInfo = 9
    TimeInfo2 = 10
    TimeInfo3 = 11
    TimeInfo4 = 12
    PythonVersion = 13

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 1000
        self.poll_enabled = True
        self.type = {'Boxtype': self.Boxtype,
                     'CpuInfo': self.CpuInfo,
                     'HddTemp': self.HddTemp,
                     'TempInfo': self.TempInfo,
                     'FanInfo': self.FanInfo,
                     'Upinfo': self.Upinfo,
                     'CpuLoad': self.CpuLoad,
                     'CpuSpeed': self.CpuSpeed,
                     'SkinInfo': self.SkinInfo,
                     'TimeInfo': self.TimeInfo,
                     'TimeInfo2': self.TimeInfo2,
                     'TimeInfo3': self.TimeInfo3,
                     'TimeInfo4': self.TimeInfo4,
                     'PythonVersion': self.PythonVersion}[type]

    def imageinfo(self):
        imageinfo = ''
        if os.path.isfile('/usr/lib/opkg/status'):
            imageinfo = '/usr/lib/opkg/status'
        elif os.path.isfile('/usr/lib/ipkg/status'):
            imageinfo = '/usr/lib/ipkg/status'
        elif os.path.isfile('/var/lib/opkg/status'):
            imageinfo = '/var/lib/opkg/status'
        elif os.path.isfile('/var/opkg/status'):
            imageinfo = '/var/opkg/status'
        return imageinfo

    @cached
    def getText(self):
        if self.type == self.Boxtype:
            box = software = ''
            if os.path.isfile('/proc/version'):
                enigma = open('/proc/version').read().split()[2]
            try:
                from Components.SystemInfo import BoxInfo
                DISPLAYBRAND = BoxInfo.getItem("displaybrand")
                if DISPLAYBRAND.startswith('Maxytec'):
                    DISPLAYBRAND = 'Novaler'
                DISPLAYMODEL = BoxInfo.getItem("displaymodel")
                box = DISPLAYBRAND + " " + DISPLAYMODEL
            except ImportError:
                box = os.popen("head -n 1 /etc/hostname").read().split()[0]

            issue_file = "/etc/issue"
            if os.path.isfile(issue_file):

                def get_boxinfo(distro_key, version_key, build_key, separator):
                    """
                    Recupera informazioni dal modulo BoxInfo.
                    """
                    try:
                        from Components.SystemInfo import BoxInfo
                        distro = BoxInfo.getItem(distro_key)
                        version = BoxInfo.getItem(version_key)
                        build = BoxInfo.getItem(build_key)if build_key else None

                        if distro and version:
                            if build:
                                return distro.upper() + " " + version + separator + build
                            return distro.upper() + " " + version
                    except ImportError:
                        print("Errore: Modulo BoxInfo non trovato.")
                    except Exception as e:
                        print("Errore durante il recupero delle informazioni da BoxInfo:", e)
                    return ""

                with open(issue_file, 'r')as f:
                    for line in f:
                        # Pulisci e formatta la riga
                        line = line.strip().lower().capitalize()
                        line = line.replace('Open vision enigma2 image for', '')\
                                   .replace('More information : https://openvision.tech', '')\
                                   .replace('%d, %t - (%s %r %m)', '')\
                                   .replace('Release', 'r')\
                                   .replace('Welcome to openatv', '')\
                                   .replace('Welcome to teamblue', '')\
                                   .replace('Welcome to openbh', '')\
                                   .replace('Welcome to openvix', '')\
                                   .replace('Welcome to opendroid', '')\
                                   .replace('Welcome to openspa', '')\
                                   .replace('\n', '')\
                                   .replace(r'\l', '')\
                                   .replace('\\', '').strip()
                        if line:
                            software += line

                if software.startswith("Egami"):
                    software = get_boxinfo("displaydistro", "imgversion", "imagedevbuild", " - R ")
                elif software.startswith("Openbh") or software.startswith("Openvix"):
                    software = get_boxinfo("displaydistro", "imgversion", "imagebuild", " ")
                elif software.startswith("Pure2"):
                    software = get_boxinfo("displaydistro", "imgversion", "imagedevbuild", " - R ")
                elif software.startswith("Openatv"):
                    software = get_boxinfo("displaydistro", "imgversion", None, " ")

                software = ' : %s ' % software.strip()

            vti_file = "/etc/vtiversion.info"
            if os.path.isfile(vti_file):
                software = ""
                with open(vti_file, 'r')as f:
                    for line in f:
                        # Estrai i dati dalla riga
                        parts = line.split()
                        if len(parts) > 1:
                            software += parts[0].split('-')[0] + ' ' + parts[-1].strip()
                software = ' : %s ' % software.strip()

            return '%s%s' % (box, software)

        elif self.type == self.PythonVersion:
            pythonversion = ''
            try:
                from Components.About import about
                pythonversion = about.getPythonVersionString()
            except ImportError:
                pass
            return '%s' % (pythonversion)
        elif self.type == self.CpuInfo:
            cpu_count = 0
            info = cpu_speed = cpu_info = core = ''
            core = _('core')
            cores = _('cores')
            if os.path.isfile('/proc/cpuinfo'):
                for line in open('/proc/cpuinfo'):
                    if 'system type' in line:
                        info = line.split(':')[-1].split()[0].strip().strip('\n')
                    elif 'cpu MHz' in line:
                        cpu_speed = line.split(':')[-1].strip().strip('\n')
                    elif 'cpu type' in line:
                        info = line.split(':')[-1].strip().strip('\n')
                    elif 'model name' in line or 'Processor' in line:
                        info = line.split(':')[-1].strip().strip('\n').replace('Processor ', '')
                    elif line.startswith('processor'):
                        cpu_count += 1
                if info.startswith('ARM') and os.path.isfile('/proc/stb/info/chipset'):
                    for line in open('/proc/cpuinfo'):
                        if 'model name' in line or 'Processor' in line:
                            info = line.split(':')[-1].split()[0].strip().strip('\n')
                            info = '%s (%s)' % (open('/proc/stb/info/chipset').readline().strip().lower().replace('hi3798mv200', 'Hi3798MV200').replace('bcm', 'BCM').replace('brcm', 'BCM').replace('7444', 'BCM7444').replace('7278', 'BCM7278'), info)
                if not cpu_speed:
                    try:
                        cpu_speed = int(open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq').read()) / 1000
                    except:
                        try:
                            import binascii
                            f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
                            clockfrequency = f.read()
                            f.close()
                            cpu_speed = "%s" % str(int(binascii.hexlify(clockfrequency), 16) / 1000000)
                        except:
                            cpu_speed = '-'
                if cpu_info == '':
                    return _('%s, %s MHz (%d %s)') % (info, cpu_speed, cpu_count, cpu_count > 1 and cores or core)
            else:
                return _('No info')

        elif self.type == self.HddTemp:
            textvalue = 'No info'
            info = 'N/A'
            try:
                out_line = popen('hddtemp -n -q /dev/sda').readline()
                info = 'HDD: Temp:' + out_line[:2] + str('\xc2\xb0') + 'C'
                textvalue = info
            except:
                pass
            return textvalue

        elif self.type == self.TempInfo:
            info = 'N/A'
            try:
                if os.path.exists('/proc/stb/sensors/temp0/value') and os.path.exists('/proc/stb/sensors/temp0/unit'):
                    info = '%s%s%s' % (open('/proc/stb/sensors/temp0/value').read().strip('\n'), str('\xc2\xb0'), open('/proc/stb/sensors/temp0/unit').read().strip('\n'))
                elif os.path.exists('/proc/stb/fp/temp_sensor_avs'):
                    info = '%s%sC' % (open('/proc/stb/fp/temp_sensor_avs').read().strip('\n'), str('\xc2\xb0'))
                elif os.path.exists('/proc/stb/fp/temp_sensor'):
                    info = '%s%sC' % (open('/proc/stb/fp/temp_sensor').read().strip('\n'), str('\xc2\xb0'))
                elif os.path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
                    info = '%s%sC' % (open('/sys/devices/virtual/thermal/thermal_zone0/temp').read()[:2].strip('\n'), str('\xc2\xb0'))
                elif os.path.exists('/proc/hisi/msp/pm_cpu'):
                    try:
                        info = '%s%sC' % (re.search(r'temperature = (\d+)degree', open('/proc/hisi/msp/pm_cpu').read()).group(1), str('\xc2\xb0'))
                    except:
                        pass
            except:
                info = 'N/A'
            if self.type is self.TempInfo:
                info = (info[0:2] + 'C')
            return info

        elif self.type == self.FanInfo:
            info = 'N/A'
            try:
                if os.path.exists('/proc/stb/fp/fan_speed'):
                    info = open('/proc/stb/fp/fan_speed').read().strip('\n')
                elif os.path.exists('/proc/stb/fp/fan_pwm'):
                    info = open('/proc/stb/fp/fan_pwm').read().strip('\n')
            except:
                info = 'N/A'
            if self.type is self.FanInfo:
                info = 'Fan: ' + info
            return info

        elif self.type == self.Upinfo:
            try:
                with open('/proc/uptime', 'r')as file:
                    uptime_info = file.read().split()
            except:
                return ' '
                uptime_info = None
            if uptime_info is not None:
                total_seconds = float(uptime_info[0])
                MINUTE = 60
                HOUR = MINUTE * 60
                DAY = HOUR * 24
                days = int(total_seconds / DAY)
                hours = int((total_seconds % DAY) / HOUR)
                minutes = int((total_seconds % HOUR) / MINUTE)
                seconds = int(total_seconds % MINUTE)
                uptime = ''
                if days > 0:
                    uptime += str(days) + ' ' + (days == 1 and 'day' or 'days') + ' '
                if len(uptime) > 0 or hours > 0:
                    uptime += str(hours) + ' ' + (hours == 1 and 'hour' or 'hours') + ' '
                if len(uptime) > 0 or minutes > 0:
                    uptime += str(minutes) + ' ' + (minutes == 1 and 'minute' or 'minutes')
                return 'Time in work: %s' % uptime

        elif self.type == self.CpuLoad:
            info = ''
            try:
                if os.path.exists('/proc/loadavg'):
                    l = open('/proc/loadavg', 'r')
                    load = l.readline(4)
                    l.close()
            except:
                load = ''
            info = load.replace('\n', '').replace(' ', '')
            return _('CPU Load: %s') % info

        elif self.type == self.CpuSpeed:
            info = 0
            try:
                for line in open('/proc/cpuinfo').readlines():
                    line = [x.strip()for x in line.strip().split(':')]
                    if line[0] == 'cpu MHz':
                        info = '%1.0f' % float(line[1])
                if not info:
                    try:
                        info = int(open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq').read()) / 1000
                    except:
                        try:
                            import binascii
                            info = int(int(binascii.hexlify(open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb').read()), 16) / 100000000) * 100
                        except:
                            info = '-'
                return 'CPU Speed: %s MHz' % info
            except:
                return ''

        elif self.type == self.SkinInfo:
            if fileExists('/etc/enigma2/settings'):
                try:
                    for line in open('/etc/enigma2/settings'):
                        if 'config.skin.primary_skin' in line:
                            return (_('Skin: ')) + line.replace('/skin.xml', ' ').split('=')[1]
                except:
                    return

        elif self.type == self.TimeInfo:
            if not config.timezone.val.value.startswith('(GMT)'):
                return config.timezone.val.value[4:7]
            else:
                return '+0'

        elif self.type == self.TimeInfo2:
            if not config.timezone.val.value.startswith('(GMT)'):
                return (_('Timezone: ')) + config.timezone.val.value[0:10]
            else:
                return (_('Timezone: ')) + 'GMT+00:00'

        elif self.type == self.TimeInfo3:
            if not config.timezone.val.value.startswith('(GMT)'):
                return (_('Timezone:')) + config.timezone.val.value[0:20]
            else:
                return '+0'

        elif self.type == self.TimeInfo4:
            if not config.timezone.area.value.startswith('(GMT)'):
                return (_('Part~of~the~light:')) + config.timezone.area.value[0:12]
            else:
                return '+0'

    text = property(getText)
