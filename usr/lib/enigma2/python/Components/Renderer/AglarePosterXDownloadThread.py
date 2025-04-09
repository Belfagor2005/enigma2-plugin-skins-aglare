#!/usr/bin/python
# -*- coding: utf-8 -*-

# edit by lululla 07.2022
# recode from lululla 2023
from __future__ import absolute_import
from Components.config import config
from PIL import Image
from enigma import getDesktop
import os
import re
import requests
import socket
import sys
import threading
import unicodedata
import random
import json
from random import choice
from requests import RequestException
from twisted.internet.reactor import callInThread
from .Converlibr import quoteEventName
from requests.adapters import HTTPAdapter, Retry


try:
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 0
except ImportError:
    from httplib import HTTPConnection
    HTTPConnection.debuglevel = 0


global my_cur_skin, srch

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    import html
    html_parser = html
else:
    from HTMLParser import HTMLParser
    html = HTMLParser()


try:
    from urllib.error import URLError, HTTPError
    from urllib.request import urlopen
except:
    from urllib2 import URLError, HTTPError
    from urllib2 import urlopen


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass


def getRandomUserAgent():
    useragents = [
        'Mozilla/5.0 (compatible; Konqueror/4.5; FreeBSD) KHTML/4.5.4 (like Gecko)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20120101 Firefox/35.0',
        'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]
    return random.choice(useragents)


tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
# thetvdbkey = 'D19315B88B2DE21F'
thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"
fanart_api = "6d231536dea4318a88cb2520ce89473b"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')


try:
    if my_cur_skin is False:
        skin_paths = {
            "tmdb_api": "/usr/share/enigma2/{}/tmdbkey".format(cur_skin),
            "omdb_api": "/usr/share/enigma2/{}/omdbkey".format(cur_skin),
            "thetvdbkey": "/usr/share/enigma2/{}/thetvdbkey".format(cur_skin)
        }
        for key, path in skin_paths.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    value = f.read().strip()
                    if key == "tmdb_api":
                        tmdb_api = value
                    elif key == "omdb_api":
                        omdb_api = value
                    elif key == "thetvdbkey":
                        thetvdbkey = value
                my_cur_skin = True
except Exception as e:
    print("Errore nel caricamento delle API:", str(e))
    my_cur_skin = False


isz = "185,278"
bisz = "300,450"
screenwidth = getDesktop(0).size()
if screenwidth.width() <= 1280:
    isz = isz.replace(isz, "185,278")
    bisz = bisz.replace(bisz, "300,450")
elif screenwidth.width() <= 1920:
    isz = isz.replace(isz, "342,514")
    bisz = bisz.replace(bisz, "780,1170")
else:
    isz = isz.replace(isz, "780,1170")
    bisz = bisz.replace(bisz, "1280,1920")


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
    if os.path.exists(mount) and isMountedInRW(mount):
        path_folder = os.path.join(mount, "poster")
        break

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


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


class AglarePosterXDownloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.adsl = intCheck()  # Assicurati che intCheck() sia definita altrove
        if not self.adsl:
            print("Connessione assente, modalità offline.")
            return
        else:
            print("Connessione rilevata.")

        self.checkMovie = ["film", "movie", "фильм", "кино", "ταινία", "película", "cinéma", "cine", "cinema", "filma"]
        self.checkTV = ["serial", "series", "serie", "serien", "série", "séries", "serious", "folge", "episodio", "episode", "épisode", "l'épisode", "ep.", "animation", "staffel", "soap", "doku", "tv", "talk", "show", "news", "factual", "entertainment", "telenovela", "dokumentation", "dokutainment", "documentary", "informercial", "information", "sitcom", "reality", "program", "magazine", "mittagsmagazin", "т/с", "м/с", "сезон", "с-н", "эпизод", "сериал", "серия", "actualité", "discussion", "interview", "débat", "émission", "divertissement", "jeu", "magasine", "information", "météo", "journal", "sport", "culture", "infos", "feuilleton", "téléréalité", "société", "clips", "concert", "santé", "éducation", "variété"]
        self.pstrNm = None  # Inizializzato come None

    def search_tmdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            print('self.dwn_poster=', self.dwn_poster)
            title_safe = title
            self.title_safe = title_safe.replace('+', ' ')
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&language={lng}&query={self.title_safe}"
            print('poster search_tmdb url title safe', url)
            data = None
            retries = Retry(total=1, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retries)
            http = requests.Session()
            http.mount("http://", adapter)
            http.mount("https://", adapter)
            headers = {'User-Agent': getRandomUserAgent()}
            response = http.get(url, headers=headers, timeout=(10, 20), verify=False)
            response.raise_for_status()
            if response.status_code == requests.codes.ok:
                try:
                    data = response.json()
                except ValueError as e:
                    print(e)
                    data = None
                self.downloadData2(data)
                return True, "Download avviato con successo"
            else:
                return False, f"Errore durante la ricerca su TMDb: {response.status_code}"
        except Exception as e:
            print('Errore nella ricerca TMDb:', e)
            return False, "Errore durante la ricerca su TMDb"

    def downloadData2(self, data):
        if isinstance(data, bytes):
            print("Decoding bytes to string...")
            data = data.decode('utf-8')
        data_json = data if isinstance(data, dict) else json.loads(data)
        if 'results' in data_json:
            try:
                for each in data_json['results']:
                    media_type = str(each['media_type']) if each.get('media_type') else ''
                    if media_type == "tv":
                        media_type = "serie"
                    if media_type in ['serie', 'movie']:
                        year = ""
                        if media_type == "movie" and 'release_date' in each and each['release_date']:
                            year = each['release_date'].split("-")[0]
                        elif media_type == "serie" and 'first_air_date' in each and each['first_air_date']:
                            year = each['first_air_date'].split("-")[0]
                        title = each.get('name', each.get('title', ''))
                        backdrop = "http://image.tmdb.org/t/p/w1280" + (each.get('backdrop_path') or '')
                        poster = "http://image.tmdb.org/t/p/w500" + (each.get('poster_path') or '')
                        rating = str(each.get('vote_average', 0))
                        show_title = title
                        if year:
                            show_title = "{} ({})".format(title, year)
                        # Check if poster and backdrop are valid before trying to save
                        if poster:
                            callInThread(self.savePoster, poster, self.dwn_poster)
                            print('callinThread=Poster')
                            return True, "[SUCCESS poster: tmdb] title {} [poster{}-backdrop{}] => year{} => rating{} => showtitle{}".format(title, poster, backdrop, year, rating, show_title)
                    return False, "[SKIP : tmdb] Not found"
            except Exception as e:
                print('error=', e)
                if os.path.exists(self.dwn_poster):
                    os.remove(self.dwn_poster)
                return False, "[ERROR : tmdb]"

    def search_tvdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            series_nb = -1
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = title
            self.title_safe = title_safe.replace('+', ' ')  # Replace '+' with space in title

            # Extract year from the description if present
            year = re.findall(r'19\d{2}|20\d{2}', fd)
            year = year[0] if year else ''

            # Query TVDB API for series information
            url_tvdbg = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(self.title_safe)
            url_read = requests.get(url_tvdbg).text
            series_id = re.findall(r'<seriesid>(.*?)</seriesid>', url_read)
            series_name = re.findall(r'<SeriesName>(.*?)</SeriesName>', url_read)
            series_year = re.findall(r'<FirstAired>(19\d{2}|20\d{2})-\d{2}-\d{2}</FirstAired>', url_read)

            # Determine the correct series based on year
            for i, iseries_year in enumerate(series_year):
                if year == '':
                    series_nb = 0
                    break
                elif year == iseries_year:
                    series_nb = i
                    break

            poster = None
            if series_nb >= 0 and series_id and series_id[series_nb]:
                # Sanitize the series name if found
                series_name = self.UNAC(series_name[series_nb]) if series_name else ''

                # Check if the title matches the series name
                if self.PMATCH(self.title_safe, series_name):
                    url_tvdb = "https://thetvdb.com/api/{}/series/{}".format(thetvdbkey, series_id[series_nb])
                    url_tvdb += f"/{lng}" if lng else "/en"
                    url_read = requests.get(url_tvdb).text

                    poster = re.findall(r'<poster>(.*?)</poster>', url_read)
                    if poster:
                        url_poster = "https://artworks.thetvdb.com/banners/{}".format(poster[0])
                        # Call method to save the poster asynchronously
                        callInThread(self.savePoster, url_poster, self.dwn_poster)
                        return True, "[SUCCESS : tvdb] {} [{}-{}] => {} => {} => {}".format(self.title_safe, chkType, year, url_tvdbg, url_tvdb, url_poster)
            else:
                return False, "[SKIP : tvdb] {} [{}-{}] => {} (Not found)".format(self.title_safe, chkType, year, url_tvdbg)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : tvdb] {} => {} ({})".format(title, url_tvdbg, str(e))

    def search_fanart(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            year = None
            url_maze = ""
            url_fanart = ""
            id = "-"
            title_safe = title
            self.title_safe = title_safe.replace('+', ' ')  # Replace '+' with space in title

            # Extract year from description if present
            chkType, fd = self.checkType(shortdesc, fulldesc)
            try:
                year = re.findall(r'19\d{2}|20\d{2}', fd)[1] if len(re.findall(r'19\d{2}|20\d{2}', fd)) > 1 else ''
            except IndexError:
                year = ''

            # Get TVMaze ID for the show
            try:
                url_maze = "http://api.tvmaze.com/singlesearch/shows?q={}".format(self.title_safe)
                mj = requests.get(url_maze).json()
                id = mj['externals']['thetvdb']
            except Exception as err:
                print('Error retrieving TVMaze info:', err)

            # Fetch Fanart poster information
            try:
                url_fanart = "https://webservice.fanart.tv/v3/{}/{}?api_key={}".format('tv', id, fanart_api)
                fjs = requests.get(url_fanart, verify=False, timeout=5).json()
                url = fjs['tvposter'][0]['url'] if fjs.get('tvposter') else fjs['movieposter'][0]['url']

                # Fetch and save the poster
                if url:
                    callInThread(self.savePoster, url, self.dwn_poster)
                    return True, "[SUCCESS poster: fanart] {} [{}-{}] => {} => {} => {}".format(self.title_safe, chkType, year, url_maze, url_fanart, url)
                return False, "[SKIP : fanart] {} [{}-{}] => {} (Not found)".format(self.title_safe, chkType, year, url_fanart)
            except Exception as e:
                print(e)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : fanart] {} [{}-{}] => {} ({})".format(self.title_safe, chkType, year, url_fanart, str(e))

    def search_imdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            idx_imdb = None
            len_imdb = 0
            self.dwn_poster = dwn_poster
            url_poster = None
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = title
            self.title_safe = title_safe.replace('+', ' ')  # Replace '+' with space

            aka = re.findall(r'\((.*?)\)', fd)
            aka = aka[1] if len(aka) > 1 and not aka[1].isdigit() else aka[0] if len(aka) > 0 and not aka[0].isdigit() else None

            paka = self.UNAC(aka) if aka else ''
            year = re.findall(r'19\d{2}|20\d{2}', fd)
            year = year[0] if year else ''

            url_mimdb = ""
            url_imdb = ""

            # Search in IMDb based on title and aka
            if aka and aka != self.title_safe:
                url_mimdb = "https://m.imdb.com/find?q={}%20({})".format(self.title_safe, quoteEventName(aka))
            else:
                url_mimdb = "https://m.imdb.com/find?q={}".format(self.title_safe)

            url_read = requests.get(url_mimdb).text
            rc = re.compile(r'<img src="(.*?)".*?<span class="h3">\n(.*?)\n</span>.*?\((\d+)\)(\s\(.*?\))?(.*?)</a>', re.DOTALL)
            url_imdb = rc.findall(url_read)

            # Retry with simpler search if no results
            if len(url_imdb) == 0 and aka:
                url_mimdb = "https://m.imdb.com/find?q={}".format(self.title_safe)
                url_read = requests.get(url_mimdb).text
                url_imdb = rc.findall(url_read)

            pfound = False
            for imdb in url_imdb:
                imdb = list(imdb)
                imdb[1] = self.UNAC(imdb[1])
                tmp = re.findall(r'aka <i>"(.*?)"</i>', imdb[4])
                imdb[4] = tmp[0] if tmp else ''
                imdb[4] = self.UNAC(imdb[4])

                imdb_poster = re.search(r"(.*?)._V1_.*?.jpg", imdb[0])
                if imdb_poster and imdb[3] == '':
                    if year and year == imdb[2]:
                        url_poster = "{}._V1_UY278,1,185,278_AL_.jpg".format(imdb_poster.group(1))
                        imsg = f"Found title : '{imdb[1]}', aka : '{imdb[4]}', year : '{imdb[2]}'"
                        if self.PMATCH(self.title_safe, imdb[1]) or self.PMATCH(self.title_safe, imdb[4]) or (paka and self.PMATCH(paka, imdb[1])) or (paka and self.PMATCH(paka, imdb[4])):
                            pfound = True
                            break
                    elif not url_poster and (int(year) - 1 == int(imdb[2]) or int(year) + 1 == int(imdb[2])):
                        url_poster = "{}._V1_UY278,1,185,278_AL_.jpg".format(imdb_poster.group(1))
                        imsg = f"Found title : '{imdb[1]}', aka : '{imdb[4]}', year : '+/-{imdb[2]}'"
                        if self.title_safe == imdb[1] or self.title_safe == imdb[4] or (paka and paka == imdb[1]) or (paka and paka == imdb[4]):
                            pfound = True
                            break
                idx_imdb += 1

            if url_poster and pfound:
                callInThread(self.savePoster, url_poster, dwn_poster)
                if os.path.exists(dwn_poster):
                    return True, "[SUCCESS url_poster: imdb] {} [{}-{}] => {} [{}/{}] => {} => {}".format(self.title_safe, chkType, year, imsg, idx_imdb, len_imdb, url_mimdb, url_poster)
            return False, "[SKIP : imdb] {} [{}-{}] => {} (No Entry found [{}])".format(self.title_safe, chkType, year, url_mimdb, len_imdb)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : imdb] {} [{}-{}] => {} ({})".format(self.title_safe, chkType, year, url_mimdb, str(e))

    def search_programmetv_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            chkType, fd = self.checkType(shortdesc, fulldesc)

            if chkType.startswith("movie"):
                return False, "[SKIP : programmetv-google] {} [{}] => Skip movie title".format(title, chkType)

            title_safe = title
            self.title_safe = title_safe.replace('+', ' ')  # Replace '+' with space

            url_ptv = "site:programme-tv.net+" + self.title_safe
            if channel and self.title_safe.find(channel.split()[0]) < 0:
                url_ptv += "+" + quoteEventName(channel)

            url_ptv = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(url_ptv)
            ff = requests.get(url_ptv, stream=True, headers=headers, cookies={'CONSENT': 'YES+'}).text

            ptv_id = 0
            plst = re.findall(r'\],\["https://www.programme-tv.net(.*?)",\d+,\d+]', ff)
            for posterlst in plst:
                ptv_id += 1
                url_poster = "https://www.programme-tv.net{}".format(posterlst)
                url_poster = re.sub(r"\\u003d", "=", url_poster)
                url_poster_size = re.findall(r'([\d]+)x([\d]+).*?([\w\.-]+).jpg', url_poster)

                if url_poster_size and url_poster_size[0]:
                    get_title = self.UNAC(url_poster_size[0][2].replace('-', ''))
                    if self.title_safe == get_title:
                        h_ori = float(url_poster_size[0][1])
                        h_tar = float(re.findall(r'(\d+)', isz)[1])
                        ratio = h_ori / h_tar
                        w_ori = float(url_poster_size[0][0])
                        w_tar = w_ori / ratio
                        w_tar = int(w_tar)
                        h_tar = int(h_tar)
                        url_poster = re.sub(r'/\d+x\d+/', "/" + str(w_tar) + "x" + str(h_tar) + "/", url_poster)
                        url_poster = re.sub(r'crop-from/top/', '', url_poster)
                        callInThread(self.savePoster, url_poster, self.dwn_poster)
                        return True, "[SUCCESS url_poster: programmetv-google] {} [{}] => Found self.title_safe : '{}' => {} => {} (initial size: {}) [{}]".format(self.title_safe, chkType, get_title, url_ptv, url_poster, url_poster_size, ptv_id)

            return False, "[SKIP : programmetv-google] {} [{}] => Not found [{}] => {}".format(self.title_safe, chkType, ptv_id, url_ptv)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : programmetv-google] {} [{}] => {} ({})".format(self.title_safe, chkType, url_ptv, str(e))

    def search_molotov_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = title.replace('+', ' ')
            poster = None
            url_mgoo = "site:molotov.tv+" + title_safe
            if channel and title_safe.find(channel.split()[0]) < 0:
                url_mgoo += "+" + quoteEventName(channel)
            url_mgoo = "https://www.google.com/search?q={}&tbm=isch".format(url_mgoo)

            ff = requests.get(url_mgoo, stream=True, headers=headers, cookies={'CONSENT': 'YES+'}).text
            plst = re.findall(r'https://www.molotov.tv/(.*?)"(?:.*?)?"(.*?)"', ff)
            molotov_table = [0, 0, None, None, 0]
            partialtitle = 0
            partialchannel = 0
            for pl in plst:
                get_path = "https://www.molotov.tv/" + pl[0]
                get_name = self.UNAC(pl[1])
                get_title = re.findall(r'(.*?)[ ]+en[ ]+streaming', get_name)
                get_channel = self.extract_channel(get_name)

                partialchannel = self.PMATCH(channel, get_channel)
                partialtitle = self.PMATCH(title_safe, get_title)

                if partialtitle > molotov_table[0]:
                    molotov_table = [partialtitle, partialchannel, get_name, get_path, len(plst)]
                if partialtitle == 100 and partialchannel == 100:
                    break

            if molotov_table[0]:
                poster = self.download_poster(molotov_table, headers)

            if poster:
                return True, "[SUCCESS poster: molotov-google] {} => {}".format(title_safe, poster)
            return False, "[SKIP : molotov-google] {} (No poster found)".format(title_safe)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : molotov-google] {} ({})".format(title_safe, str(e))

    def search_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            self.dwn_poster = dwn_poster
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            chkType, fd = self.checkType(shortdesc, fulldesc)
            title_safe = title.replace('+', ' ')
            poster = None
            year = re.findall(r'19\d{2}|20\d{2}', fd)
            year = year[0] if year else None
            url_google = '"{}"'.format(title_safe)

            if channel and title_safe.find(channel) < 0:
                url_google += "+{}".format(quoteEventName(channel))
            if year:
                url_google += "+{}".format(year)

            url_google = "https://www.google.com/search?q={}&tbm=isch&tbs=sbd:0".format(url_google)
            ff = requests.get(url_google, stream=True, headers=headers, cookies={'CONSENT': 'YES+'}).text

            posterlst = re.findall(r'\],\["https://(.*?)",\d+,\d+]', ff)
            if len(posterlst) == 0:
                url_google = "https://www.google.com/search?q={}&tbm=isch&tbs=ift:jpg%2Cisz:m".format(title_safe)
                ff = requests.get(url_google, stream=True, headers=headers).text
                posterlst = re.findall(r'\],\["https://(.*?)",\d+,\d+]', ff)

            for pl in posterlst:
                url_poster = "https://{}".format(pl)
                url_poster = re.sub(r"\\u003d", " = ", url_poster)
                self.savePoster(url_poster, dwn_poster)
                if os.path.exists(dwn_poster):
                    poster = url_poster
                    break

            if poster:
                return True, "[SUCCESS poster: google] {} => {}".format(title_safe, poster)
            return False, "[SKIP : google] {} (No poster found)".format(title_safe)

        except Exception as e:
            if os.path.exists(dwn_poster):
                os.remove(dwn_poster)
            return False, "[ERROR : google] {} ({})".format(title_safe, str(e))

    def extract_channel(self, name):
        channel = re.findall(r'(?:streaming|replay)?[ ]+sur[ ]+(.*?)[ ]+molotov.tv', name)
        if not channel:
            channel = re.findall(r'regarder[ ]+(.*?)[ ]+en', name)
        return self.UNAC(channel[0]).replace(' ', '') if channel else None

    def download_poster(self, molotov_table, headers):
        poster_url = "https://www.molotov.tv/" + molotov_table[3]
        ffm = requests.get(poster_url, stream=True, headers=headers).text
        pltt = re.findall(r'"https://fusion.molotov.tv/(.*?)/jpg" alt="(.*?)"', ffm)
        if pltt:
            return "https://fusion.molotov.tv/" + pltt[0][0] + "/jpg"
        return None

    def savePoster(self, url, callback):
        AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
            "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edge/87.0.664.75",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363"
        ]
        headers = {"User-Agent": choice(AGENTS)}
        try:
            response = requests.get(url.encode(), headers=headers, timeout=(3.05, 6))
            response.raise_for_status()
            with open(callback, "wb") as local_file:
                local_file.write(response.content)
        except RequestException as error:
            print(f"ERROR in module 'download': {str(error)}")
        return callback

    def resizePoster(self, dwn_poster):
        try:
            print('resizePoster poster==============')
            img = Image.open(dwn_poster)
            width, height = img.size
            ratio = float(width) / float(height)  # Use floating point division
            new_height = int(isz.split(",")[1])  # Assuming 'isz' is correctly defined elsewhere
            new_width = int(ratio * new_height)
            try:
                rimg = img.resize((new_width, new_height), Image.LANCZOS)
            except Exception:
                rimg = img.resize((new_width, new_height), Image.ANTIALIAS)
            img.close()
            rimg.save(dwn_poster)
            rimg.close()
        except Exception as e:
            print(f"ERROR resizing poster: {e}")

    def verifyPoster(self, dwn_poster):
        try:
            img = Image.open(dwn_poster)
            img.verify()
            if img.format != "JPEG":
                os.remove(dwn_poster)
                return False
        except Exception as e:
            print(f"ERROR verifying poster: {e}")
            os.remove(dwn_poster)
            return False
        return True

    def checkType(self, shortdesc, fulldesc):
        if shortdesc and shortdesc != '':
            fd = shortdesc.splitlines()[0]
        elif fulldesc and fulldesc != '':
            fd = fulldesc.splitlines()[0]
        else:
            fd = ''
        global srch
        srch = "multi"
        return srch, fd

    def UNAC(self, string):
        string = html.unescape(string)
        string = unicodedata.normalize('NFD', string)
        string = re.sub(r"u0026", "&", string)
        string = re.sub(r"u003d", "=", string)
        string = re.sub(r'[\u0300-\u036f]', '', string)
        string = re.sub(r"[,!?\.\"]", ' ', string)
        string = re.sub(r'\s+', ' ', string)
        string = string.strip()
        return string

    def PMATCH(self, textA, textB):
        if not textB or textB == '' or not textA or textA == '':
            return 0
        if textA == textB:
            return 100
        if textA.replace(" ", "") == textB.replace(" ", ""):
            return 100
        if len(textA) > len(textB):
            lId = len(textA.replace(" ", ""))
        else:
            lId = len(textB.replace(" ", ""))
        textA = textA.split()
        cId = 0
        for id in textA:
            if id in textB:
                cId += len(id)
        cId = 100 * cId // lId
        return cId
