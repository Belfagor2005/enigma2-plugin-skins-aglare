#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
****************************************
*        modded by Lululla             *
*             26/04/2024               *
****************************************
# --------------------#
# Info Linuxsat-support.com  corvoboys.org
'''
# by 2boom 4bob@ua.fm
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.config import config
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import (SCOPE_SKIN, resolveFilename)
from Tools.LoadPixmap import LoadPixmap
from enigma import getDesktop
import os
import sys

global path_folder_log


version = '1.3'
path_folder_log = '/media/usb/'


def isMountReadonly(mnt):
    mount_point = ''
    try:
        with open('/proc/mounts', 'r') as f:
            for line in f:
                line_parts = line.split()
                if len(line_parts) < 4:
                    continue
                device, mount_point, filesystem, flags = line_parts[:4]
                if mount_point == mnt:
                    return 'ro' in flags
    except IOError as e:
        # Gestione errori di I/O (es. file non accessibile)
        print("Errore di I/O: %s" % str(e), file=sys.stderr)
    except Exception as err:
        # Gestione generale delle eccezioni
        print("Errore: %s" % str(err), file=sys.stderr)
    return "mount: '%s' doesn't exist" % mnt


def paths():
    return [
        "/media/hdd", "/media/usb", "/media/mmc", "/home/root", "/home/root/logs/",
        "/media/hdd/logs", "/media/usb/logs", "/ba/", "/ba/logs"
    ]


def crashlogPath():
    path_folder_log = '/media/hdd/'
    crashlogPath_found = False
    try:
        path_folder_log = config.crash.debug_path.value
    except (KeyError, AttributeError):
        path_folder_log = None
    print('path_folder_log:', path_folder_log)
    if path_folder_log is None:
        possible_paths = paths()
        for path in possible_paths:
            if os.path.exists(path) and not isMountReadonly(path):
                path_folder_log = path + "/"
                break
        else:
            path_folder_log = "/tmp/"

    try:
        for crashlog in os.listdir(path_folder_log):
            if crashlog.endswith(".log") and ("crashlog" in crashlog or "twiste" in crashlog):
                crashlogPath_found = True
                break
    except OSError as e:
        print("Errore nell'accesso alla directory di crashlog: %s" % str(e))
        crashlogPath_found = False
    print('path_folder_log 2 :', path_folder_log)
    return crashlogPath_found


def find_log_files():
    log_files = []
    possible_paths = paths()
    for path in possible_paths:
        if os.path.exists(path) and not isMountReadonly(path):
            try:
                for file in os.listdir(path):
                    if file.endswith(".log") and ("crashlog" in file or "twiste" in file):
                        log_files.append(os.path.join(path, file))
            except OSError as e:
                print("Errore durante l'accesso a:", path, str(e))
    return log_files


def delete_log_files(files):
    for file in files:
        try:
            os.remove(file)
            print('File eliminato:', file)
        except OSError as e:
            print("Errore durante l'eliminazione di {file}:", str(e))


class CrashLogScreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 2560:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="1280,1000" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="160,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="415,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="670,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="925,900" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="160,948" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="415,948" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="670,948" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="925,948" size="250,6" zPosition="12" />
        <eLabel name="" position="1194,901" size="52,52" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 17" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="80,67" size="1137,781" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (80, 5), size = (580, 46), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0), # index 2 is the Menu Titel
            MultiContentEntryText(pos = (80, 55), size = (580, 38), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1), # index 3 is the Description
            MultiContentEntryPixmapAlphaTest(pos = (5, 35), size = (51, 40), png = 2), # index 4 is the pixmap
                ],
        "fonts": [gFont("Regular", 42),gFont("Regular", 34)],
        "itemHeight": 100
        }
                </convert>
            </widget>
        </screen>
        """

    elif sz_w == 1920:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="1000,880" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="0,814" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="252,813" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="499,814" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="749,814" size="250,45" zPosition="11" font="Regular; 26" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="0,858" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="250,858" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="500,858" size="250,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="750,858" size="250,6" zPosition="12" />
        <eLabel name="" position="933,753" size="52,52" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 17" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="20,10" size="961,781" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (70, 2), size = (580, 34), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
            MultiContentEntryText(pos = (80, 29), size = (580, 30), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
            MultiContentEntryPixmapAlphaTest(pos = (5, 15), size = (51, 40), png = 2), # index 4 is the pixmap
                ],
        "fonts": [gFont("Regular", 30),gFont("Regular", 26)],
        "itemHeight": 70
        }
                </convert>
            </widget>
        </screen>
        """
    else:
        skin = """
        <screen name="crashlogscreen" position="center,center" size="640,586" title="View or Remove Crashlog files">
        <widget source="Redkey" render="Label" position="6,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Greenkey" render="Label" position="166,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Yellowkey" render="Label" position="325,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <widget source="Bluekey" render="Label" position="485,536" size="160,35" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="5,570" size="160,6" zPosition="12" />
        <eLabel backgroundColor="#0000ff00" position="165,570" size="160,6" zPosition="12" />
        <eLabel backgroundColor="#00ffff00" position="325,570" size="160,6" zPosition="12" />
        <eLabel backgroundColor="#000000ff" position="480,570" size="160,6" zPosition="12" />
        <eLabel name="" position="586,495" size="42,35" backgroundColor="#003e4b53" halign="center" valign="center" transparent="0" cornerRadius="26" font="Regular; 14" zPosition="1" text="INFO" />
        <widget source="menu" render="Listbox" position="13,6" size="613,517" scrollbarMode="showOnDemand">
        <convert type="TemplatedMultiContent">
        {"template": [
            MultiContentEntryText(pos = (46, 1), size = (386, 22), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
            MultiContentEntryText(pos = (53, 19), size = (386, 20), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
            MultiContentEntryPixmapAlphaTest(pos = (3, 10), size = (34, 26), png = 2), # index 4 is the pixmap
                ],
        "fonts": [gFont("Regular", 18),gFont("Regular", 16)],
        "itemHeight": 50
        }
                </convert>
        </widget>
        </screen>
        """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "EPGSelectActions"],
                                      {
                                      "ok": self.Ok,
                                      "cancel": self.exit,
                                      "back": self.exit,
                                      "red": self.exit,
                                      "green": self.Ok,
                                      "yellow": self.YellowKey,
                                      "blue": self.BlueKey,
                                      "info": self.infoKey,
                                      })
        self["Redkey"] = StaticText(_("Close"))
        self["Greenkey"] = StaticText(_("View"))
        self["Yellowkey"] = StaticText(_("Remove"))
        self["Bluekey"] = StaticText(_("Remove All"))
        self.list = []
        self["menu"] = List(self.list)
        self.CfgMenu()

    def CfgMenu(self):
        self.list = []
        path_folder_log = "/tmp/"
        log_files = find_log_files()
        if log_files:
            paths_to_search = ' '.join(log_files)
        else:
            paths_to_search = ("%s*crash*.log \
                               %slogs/*crash*.log \
                               /home/root/*crash*.log \
                               /home/root/logs/*crash*.log \
                               %stwisted.log \
                               /media/usb/logs/*crash*.log \
                               /media/usb/*crash*.log \
                               /media/hdd/*crash*.log \
                               /media/hdd/logs/*crash*.log \
                               /media/mmc/*crash*.log \
                               /ba/*crash*.log \
                               /ba/logs/*crash*.log") % (path_folder_log, path_folder_log, path_folder_log)
            # paths_to_search = "%s*crash*.log %slogs/*crash*.log /home/root/*crash*.log /home/root/logs/*crash*.log %stwisted.log /media/usb/logs/*crash*.log /media/usb/*crash*.log" % (path_folder_log, path_folder_log, path_folder_log)
        crashfiles = os.popen("ls -lh " + paths_to_search).read()
        print('crashfiles:', crashfiles)  # Stampa per debug
        cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
        minipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN, str(cur_skin) + "/mainmenu/crashlog.png"))
        for line in crashfiles.splitlines():
            print("Linea di crashfile:", line)
            item = line.split()
            if len(item) >= 9:
                file_size = item[4]  # Dimensione del file
                file_date = " ".join(item[5:8])  # Data e ora del file
                file_name = item[8]  # Nome del file con percorso
                display_name = (file_name.split("/")[-1],  # Mostra solo il nome del file
                                "Dimensione: %s - Data: %s" % (file_size, file_date),  # Dettagli
                                minipng,  # Icona appropriata
                                file_name)  # Percorso completo del file
                if display_name not in self.list:
                    print('Aggiungendo alla lista:', display_name)  # Debug per verificare l'aggiunta
                    self.list.append(display_name)
        self["menu"].setList(self.list)
        self["actions"] = ActionMap(["OkCancelActions"], {"cancel": self.close}, -1)

    def Ok(self):
        item = self["menu"].getCurrent()
        global Crashfile
        try:
            base_dir = item[3]
            filename = item[0]  # + ".log"
            print('base_dir=', base_dir)
            print('filename=', filename)
            # 17:53:17.5409 base_dir= /home/root/logs/20240922-165717-enigma2-crash.log
            # 17:53:17.5410 filename= 20240922-165717-enigma2-crash.log.log
            Crashfile = str(base_dir)
            self.session.openWithCallback(self.CfgMenu, LogScreen)
        except (IndexError, TypeError, KeyError) as e:
            print(e)
            Crashfile = " "

    def YellowKey(self):
        item = self["menu"].getCurrent()
        try:
            base_dir = item[3]
            # filename = item[0]  # + ".log"
            file_path = str(base_dir)
            print('YellowKey file_path=', file_path)
            os.remove(file_path)
            self.mbox = self.session.open(MessageBox, (_("Removed %s") % (file_path)), MessageBox.TYPE_INFO, timeout=4)
        except (IndexError, TypeError, KeyError) as e:
            self.mbox = self.session.open(MessageBox, (_("Failed to remove file due to an error: %s") % str(e)), MessageBox.TYPE_INFO, timeout=4)
        except OSError as e:
            self.mbox = self.session.open(MessageBox, (_("Failed to remove file: %s") % str(e)), MessageBox.TYPE_INFO, timeout=4)
        except Exception as e:
            self.mbox = self.session.open(MessageBox, (_("An unexpected error occurred: %s") % str(e)), MessageBox.TYPE_INFO, timeout=4)
        self.CfgMenu()

    def BlueKey(self):
        try:
            log_files = find_log_files()
            if log_files:
                paths_to_search = ' '.join(log_files)
            else:
                paths_to_search = "%s*crash*.log %slogs/*crash*.log /home/root/*crash*.log /home/root/logs/*crash*.log %stwisted.log /media/usb/logs/*crash*.log /media/usb/*crash*.log" % (path_folder_log, path_folder_log, path_folder_log)
            crashfiles = os.popen("ls -lh " + paths_to_search).read()
            for line in crashfiles.splitlines():  # Dividi l'output in linee
                item = line.split()
                if len(item) >= 9:  # Assicurati che ci siano abbastanza informazioni
                    file_name = item[8]  # Nome del file con percorso
                    print('BlueKey file_name=', file_name)
                    os.remove(file_name)
            self.mbox = self.session.open(MessageBox, (_("Removed All Crashlog Files")), MessageBox.TYPE_INFO, timeout=4)
        except (OSError, IOError) as e:
            self.mbox = self.session.open(MessageBox, (_("Failed to remove some files: %s") % str(e)), MessageBox.TYPE_INFO, timeout=4)
        except Exception as e:
            self.mbox = self.session.open(MessageBox, (_("An unexpected error occurred: %s") % str(e)), MessageBox.TYPE_INFO, timeout=4)
        self.CfgMenu()

    def infoKey(self):
        self.session.open(MessageBox, _("Crashlog Viewer  ver. %s\n\nDeveloper: 2boom\n\nModifier: Evg77734\n\nUpdate from Lululla\nHomepage: gisclub.tv") % version, MessageBox.TYPE_INFO)

    def exit(self):
        self.close()


class LogScreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w == 2560:
        skin = """
        <screen name="crashlogview" position="center,center" size="2560,1440" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="32,1326" size="250,69" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="35,1393" size="250,6" zPosition="12" />
        <widget name="text" position="0,10" size="2560,1092" font="Console; 42" text="text" />
        <widget name="text2" position="-279,1123" size="2560,190" font="Console; 42" text="text2" foregroundColor="#ff0000" />
        <eLabel position="10,1110" size="2560,4" backgroundColor="#555555" zPosition="1" />
        </screen>
        """

    elif sz_w == 1920:
        skin = """
        <screen name="crashlogview" position="center,center" size="1880,980" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="16,919" size="250,45" zPosition="11" font="Regular; 30" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="20,963" size="250,6" zPosition="12" />
        <widget name="text" position="10,10" size="1860,695" font="Console; 24" text="text" />
        <widget name="text2" position="10,720" size="1860,190" font="Console; 26" text="text2" foregroundColor="#ff0000" />
        <eLabel position="10,710" size="1860,2" backgroundColor="#555555" zPosition="1" />
        </screen>
        """
    else:
        skin = """
        <screen name="crashlogview" position="center,center" size="1253,653" title="View Crashlog file">
        <widget source="Redkey" render="Label" position="19,609" size="172,33" zPosition="11" font="Regular; 22" valign="center" halign="center" backgroundColor="#050c101b" transparent="1" foregroundColor="white" />
        <eLabel backgroundColor="#00ff0000" position="20,643" size="172,6" zPosition="12" />
        <widget name="text" position="6,6" size="1240,463" font="Console; 16" text="text" />
        <widget name="text2" position="6,480" size="1240,126" font="Console; 17" text="text2" foregroundColor="#ff0000" />
        <eLabel position="6,473" size="1240,1" backgroundColor="#555555" zPosition="1" />
        </screen>
        """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        global Crashfile
        self.setTitle('View Crashlog file:  ' + str(Crashfile))
        self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
                                      {
                                      "cancel": self.exit,
                                      "back": self.exit,
                                      "red": self.exit,
                                      })
        self["Redkey"] = StaticText(_("Close"))
        self["Greenkey"] = StaticText(_("Restart GUI"))
        self["text"] = ScrollLabel("")
        self["text2"] = ScrollLabel("")
        self.list = []
        self["menu"] = List(self.list)
        self.listcrah()

    def exit(self):
        self.close()

    def listcrah(self):
        global Crashfile
        list = "No data error"
        list2 = "No data error"
        try:
            crashfiles = open(Crashfile, "r")
            for line in crashfiles:
                if line.find("Traceback (most recent call last):") != -1 or line.find("Backtrace:") != -1:
                    list = " "
                    list2 = " "
                    for line in crashfiles:
                        list += line
                        if line.find("Error: ") != -1:
                            list2 += line
                        if line.find("]]>") != -1 or line.find("dmesg") != -1 or line.find("StackTrace") != -1 or line.find("FATAL SIGNAL") != -1:
                            if line.find("FATAL SIGNAL") != -1:
                                list2 = "FATAL SIGNAL"
                            break
            self["text"].setText(list)
            crashfiles.close()
        except Exception as e:
            print('error to open crashfile: ', e)
        self["text2"].setText(list2)
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], {"cancel": self.close, "up": self["text"].pageUp, "left": self["text"].pageUp, "down": self["text"].pageDown, "right": self["text"].pageDown}, -1)
