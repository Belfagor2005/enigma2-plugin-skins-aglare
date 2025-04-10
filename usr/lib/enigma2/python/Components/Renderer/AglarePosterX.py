#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng...07.2021,
# 08.2021(stb lang support),
# 09.2021 mini fixes
# edit by lululla 07.2022
# recode from lululla 2023
# © Provided that digiteng rights are protected, all or part of the code can be used, modified...
# russian and py3 support by sunriser...
# downloading in the background while zaping...
# by beber...03.2022,
# 03.2022 several enhancements : several renders with one queue thread, google search (incl. molotov for france) + autosearch & autoclean thread ...
# for infobar,
# <widget source="session.Event_Now" render="AglarePosterX" position="100,100" size="185,278" />
# <widget source="session.Event_Next" render="AglarePosterX" position="100,100" size="100,150" />
# <widget source="session.Event_Now" render="AglarePosterX" position="100,100" size="185,278" nexts="2" />
# <widget source="session.CurrentService" render="AglarePosterX" position="100,100" size="185,278" nexts="3" />

# for ch,
# <widget source="ServiceEvent" render="AglarePosterX" position="100,100" size="185,278" />
# <widget source="ServiceEvent" render="AglarePosterX" position="100,100" size="185,278" nexts="2" />

# for epg, event
# <widget source="Event" render="AglarePosterX" position="100,100" size="185,278" />
# <widget source="Event" render="AglarePosterX" position="100,100" size="185,278" nexts="2" />
# or put tag -->  path="/media/hdd/poster"
from __future__ import print_function, absolute_import

# Standard library
from os import utime, remove, listdir, makedirs
from os.path import exists, join, getmtime, getsize
import socket
from sys import version_info
from time import time, sleep
from traceback import print_exc
from datetime import datetime
from glob import glob
import threading
# from functools import lru_cache
import codecs

# Enigma2 specific
import NavigationInstance
from enigma import (
	ePixmap,
	loadJPG,
	eEPGCache,
	eTimer,
)
from ServiceReference import ServiceReference
from Components.config import config
from Components.Renderer.Renderer import Renderer
from Components.Renderer.AglarePosterXDownloadThread import AglarePosterXDownloadThread
from Components.Sources.CurrentService import CurrentService
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent

# Local imports
# from .Converlibr import convtext
from .AglareConverlibr import convtext


PY3 = version_info[0] >= 3
if not PY3:
	import Queue
	from urllib2 import HTTPError, URLError
	from urllib2 import urlopen
	# from thread import start_new_thread
else:
	import queue
	from urllib.error import HTTPError, URLError
	from urllib.request import urlopen
	# from _thread import start_new_thread


epgcache = eEPGCache.getInstance()
if PY3:
	pdb = queue.LifoQueue()
else:
	pdb = Queue.LifoQueue()


cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
noposter = "/usr/share/enigma2/%s/main/noposter.jpg" % cur_skin


def isMountedInRW(mount_point):
	with open("/proc/mounts", "r") as f:
		for line in f:
			parts = line.split()
			if len(parts) > 1 and parts[1] == mount_point:
				return True
	return False


path_folder = "/tmp/poster"

# Check preferred paths in order
for mount in ["/media/usb", "/media/hdd", "/media/mmc"]:
	if exists(mount) and isMountedInRW(mount):
		path_folder = join(mount, "poster")
		break

if not exists(path_folder):
	makedirs(path_folder)


apdb = dict()


try:
	lng = config.osd.language.value
	lng = lng[:-3]
except:
	lng = 'en'
	pass


def logPoster(*args):
	message = " ".join(str(arg) for arg in args)
	print(message)


def logDB(*args):
	try:
		logmsg = " ".join(str(arg) for arg in args)
		with open("/tmp/PosterDB.log", "a") as w:
			w.write("%s\n" % logmsg)
	except Exception as e:
		logPoster("logDB error:", str(e))
		print_exc()


def logPosterx(*args):
	try:
		logmsg = " ".join(str(arg) for arg in args)
		with open("/tmp/logPosterX.log", "a") as w:
			w.write("%s\n" % logmsg)
	except Exception as e:
		logPoster('logPoster error', str(e))
		print_exc()


def logAutoDB(*args):
	try:
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		logmsg = " ".join(str(arg) for arg in args)
		with open("/tmp/PosterAutoDB.log", "a") as w:
			w.write("[{}] {}\n".format(timestamp, logmsg))
	except Exception as e:
		logPoster("logAutoDB error: {}".format(e))
		print_exc()


def SearchBouquetTerrestrial():
	"""Searches for a bouquet file containing specific terrestrial markers."""
	fallback_file = "/etc/enigma2/userbouquet.favourites.tv"
	for filepath in sorted(glob("/etc/enigma2/*.tv")):
		with codecs.open(filepath, "r", encoding="utf-8") as f:
			content = f.read().strip().lower()
			if "eeee" in content:
				if "82000" not in content and "c0000" not in content:
					return filepath  # Return path, not content
	return fallback_file


autobouquet_file = None


def process_autobouquet():
	"""Processes the selected bouquet file and extracts valid services."""
	global autobouquet_file
	autobouquet_file = SearchBouquetTerrestrial()
	autobouquet_count = 70
	apdb = {}

	if not exists(autobouquet_file):
		logPoster("File not found:", autobouquet_file)
		return {}

	try:
		with open(autobouquet_file, "r", encoding="utf-8") as f:
			lines = f.readlines()
	except (IOError, OSError) as e:
		logPoster("Error reading file:", e)
		return {}

	autobouquet_count = min(autobouquet_count, len(lines))

	for i, line in enumerate(lines[:autobouquet_count]):
		if line.startswith("#SERVICE"):
			parts = line[9:].strip().split(":")
			if len(parts) == 11 and ":".join(parts[3:7]) != "0:0:0:0":
				apdb[i] = ":".join(parts)

	logPoster("Found", len(apdb), "valid services.")
	return apdb


apdb = process_autobouquet()


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


class PosterDB(AglarePosterXDownloadThread):
	def __init__(self):
		AglarePosterXDownloadThread.__init__(self)
		self.logdbg = None
		self.pstcanal = None

	def run(self):
		logDB("[QUEUE] : Initialized")
		while True:
			canal = pdb.get()
			logDB("[QUEUE] : {} : {}-{} ({})".format(canal[0], canal[1], canal[2], canal[5]))
			self.pstcanal = convtext(canal[5])

			if not self.pstcanal:
				logDB("[ERROR] Poster not found for channel")
				pdb.task_done()
				continue

			dwn_poster = join(path_folder, self.pstcanal + ".jpg")
			if exists(dwn_poster):
				utime(dwn_poster, (time(), time()))
			if not exists(dwn_poster):
				val, log = self.search_tmdb(dwn_poster, self.pstcanal, canal[4], canal[3])
				logDB(log)
			elif not exists(dwn_poster):
				val, log = self.search_tvdb(dwn_poster, self.pstcanal, canal[4], canal[3])
				logDB(log)
			elif not exists(dwn_poster):
				val, log = self.search_fanart(dwn_poster, self.pstcanal, canal[4], canal[3])
				logDB(log)
			elif not exists(dwn_poster):
				val, log = self.search_imdb(dwn_poster, self.pstcanal, canal[4], canal[3])
				logDB(log)
			elif not exists(dwn_poster):
				val, log = self.search_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
				logDB(log)
			pdb.task_done()


class PosterAutoDB(AglarePosterXDownloadThread):
	def __init__(self):
		AglarePosterXDownloadThread.__init__(self)
		self.logdbg = None
		self.pstcanal = None

	def run(self):
		logAutoDB("[AutoDB] *** Initialized ***")

		try:
			while True:
				sleep(7200)  # 7200 - Start every 2 hours
				logAutoDB("[AutoDB] *** Running ***")
				self.pstcanal = None
				for service in apdb.values():
					try:
						events = epgcache.lookupEvent(['IBDCTESX', (service, 0, -1, 1440)])
						newfd = 0
						newcn = None

						for evt in events:
							logAutoDB("[AutoDB] evt {} events ({})".format(evt, len(events)))
							canal = [None] * 6

							if PY3:
								canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
							else:
								canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '').encode('utf-8')
							if evt[1] is None or evt[4] is None or evt[5] is None or evt[6] is None:
								logAutoDB("[AutoDB] *** Missing EPG for {}".format(canal[0]))
							else:
								canal[1:6] = [evt[1], evt[4], evt[5], evt[6], evt[4]]
								self.pstcanal = convtext(canal[5]) if canal[5] else None
								if self.pstcanal is not None:
									dwn_poster = join(path_folder, self.pstcanal + ".jpg")
								else:
									logPoster("None type detected - poster not found")
									continue

								if exists(dwn_poster):
									utime(dwn_poster, (time(), time()))
								if not exists(dwn_poster):
									val, log = self.search_tmdb(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
									if val and log.find("SUCCESS"):
										newfd += 1
								elif not exists(dwn_poster):
									val, log = self.search_tvdb(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
									if val and log.find("SUCCESS"):
										newfd += 1
								elif not exists(dwn_poster):
									val, log = self.search_fanart(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
									if val and log.find("SUCCESS"):
										newfd += 1
								elif not exists(dwn_poster):
									val, log = self.search_imdb(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
									if val and log.find("SUCCESS"):
										newfd += 1
								elif not exists(dwn_poster):
									val, log = self.search_google(dwn_poster, self.pstcanal, canal[4], canal[3], canal[0])
									if val and log.find("SUCCESS"):
										newfd += 1
							newcn = canal[0]
							logAutoDB("[AutoDB] {} new file(s) added ({})".format(newfd, newcn))

					except Exception as e:
						logAutoDB("[AutoDB] *** Service error: {}".format(e))
						print_exc()

				# AUTO REMOVE OLD FILES
				if not exists(path_folder):
					logAutoDB("[AutoDB] path_folder does not exist: {}".format(path_folder))
					continue

				now_tm = time()
				emptyfd = 0
				oldfd = 0
				for f in listdir(path_folder):
					if not f.endswith(".jpg"):
						continue
					file_path = join(path_folder, f)
					try:
						diff_tm = now_tm - getmtime(file_path)
						if diff_tm > 120 and getsize(file_path) == 0:
							remove(file_path)
							emptyfd += 1
						elif diff_tm > 31536000:  # 1 year
							remove(file_path)
							oldfd += 1
					except Exception as e:
						logAutoDB("[ERROR] File removal failed: {} - {}".format(file_path, e))
				logAutoDB("[AutoDB] {} old file(s) removed".format(oldfd))
				logAutoDB("[AutoDB] {} empty file(s) removed".format(emptyfd))
				logAutoDB("[AutoDB] *** Stopping ***")
		except Exception as e:
			logAutoDB("[AutoDB] *** Fatal error: {}".format(e))
			print_exc()


class AglarePosterX(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.adsl = intCheck()
		if not self.adsl:
			logPoster("Connessione assente, modalità offline.")
			return
		else:
			logPoster("Connessione rilevata.")

		self.nxts = 0
		self.path = path_folder
		self.canal = [None] * 6
		self.pstrNm = None
		self.oldCanal = None
		self.logdbg = None
		self.pstcanal = None

		self.timer = eTimer()
		try:
			self.timer_conn = self.timer.timeout.connect(self.showPoster)
		except:
			self.timer.callback.append(self.showPoster)

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value) in self.skinAttributes:
			if attrib == "nexts":
				self.nxts = int(value)
			if attrib == "path":
				self.path = str(value)
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

		servicetype = None
		try:

			service = None
			source_type = type(self.source)
			if source_type is ServiceEvent:
				service = self.source.getCurrentService()
				servicetype = "ServiceEvent"
			elif source_type is CurrentService:
				service = self.source.getCurrentServiceRef()
				servicetype = "CurrentService"
			elif source_type is EventInfo:
				service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				servicetype = "EventInfo"
			elif source_type is Event:
				if self.nxts:
					service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				else:
					self.canal[0] = None
					self.canal[1] = self.source.event.getBeginTime()
					event_name = self.source.event.getEventName().replace('\xc2\x86', '').replace('\xc2\x87', '')
					if not PY3:
						event_name = event_name.encode('utf-8')
					self.canal[2] = event_name
					self.canal[3] = self.source.event.getExtendedDescription()
					self.canal[4] = self.source.event.getShortDescription()
					self.canal[5] = event_name
				servicetype = "Event"

			if service is not None:
				service_str = service.toString()
				events = epgcache.lookupEvent(['IBDCTESX', (service_str, 0, -1, -1)])
				service_name = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
				if not PY3:
					service_name = service_name.encode('utf-8')
				self.canal[0] = service_name
				self.canal[1] = events[self.nxts][1]
				self.canal[2] = events[self.nxts][4]
				self.canal[3] = events[self.nxts][5]
				self.canal[4] = events[self.nxts][6]
				self.canal[5] = self.canal[2]

				if not autobouquet_file and service_name not in apdb:
					apdb[service_name] = service_str

		except Exception as e:
			logPoster("Error (service):", str(e))
			if self.instance:
				self.instance.hide()
			return

		if not servicetype:
			if self.instance:
				self.instance.hide()
			return

		# if self.instance:
			# self.instance.hide()

		try:
			curCanal = "{}-{}".format(self.canal[1], self.canal[2])
			"""
			if curCanal != self.oldCanal:
				self.oldCanal = curCanal
				self.pstcanal = convtext(self.canal[5])
				if self.pstcanal is not None:
					self.pstrNm = join(self.path, str(self.pstcanal) + ".jpg")
					self.pstcanal = self.pstrNm

				if exists(self.pstcanal):
					self.timer.start(5, True)
				else:
					canal = self.canal[:]
					pdb.put(canal)
					self.runPosterThread()
			"""
			if curCanal == self.oldCanal:
				return
			self.oldCanal = curCanal
			self.pstcanal = convtext(self.canal[5])
			if self.pstcanal is not None:
				self.pstrNm = join(self.path, str(self.pstcanal) + ".jpg")
				self.pstcanal = self.pstrNm

			if exists(self.pstcanal):
				self.timer.start(5, True)
			else:
				canal = self.canal[:]
				pdb.put(canal)
				# start_new_thread(self.waitPoster, ())
				self.runPosterThread()

		except Exception as e:
			logPoster("Error (eFile):", str(e))
			if self.instance:
				self.instance.hide()
			return

	def runPosterThread(self):
		threading.Thread(target=self.waitPoster, daemon=True).start()

	def generatePosterPath(self):
		# if self.canal and len(self.canal) > 5 and self.canal[5]:
		if len(self.canal) > 5 and self.canal[5]:
			pstcanal = convtext(self.canal[5])
			return join(self.path, f"{pstcanal}.jpg")
		return None

	def showPoster(self):
		if self.instance:
			self.instance.hide()
		self.pstrNm = self.generatePosterPath()
		if self.pstrNm and exists(self.pstrNm):
			self.instance.setPixmap(loadJPG(self.pstrNm))
			self.instance.setScale(1)
			self.instance.show()

	def waitPoster(self):
		if self.instance:
			self.instance.hide()
		self.pstrNm = self.generatePosterPath()
		if not self.pstrNm:
			logPoster("[ERROR: waitPoster] Poster path is None")
			return

		loop = 60
		found = False
		logPoster("[LOOP: waitPoster] " + self.pstrNm)
		while loop > 0:
			if self.pstrNm is not None and exists(self.pstrNm):
				found = True
				break
			sleep(1)
			loop -= 1

		if found:
			self.timer.start(10, True)


threadDB = PosterDB()
threadDB.start()

threadAutoDB = PosterAutoDB()
threadAutoDB.start()
