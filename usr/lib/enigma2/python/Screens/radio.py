#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin RadioM is developed
from Lululla to Mmark
"""
from __future__ import print_function
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import (MultiContentEntryPixmapAlphaTest, MultiContentEntryText)
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import InfoBarBase
from Components.config import config
from Screens.InfoBarGenerics import (
    InfoBarMenu,
    InfoBarSeek,
    InfoBarNotifications,
    InfoBarShowHide,
)
from Screens.Screen import Screen
try:
    from Tools.Directories import SCOPE_GUISKIN as SCOPE_SKIN
except ImportError:
    from Tools.Directories import SCOPE_SKIN
from Tools.Directories import resolveFilename
from requests.adapters import HTTPAdapter
from enigma import (
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
    eServiceReference,
    ePicLoad,
    getDesktop,
    eTimer,
    loadPNG,
    eListboxPythonMultiContent,
    gFont,
)
import os
import sys
import six
import requests
from datetime import datetime as dt
version = '1.1'
HD = getDesktop(0).size()
iconpic = 'plugin.png'
screenWidth = getDesktop(0).size().width()
PY3 = sys.version_info.major >= 3
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
path_png = os.path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin))) + "/radio/"
if PY3:
    unicode = str
    from urllib.request import urlopen
    from urllib.request import Request
else:
    from urllib2 import urlopen
    from urllib2 import Request


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
           'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
           'Accept-Encoding': 'gzip, deflate'}


def ReadUrl2(url, referer):
    try:
        import ssl
        CONTEXT = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    except:
        CONTEXT = None

    TIMEOUT_URL = 30
    print('ReadUrl1:\n  url = %s' % url)
    try:
        req = Request(url)
        req.add_header('User-Agent', RequestAgent())
        req.add_header('Referer', referer)
        try:
            r = urlopen(req, None, TIMEOUT_URL, context=CONTEXT)
        except Exception as e:
            r = urlopen(req, None, TIMEOUT_URL)
            print('CreateLog Codifica ReadUrl: %s.' % str(e))
        link = r.read()
        r.close()
        dec = 'Null'
        dcod = 0
        tlink = link
        if str(type(link)).find('bytes') != -1:
            try:
                tlink = link.decode('utf-8')
                dec = 'utf-8'
            except Exception as e:
                dcod = 1
                print('ReadUrl2 - Error: ', str(e))
            if dcod == 1:
                dcod = 0
                try:
                    tlink = link.decode('cp437')
                    dec = 'cp437'
                except Exception as e:
                    dcod = 1
                    print('ReadUrl3 - Error:', str(e))
            if dcod == 1:
                dcod = 0
                try:
                    tlink = link.decode('iso-8859-1')
                    dec = 'iso-8859-1'
                except Exception as e:
                    dcod = 1
                    print('CreateLog Codific ReadUrl: ', str(e))
            link = tlink
        elif str(type(link)).find('str') != -1:
            dec = 'str'
        print('CreateLog Codifica ReadUrl: %s.' % dec)
    except Exception as e:
        print('ReadUrl5 - Error: ', str(e))
        link = None
    return link


def geturl(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        return response.content
    except Exception as e:
        print(str(e))
        return ''


class radioList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screenWidth >= 1920:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont('Regular', 38))
        else:
            self.l.setItemHeight(40)
            self.l.setFont(0, gFont('Regular', 34))


def RListEntry(download):
    res = [(download)]
    col = 0xffffff
    colsel = 0xf07655
    pngx = os.path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin))) + "/skin_default/icons/folder.png"
    if screenWidth >= 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 10), size=(30, 30), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(600, 50), font=0, text=download, color=col, color_sel=colsel, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryText(pos=(0, 0), size=(400, 40), font=0, text=download, color=col, color_sel=colsel, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(data, list):
    icount = 0
    plist = []
    for line in data:
        name = data[icount]
        plist.append(RListEntry(name))
        icount += 1
    list.setList(plist)


def resizePoster(x, y, dwn_poster):
    try:
        from PIL import Image
        img = Image.open(dwn_poster)
        # width, height = img.size
        # ratio = float(width) / float(height)
        # new_height = int(isz.split(",")[1])
        # new_width = int(ratio * new_height)
        new_width = x
        new_height = y
        try:
            rimg = img.resize((new_width, new_height), Image.LANCZOS)
        except:
            rimg = img.resize((new_width, new_height), Image.ANTIALIAS)
        img.close()
        rimg.save(dwn_poster)
        rimg.close()
    except Exception as e:
        print("ERROR:{}".format(e))


def titlesong2(url):
    try:
        # Header HTTP
        hdr = {"User-Agent": "Enigma2 - RadioM Plugin"}
        # Configura HTTPAdapter
        adapter = HTTPAdapter()
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        # Effettua la richiesta
        r = http.get(url, headers=hdr, timeout=10, verify=False, stream=True)
        r.raise_for_status()
        # Controlla lo stato della risposta
        if r.status_code == requests.codes.ok:
            # Ritorna i dati JSON
            return r.json()
    except Exception as e:
        # Ritorna un errore in caso di problemi
        return {"error": str(e)}


def titlesong(url):
    try:
        # Header HTTP
        hdr = {"User-Agent": "Enigma2 - RadioM Plugin"}
        # Configura HTTPAdapter
        adapter = HTTPAdapter()
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)

        # Effettua la richiesta
        r = http.get(url, headers=hdr, timeout=10, verify=False, stream=True)
        r.raise_for_status()

        # Controlla lo stato della risposta
        if r.status_code == requests.codes.ok:
            data = r.json()

            # Variabili di default
            title = ''
            start = ''
            ends = ''
            duration = 0
            artist = ''

            # Estrai il titolo
            if "title" in data:
                title = data["title"].replace('()', '')

            # Estrai e converti i timestamp
            if "started_at" in data:
                start = data["started_at"].strip(' ')[0:19]
                start_time = dt.strptime(start, "%Y-%m-%d %H:%M:%S")

            if "ends_at" in data:
                ends = data["ends_at"].strip(' ')[0:19]
                end_time = dt.strptime(ends, "%Y-%m-%d %H:%M:%S")

                # Calcola la differenza
                delta = end_time - start_time
                duration = delta.total_seconds()

            # Estrai l'artista
            if "artist" in data:
                try:
                    artist = data["artist"]["name"]
                except KeyError:
                    artist = ", ".join(data.get("top_artists", []))

            # Costruisci il risultato
            comeback = (
                'Artist: ' + str(artist) + '\n' +
                'Title: ' + str(title) + '\n' +
                'Start: ' + str(start) + '\n' +
                'End: ' + str(ends) + '\n' +
                'Duration sec.: ' + str(duration)
            )

            return {"comeback": comeback, "artist": artist, "title": title, "start": start, "ends": ends, "duration": duration}

    except Exception as e:
        # In caso di errore, ritorna un dizionario con il messaggio di errore
        return {"error": str(e)}


class radiom1(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label('HOME RADIO VIEW')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self.currentList = 'list'
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        sc = AVSwitch().getFramebufferScale()
        self.picload = PicLoader()
        global x, y
        pic = path_png + "ft.jpg"
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 400
            y = 400
        if screenWidth == 2560:
            x = 850
            y = 850
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)
        self['setupActions'] = ActionMap(['HotkeyActions',
                                          'OkCancelActions',
                                          'TimerEditActions',
                                          'DirectionActions'], {
            'red': self.close,
            'green': self.okClicked,
            'cancel': self.close,
            'up': self.up,
            'down': self.down,
            'left': self.left,
            'right': self.right,
            'ok': self.okClicked
        },        -2)
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        self.names = []
        self.urls = []
        self.pics = []
        self.names.append('PLAYLIST')
        self.urls.append('http://75.119.158.76:8090/radio.mp3')
        self.pics.append(path_png + "ft.jpg")
        self.names.append('RADIO 80')
        self.urls.append('http://laut.fm/fm-api/stations/soloanni80')
        self.pics.append(path_png + "80s.png")
        self.names.append('80ER')
        self.urls.append('http://laut.fm/fm-api/stations/80er')
        self.pics.append(path_png + "80er.png")
        self.names.append('SCHLAGER-RADIO')
        self.urls.append('http://laut.fm/fm-api/stations/schlager-radio')
        self.pics.append(path_png + "shclager.png")
        self.names.append('1000OLDIES')
        self.urls.append('http://laut.fm/fm-api/stations/1000oldies')
        self.pics.append(path_png + "/1000oldies.png")
        self.names.append('RADIO CYRUS')
        self.urls.append('http://75.119.158.76:8090/radio.mp3')
        self.pics.append(path_png + "ft.jpg")
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        name = self.names[idx]
        url = self.urls[idx]
        pic = self.pics[idx]
        if 'PLAYLIST' in name:
            self.session.open(radiom2)
        elif 'RADIO CYRUS' in name:
            self.session.open(Playstream2, name, url)
        else:
            self.session.open(radiom80, name, url, pic)

    def selectpic(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        pic = self.pics[idx]
        sc = AVSwitch().getFramebufferScale()
        self.picload = PicLoader()
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr.__deref__())
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage:", err)

    def up(self):
        self[self.currentList].up()
        self.selectpic()

    def down(self):
        self[self.currentList].down()
        self.selectpic()

    def left(self):
        self[self.currentList].pageUp()
        self.selectpic()

    def right(self):
        self[self.currentList].pageDown()
        self.selectpic()

    def cancel(self):
        Screen.close(self, False)


class radiom2(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label()
        self['info'].setText('UserList')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self["back"].hide()
        sc = AVSwitch().getFramebufferScale()
        self.picload = PicLoader()
        global x, y
        pic = path_png + "ft.jpg"
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 400
            y = 400
        if screenWidth == 2560:
            x = 850
            y = 850
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)
        self['setupActions'] = ActionMap(['SetupActions',
                                          'ColorActions',
                                          'TimerEditActions'], {
            'red': self.close,
            'green': self.okClicked,
            'cancel': self.cancel,
            'ok': self.okClicked,
        },        -2)
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        # uLists = path_png
        self.names = []
        for root, dirs, files in os.walk(path_png):
            for name in files:
                if '.txt' in name:
                    # continue
                    self.names.append(name)
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        name = self.names[idx]
        self.session.open(radiom3, name)

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr.__deref__())
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage:", err)

    def cancel(self):
        Screen.close(self, False)


class radiom3(Screen):
    def __init__(self, session, name):
        Screen.__init__(self, session)
        self.name = name
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label()
        self['info'].setText(name)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self["back"].hide()
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.is_playing = False
        sc = AVSwitch().getFramebufferScale()
        self.picload = PicLoader()
        global x, y
        pic = path_png + "ft.jpg"
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 400
            y = 400
        if screenWidth == 2560:
            x = 850
            y = 850
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(pic)

        self['setupActions'] = ActionMap(['SetupActions',
                                          'ColorActions',
                                          'TimerEditActions'], {
            'red': self.close,
            'green': self.okClicked,
            'cancel': self.cancel,
            'ok': self.okClicked,
        },        -2)
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        # uLists = THISPLUG + '/Playlists'
        file1 = path_png + str(self.name)
        print('Here in showContentA2 file1 = ', file1)
        self.names = []
        self.urls = []
        f1 = open(file1, 'r')
        for line in f1.readlines():
            if '##' not in line:
                continue
            line = line.replace('\n', '')
            items = line.split('###')
            name = items[0]
            url = items[1]
            self.names.append(name)
            self.urls.append(url)
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        name = self.names[idx]
        url = self.urls[idx]
        if self.is_playing:
            self.stop()
            return

        url = url.replace(':', '%3a').replace(' ', '%20')
        tv = False
        if tv is False:
            ref = '4097:0:1:0:0:0:0:0:0:0:' + str(url)  # tv
        else:
            ref = '4097:0:2:0:0:0:0:0:0:0:' + str(url)  # radio
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)
        self.is_playing = True

    def stop(self, text=''):
        if self.is_playing:
            try:
                self.is_playing = False
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                return
            except TypeError as e:
                print(e)
                self.close()

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr.__deref__())
                self["logo"].instance.show()
        except Exception as err:
            self["logo"].instance.hide()
            print("ERROR showImage:", err)

    def cancel(self):
        self.stop()
        Screen.close(self, False)


class radiom80(Screen):
    def __init__(self, session, name, url, pic):
        Screen.__init__(self, session)
        self.session = session
        self.name = name
        self.url = url
        self.pic = pic
        self.list = []
        self['list'] = radioList([])
        self['info'] = Label()
        self['info'].setText(name)
        self['current_song'] = Label()
        self['listeners'] = Label()
        self['format'] = Label()
        self['description'] = Label()
        self['djs'] = Label()
        self["logo"] = Pixmap()
        self["back"] = Pixmap()
        self["back"].hide()
        self.player = '1'
        sc = AVSwitch().getFramebufferScale()
        self.picload = PicLoader()
        global x, y
        pic = pic.replace("\n", "").replace("\r", "")
        x = 430
        y = 430
        if screenWidth == 1920:
            x = 340
            y = 340
        if screenWidth == 2560:
            x = 850
            y = 850
        resizePoster(x, y, pic)
        self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "#00000000"))
        self.picload.addCallback(self.showback)
        self.picload.startDecode(self.pic)
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.is_playing = False
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['key_red'] = Button(_('Exit'))
        self['key_blue'] = Label('Player 1-2-3')
        self['key_green'] = Button(_('Select'))
        self['key_green'].hide()
        self['actions'] = ActionMap(['OkActions',
                                     'SetupActions',
                                     'ColorActions',
                                     'EPGSelectActions',
                                     'InfoActions',
                                     'CancelActions'], {
            'red': self.cancel,
            'back': self.cancel,
            'blue': self.typeplayer,
            'green': self.openPlay,
            'info': self.countdown,
            'cancel': self.cancel,
            'ok': self.openPlay,
        },        -2)
        self.onShow.append(self.openTest)

    def typeplayer(self):
        if self.player == '2':
            self["key_blue"].setText("Player 3-2-1")
            self.player = '3'
        elif self.player == '1':
            self["key_blue"].setText("Player 2-3-1")
            self.player = '2'
        else:
            self["key_blue"].setText("Player 1-2-3")
            self.player = '1'
        return

    def showback(self, picInfo=None):
        try:
            ptr = self.picload.getData()
            if ptr is not None:
                self["logo"].instance.setPixmap(ptr.__deref__())
                self["logo"].instance.show()
        except Exception as err:
            print("ERROR showback:", err)

    def selectpic(self):
        if self.okcoverdown == 'success':
            pic = '/tmp/artist.jpg'
            x = self["logo"].instance.size().width()
            y = self["logo"].instance.size().height()
            pic = pic.replace("\n", "").replace("\r", "")
            resizePoster(x, y, pic)
            sc = AVSwitch().getFramebufferScale()
            self.picload = PicLoader()
            self.picload.setPara((x, y, sc[0], sc[1], 0, 1, "FF000000"))
            self.picload.addCallback(self.showback)
            self.picload.startDecode(pic)
        return

    '''
    # http://radio.garden/api/ara/content/places
    # "results": [
        # {
            # "wrapperType": "track",
            # "kind": "music-video",
            # "artistId": 909253,
            # "collectionId": 1445738051,
            # "trackId": 1445738215,
            # "artistName": "Jack Johnson",
            # "collectionName": "To the Sea",
            # "trackName": "You And Your Heart",
            # "collectionCensoredName": "To the Sea",
            # "trackCensoredName": "You And Your Heart (Closed-Captioned)",
            # "artistViewUrl": "https://music.apple.com/us/artist/jack-johnson/909253?uo=4",
            # "collectionViewUrl": "https://music.apple.com/us/music-video/you-and-your-heart-closed-captioned/1445738215?uo=4",
            # "trackViewUrl": "https://music.apple.com/us/music-video/you-and-your-heart-closed-captioned/1445738215?uo=4",
            # "previewUrl": "https://video-ssl.itunes.apple.com/itunes-assets/Video115/v4/f0/92/0c/f0920ce2-8bb7-5e62-b44c-36ce701fe7b1/mzvf_6922739671336234286.640x352.h264lc.U.p.m4v",
            # "artworkUrl30": "https://is1-ssl.mzstatic.com/image/thumb/Video/41/81/14/mzi.wdsoqdmh.jpg/30x30bb.jpg",
            # "artworkUrl60": "https://is1-ssl.mzstatic.com/image/thumb/Video/41/81/14/mzi.wdsoqdmh.jpg/60x60bb.jpg",
            # "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/Video/41/81/14/mzi.wdsoqdmh.jpg/100x100bb.jpg",
            # "collectionPrice": 11.99,
            # "trackPrice": -1.0,
            # "releaseDate": "2010-06-01T07:00:00Z",
            # "collectionExplicitness": "notExplicit",
            # "trackExplicitness": "notExplicit",
            # "discCount": 1,
            # "discNumber": 1,
            # "trackCount": 15,
            # "trackNumber": 14,
            # "trackTimeMillis": 197288,
            # "country": "USA",
            # "currency": "USD",
            # "primaryGenreName": "Rock"
        # },'''

    def downloadCover(self, title):
        try:
            self.okcoverdown = 'failed'
            print('^^^DOWNLOAD COVER^^^')
            itunes_url = 'http://itunes.apple.com/search?term=%s&limit=1&media=music' % six.moves.urllib.parse.quote_plus(title)
            res = requests.get(itunes_url, timeout=5)
            data = res.json()
            if six.PY3:
                url = data['results'][0]['artworkUrl100']
            else:
                url = data['results'][0]['artworkUrl100'].encode('utf-8')
            url = url.replace('https', 'http')
            print('url is: ', url)
            if self.getCover(url):
                self.okcoverdown = 'success'
                print('success artist url')
            else:
                self.okcoverdown = 'failed'
        except:
            self.okcoverdown = 'failed'
        print('self.okcoverdown = ', self.okcoverdown)
        return

    def getCover(self, url):
        try:
            data = geturl(url)
            if data:
                with open('/tmp/artist.jpg', 'wb') as f:
                    f.write(data)
                return True
            return False
        except:
            return False

    def openTest(self):
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.loadPlaylist)
        except:
            self.timer.callback.append(self.loadPlaylist)
        self.timer.start(250, True)

    def loadPlaylist(self):
        self.names = []
        self.urls = []
        a = 0
        display_name = ''
        page_url = ''
        stream_url = ''
        current_song = ''
        listeners = ''
        format = ''
        description = ''
        djs = ''
        if a == 0:
            data = titlesong2(self.url)
            if "error" in data:
                print("Errore:", data["error"])
            else:
                print("Dati della canzone:", data)

            for cat in data:
                print('cat: ', cat)
                display_name = ''
                page_url = ''
                stream_url = ''
                current_song = ''
                listeners = ''
                format = ''
                description = ''
                djs = ''
                # Estrazione dei dati
                if "stream_url" in cat:
                    if "display_name" in cat:
                        display_name = str(cat["display_name"])
                        print('display_name = ', display_name)

                    if "page_url" in cat:
                        page_url = str(cat["page_url"])
                        print('page_url = ', page_url)

                    if "stream_url" in cat:
                        stream_url = str(cat["stream_url"])
                        print('stream_url = ', stream_url)

                    if "current_song" in cat["api_urls"]:
                        urla = cat["api_urls"]["current_song"]
                        self.backing = str(urla)
                        print('url song = ', urla)

                        current_song_data = titlesong2(urla)
                        if "error" in current_song_data:
                            print('Errore nel recuperare la canzone:', current_song_data["error"])
                            current_song = _("Error retrieving song")
                        else:
                            current_song = current_song_data.get("title", _("Unknown Title"))
                            print('current_song = ', current_song)

                    if "listeners" in cat["api_urls"]:
                        urlb = str(cat["api_urls"]["listeners"])
                        self.listen = urlb
                        listeners = self.listener(urlb)
                        print('listeners = ', listeners)

                    if "format" in cat:
                        format = str(cat["format"])
                        print('format = ', format)

                    if "description" in cat:
                        description = str(cat["description"])
                        print('description = ', description)

                    if "djs" in cat:
                        djs = str(cat["djs"])
                        print('djs = ', djs)

                    self['current_song'].setText(str(current_song))
                    self['listeners'].setText(_('Online: ') + str(listeners))
                    self['format'].setText(_(format))
                    self['description'].setText(_(description))
                    self['djs'].setText(_('Dj: ') + str(djs))

                    self.names.append(display_name)
                    self.urls.append(stream_url)
                self.countdown()
                print('current_song = ', current_song)
                self['info'].setText(_('Select and Play'))
                self['key_green'].show()
                showlist(self.names, self['list'])

    def listener(self, urlx):
        content = ' '
        try:
            referer = 'https://laut.fm'
            content = ReadUrl2(urlx, referer)
        except Exception as e:
            print('err:', e)
        return content

    def cancel(self):
        self.stop()
        self.close()

    def countdown(self):
        try:
            live = self.listener(self.listen)
            titlex_data = titlesong(self.backing)
            if "error" in titlex_data:
                print("Errore nel recupero della canzone:", titlex_data["error"])
                titlex = "Canzone non disponibile"
                self.artist = "Artista sconosciuto"
            else:
                titlex = titlex_data.get("comeback", "Canzone non disponibile")
                self.artist = titlex_data.get("artist", "Artista sconosciuto")
            self.downloadCover(self.artist)
            self['current_song'].setText(titlex)
            self['listeners'].setText(_('Online: ') + str(live))
            self.selectpic()
            self.openTest2()
            print('Countdown finished.')
        except Exception as e:
            print('Errore durante il countdown:', e)

    def openTest2(self):
        print('duration mmm: ', self.duration)
        print(type(self.duration))
        if self.duration >= 0.0:
            value_str = str(self.duration)
            conv = value_str.split('.')[0]
            print('conv mmm: ', conv)
            current = int(float(conv)) * 60
            print('current mmm: ', current)
            self.timer = eTimer()
            try:
                self.timer_conn = self.timer.timeout.connect(self.countdown)
            except:
                self.timer.callback.append(self.countdown)
            self.timer.start(current, False)

    def showback2(self, picInfo=None):
        try:
            self["back"].instance.show()
        except Exception as err:
            self["back"].instance.hide()
            print("ERROR showback:", err)
        return

    def openPlay(self):
        idx = self['list'].getSelectionIndex()
        if idx is None:
            return
        self.showback2()
        name = self.names[idx]
        url = self.urls[idx]
        if self.is_playing:
            self.stop()
            return
        try:
            if self.player == '2':
                self.session.open(Playstream2, name, url)
            else:
                url = url.replace(':', '%3a').replace(' ', '%20')
                if self.player == '3':
                    ref = '4097:0:1:0:0:0:0:0:0:0:' + str(url)  # TV
                else:
                    ref = '4097:0:2:0:0:0:0:0:0:0:' + str(url)  # Radio
                print('Final reference:', ref)
                sref = eServiceReference(ref)
                sref.setName(name)
                self.session.nav.stopService()
                self.session.nav.playService(sref)
                self.is_playing = True
                self.countdown()
        except Exception as e:
            print("Errore durante la riproduzione:", e)

    def stop(self, text=''):
        if self.is_playing:
            self.timer.stop()
            try:
                self["back"].instance.hide()
                self.is_playing = False
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                return
            except TypeError as e:
                print(e)
                self.close()

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: '4:3 Letterbox',
                1: '4:3 PanScan',
                2: '16:9',
                3: '16:9 always',
                4: '16:10 Letterbox',
                5: '16:10 PanScan',
                6: '16:9 Letterbox'}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
               1: '4_3_panscan',
               2: '16_9',
               3: '16_9_always',
               4: '16_10_letterbox',
               5: '16_10_panscan',
               6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass


class Playstream2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
    STATE_PLAYING = 1
    STATE_PAUSED = 2

    def __init__(self, session, name, url):
        global SREF
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        self.sref = None
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['WizardActions',
                                     'MoviePlayerActions',
                                     'EPGSelectActions',
                                     'MediaPlayerSeekActions',
                                     'ColorActions',
                                     'InfobarShowHideActions',
                                     'InfobarSeekActions',
                                     'InfobarActions'], {'leavePlayer': self.stop,
                                                         'back': self.stop,
                                                         'playpauseService': self.playpauseService,
                                                         'down': self.av
                                                         }, -1)
        self.allowPiP = False
        self.is_playing = False
        InfoBarSeek.__init__(self, actionmap='MediaPlayerSeekActions')
        self.icount = 0
        self.name = name
        self.url = url
        self.state = self.STATE_PLAYING
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openPlay)
        return

    def __onStop(self):
        self.stop()

    def openPlay(self):
        if self.is_playing:
            self.stop()
        try:
            url = self.url.replace(':', '%3a').replace(' ', '%20')
            # ref = '4097:0:1:0:0:0:0:0:0:0:' + str(url)  # tv
            ref = '4097:0:2:0:0:0:0:0:0:0:' + str(url)  # radio
            print('final reference:   ', ref)
            sref = eServiceReference(ref)
            sref.setName(self.name)
            self.session.nav.stopService()
            self.session.nav.playService(sref)
            self.is_playing = True
        except:
            pass

    def stop(self, text=''):
        if self.is_playing:
            try:
                self.is_playing = False
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                if not self.new_aspect == self.init_aspect:
                    try:
                        self.setAspect(self.init_aspect)
                    except:
                        pass

                self.exit()
            except TypeError as e:
                print(e)
                self.exit()

    def exit(self):
        self.close()

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
                1: _('4:3 PanScan'),
                2: _('16:9'),
                3: _('16:9 always'),
                4: _('16:10 Letterbox'),
                5: _('16:10 PanScan'),
                6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
               1: '4_3_panscan',
               2: '16_9',
               3: '16_9_always',
               4: '16_10_letterbox',
               5: '16_10_panscan',
               6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def playpauseService(self):
        if self.state == self.STATE_PLAYING:
            self.pause()
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.unpause()
            self.state = self.STATE_PLAYING

    def pause(self):
        self.session.nav.pause(True)

    def unpause(self):
        self.session.nav.pause(False)

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)


ListAgent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8',
    'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.16) Gecko/20120427 Firefox/15.0a1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1',
]


def RequestAgent():
    from random import choice
    RandomAgent = choice(ListAgent)
    return RandomAgent


class PicLoader:
    def __init__(self):
        self.picload = ePicLoad()
        self.picload_conn = None

    def setSize(self, width, height, sc=None):
        if sc is None:
            sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((width, height, sc[0], sc[1], False, 1, "#ff000000"))

    def load(self, filename):
        if os.path.exists('/var/lib/dpkg/status'):
            self.picload.startDecode(filename, False)
        else:
            self.picload.startDecode(filename, 0, 0, False)
        data = self.picload.getData()
        return data

    def destroy(self):
        self.picload = None
        self.picload_conn = None

    def addCallback(self, callback):
        if os.path.exists('/var/lib/dpkg/status'):
            self.picload_conn = self.picload.PictureData.connect(callback)
        else:
            self.picload.PictureData.get().append(callback)

    def getData(self):
        return self.picload.getData()

    def setPara(self, *args):
        self.picload.setPara(*args)

    def startDecode(self, f):
        self.picload.startDecode(f)
