# -*- coding: utf-8 -*-
# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# russian and py3 support by sunriser...
# downloading in the background while zaping...
# by beber...03.2022,
# 03.2022 specific for EMC plugin ...
#
# for emc plugin,
# <widget source="Service" render="AglarePosterXEMC" position="100,100" size="185,278" />

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG, eEPGCache
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from Components.Renderer.AglarePosterXDownloadThread import AglarePosterXDownloadThread
from Components.config import config
import os
import socket
import sys
import re
import time
import traceback

from .Converlibr import convtext

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    import queue
    from _thread import start_new_thread
    from urllib.error import HTTPError, URLError
    from urllib.request import urlopen
else:
    import Queue
    from thread import start_new_thread
    from urllib2 import HTTPError, URLError
    from urllib2 import urlopen


epgcache = eEPGCache.getInstance()
if PY3:
    pdbemc = queue.LifoQueue()
else:
    pdbemc = Queue.LifoQueue()


def isMountedInRW(mount_point):
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) > 1 and parts[1] == mount_point:
                return True
    return False


path_folder = "/tmp/imovie"
if os.path.exists("/media/hdd"):
    if isMountedInRW("/media/hdd"):
        path_folder = "/media/hdd/imovie"
elif os.path.exists("/media/usb"):
    if isMountedInRW("/media/usb"):
        path_folder = "/media/usb/imovie"
elif os.path.exists("/media/mmc"):
    if isMountedInRW("/media/mmc"):
        path_folder = "/media/mmc/imovie"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)

try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass


def intCheck():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    return True


class PosterDBEMC(AglarePosterXDownloadThread):
    def __init__(self):
        AglarePosterXDownloadThread.__init__(self)
        self.logdbg = None
        self.pstcanal = None

    def run(self):
        self.logDB("[QUEUE] : Initialized")
        while True:
            canal = pdbemc.get()
            self.logDB("[QUEUE] : {} : {}-{} ({})".format(canal[0], canal[1], canal[2], canal[5]))
            self.pstcanal = convtext(canal[5])
            if self.pstcanal is not None:
                dwn_poster = os.path.join(path_folder, self.pstcanal + ".jpg")
            else:
                print("None type detected - poster not found")
                pdbemc.task_done()  # Per evitare il blocco del thread
                continue
            if os.path.exists(dwn_poster):
                os.utime(dwn_poster, (time.time(), time.time()))
            '''
            if lng == "fr":
                if not os.path.exists(dwn_poster):
                    val, log = self.search_molotov_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                    self.logDB(log)
                if not os.path.exists(dwn_poster):
                    val, log = self.search_programmetv_google(dwn_poster, canal[5], canal[4], canal[3], canal[0])
                    self.logDB(log)
            '''
            if not os.path.exists(dwn_poster):
                val, log = self.search_tmdb(dwn_poster, self.pstcanal, canal[4], canal[3])
                self.logDB(log)
            elif not os.path.exists(dwn_poster):
                val, log = self.search_tvdb(dwn_poster, self.pstcanal, canal[4], canal[3])
                self.logDB(log)
            elif not os.path.exists(dwn_poster):
                val, log = self.search_fanart(dwn_poster, self.pstcanal, canal[4], canal[3])
                self.logDB(log)
            elif not os.path.exists(dwn_poster):
                val, log = self.search_imdb(dwn_poster, self.pstcanal, canal[4], canal[3])
                self.logDB(log)
            elif not os.path.exists(dwn_poster):
                val, log = self.search_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
                self.logDB(log)
            pdbemc.task_done()

    def logDB(self, logmsg):
        try:
            with open("/tmp/AglarePosterXEMC.log", "a") as w:
                w.write("%s\n" % logmsg)
        except Exception as e:
            print('logDB error:', str(e))
            traceback.print_exc()


threadDBemc = PosterDBEMC()
threadDBemc.start()


class AglarePosterXEMC(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.adsl = intCheck()
        if not self.adsl:
            print("Connessione assente, modalità offline.")
            return
        else:
            print("Connessione rilevata.")
        self.canal = [None, None, None, None, None, None]
        self.logdbg = None
        self.pstrNm = None
        self.pstcanal = None
        self.path = path_folder

        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.showPoster)
        except:
            self.timer.callback.append(self.showPoster)

    def applySkin(self, desktop, parent):
        attribs = []
        for (attrib, value,) in self.skinAttributes:
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return
        self.canal = [None, None, None, None, None, None]
        try:
            if isinstance(self.source, ServiceEvent):  # source="Service"
                self.canal[0] = None
                self.canal[1] = self.source.event.getBeginTime()
                event_name = self.source.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                if not PY3:
                    event_name = event_name.encode('utf-8')
                self.canal[2] = event_name
                self.canal[3] = self.source.event.getExtendedDescription()
                self.canal[4] = self.source.event.getShortDescription()
                self.canal[5] = self.source.service.getPath().split(".ts")[0] + ".jpg"
            elif isinstance(self.source, CurrentService):  # source="session.CurrentService"
                self.canal[5] = self.source.getCurrentServiceReference().getPath().split(".ts")[0] + ".jpg"
            else:
                if self.instance:
                    self.instance.hide()
                return

        except Exception as e:
            print("Error (service processing):", str(e))
            if self.instance:
                self.instance.hide()
            return
        try:
            match = re.findall(r".*? - (.*?) - (.*?).jpg", self.canal[5])
            if match and len(match[0]) > 1:
                self.canal[0] = match[0][0].strip()
                if not self.canal[2]:
                    self.canal[2] = match[0][1].strip()
            self.logPoster("Service: {} - {} => {}".format(self.canal[0], self.canal[2], self.canal[5]))
            if self.canal[5]:
                self.timer.start(10, True)
            elif self.canal[0] and self.canal[2]:
                canal_copy = self.canal[:]
                pdbemc.put(canal_copy)
                start_new_thread(self.waitPoster, ())
            else:
                self.logPoster("Not detected...")
                if self.instance:
                    self.instance.hide()
        except Exception as e:
            print("Error (file processing):", str(e))
            if self.instance:
                self.instance.hide()

    def generatePosterPath(self):
        """Genera il percorso completo per il poster."""
        if self.canal[5]:
            pstcanal = convtext(self.canal[5])
            return os.path.join(self.path, str(pstcanal) + ".jpg")
        return None

    def showPoster(self):
        if self.instance:
            self.instance.hide()
        self.pstrNm = self.generatePosterPath()
        if self.pstrNm and os.path.exists(self.pstrNm):
            print('showPosterXEMC----')
            self.logPoster("[LOAD : showPoster] " + self.pstrNm)
            self.instance.setPixmap(loadJPG(self.pstrNm))
            self.instance.setScale(1)
            self.instance.show()

    def waitPoster(self):
        if self.instance:
            self.instance.hide()

        self.pstrNm = self.generatePosterPath()
        if self.pstrNm:
            loop = 180
            found = False
            self.logPoster("[LOOP: waitPosterXEMC] " + self.pstrNm)

            while loop > 0:
                if os.path.exists(self.pstrNm):
                    found = True
                    break
                time.sleep(0.5)
                loop -= 1

            if found:
                self.timer.start(10, True)

    def logPoster(self, logmsg):
        import traceback
        try:
            with open("/tmp/PosterXEMC.log", "a") as w:
                w.write("%s\n" % logmsg)
        except Exception as e:
            print('logPoster error:', str(e))
            traceback.print_exc()
