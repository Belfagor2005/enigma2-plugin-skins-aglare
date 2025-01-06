#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from re import search, sub, I, S, escape
from six import text_type
import sys

PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    import html
    html_parser = html
    from urllib.parse import quote_plus
else:
    from urllib import quote_plus
    from HTMLParser import HTMLParser
    html_parser = HTMLParser()


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


REGEX = re.compile(
    r'[\(\[].*?[\)\]]|'                    # Parentesi tonde o quadre
    r':?\s?odc\.\d+|'                      # odc. con o senza numero prima
    r'\d+\s?:?\s?odc\.\d+|'                # numero con odc.
    r'[:!]|'                               # due punti o punto esclamativo
    r'\s-\s.*|'                            # trattino con testo successivo
    r',|'                                  # virgola
    r'/.*|'                                # tutto dopo uno slash
    r'\|\s?\d+\+|'                         # | seguito da numero e +
    r'\d+\+|'                              # numero seguito da +
    r'\s\*\d{4}\Z|'                        # * seguito da un anno a 4 cifre
    r'[\(\[\|].*?[\)\]\|]|'                # Parentesi tonde, quadre o pipe
    r'(?:\"[\.|\,]?\s.*|\"|'               # Testo tra virgolette
    r'\.\s.+)|'                            # Punto seguito da testo
    r'Премьера\.\s|'                       # Specifico per il russo
    r'[хмтдХМТД]/[фс]\s|'                  # Pattern per il russo con /ф o /с
    r'\s[сС](?:езон|ерия|-н|-я)\s.*|'      # Stagione o episodio in russo
    r'\s\d{1,3}\s[чсЧС]\.?\s.*|'           # numero di parte/episodio in russo
    r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'         # numero di parte/episodio in russo con punto
    r'\s[чсЧС]\.?\s\d{1,3}.*|'             # Parte/Episodio in russo
    r'\d{1,3}-(?:я|й)\s?с-н.*',            # Finale con numero e suffisso russo
    re.DOTALL)


def remove_accents(string):
    if not isinstance(string, text_type):
        string = text_type(string, 'utf-8')
    string = sub(u"[àáâãäå]", 'a', string)
    string = sub(u"[èéêë]", 'e', string)
    string = sub(u"[ìíîï]", 'i', string)
    string = sub(u"[òóôõö]", 'o', string)
    string = sub(u"[ùúûü]", 'u', string)
    string = sub(u"[ýÿ]", 'y', string)
    return string


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, text_type):
        s = text_type(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def str_encode(text, encoding="utf8"):
    if not PY3:
        if isinstance(text, text_type):
            return text.encode(encoding)
    return text


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '')  # .replace('.', '').replace(' | ', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        eventName = eventName.replace('المسلسل العربي', '')
        eventName = eventName.replace('مسلسل', '')
        eventName = eventName.replace('برنامج', '')
        eventName = eventName.replace('فيلم وثائقى', '')
        eventName = eventName.replace('حفل', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = re.sub('\\(\d+\)$', '', eventitle)
    # save_name = re.sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def sanitize_filename(filename):
    # Replace spaces with underscores and remove invalid characters (like ':')
    sanitized = sub(r'[^\w\s-]', '', filename)  # Remove invalid characters
    # sanitized = sanitized.replace(' ', '_')      # Replace spaces with underscores
    # sanitized = sanitized.replace('-', '_')      # Replace dashes with underscores
    return sanitized.strip()


def convtext(text=''):
    try:
        if text is None:
            print('return None original text:', type(text))
            return  # Esci dalla funzione se text è None
        if text == '':
            print('text is an empty string')
        else:
            # print('original text:', text)
            # Converti tutto in minuscolo
            text = text.lower()
            # print('lowercased text:', text)
            # Rimuovi accenti
            text = remove_accents(text)
            # print('remove_accents text:', text)

            text = text.lstrip()

            # Applica le funzioni di taglio e pulizia del titolo
            text = cutName(text)
            text = getCleanTitle(text)

            # Regola il titolo se finisce con "the"
            if text.endswith("the"):
                text = "the " + text[:-4]

            # Modifiche personalizzate
            if 'giochi olimpici parigi' in text:
                text = 'olimpiadi di parigi'
            if 'bruno barbieri' in text:
                text = text.replace('bruno barbieri', 'brunobarbierix')
            if "anni '60" in text:
                text = "anni 60"
            if 'tg regione' in text:
                text = 'tg3'
            if 'studio aperto' in text:
                text = 'studio aperto'
            if 'josephine ange gardien' in text:
                text = 'josephine ange gardien'
            if 'elementary' in text:
                text = 'elementary'
            if 'squadra speciale cobra 11' in text:
                text = 'squadra speciale cobra 11'
            if 'criminal minds' in text:
                text = 'criminal minds'
            if 'i delitti del barlume' in text:
                text = 'i delitti del barlume'
            if 'senza traccia' in text:
                text = 'senza traccia'
            if 'hudson e rex' in text:
                text = 'hudson e rex'
            if 'ben-hur' in text:
                text = 'ben-hur'
            if 'alessandro borghese - 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'
            if 'alessandro borghese: 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'
            if 'amici di maria' in text:
                text = 'amicidimariadefilippi'

            text = text.replace('1/2', 'mezzo')

            # Sostituisci caratteri speciali con stringhe vuote
            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')
            text = text.replace('1^ visione rai', '').replace('1^ visione', '').replace('primatv', '').replace('1^tv', '')
            text = text.replace('prima visione', '').replace('1^ tv', '').replace('((', '(').replace('))', ')')
            text = text.replace('live:', '').replace(' - prima tv', '')

            # # Gestione casi specifici
            # replacements = {
                # 'giochi olimpici parigi': 'olimpiadi di parigi',
                # 'bruno barbieri': 'brunobarbierix',
                # "anni '60": 'anni 60',
                # 'tg regione': 'tg3',
                # 'studio aperto': 'studio aperto',
                # 'josephine ange gardien': 'josephine ange gardien',
                # 'elementary': 'elementary',
                # 'squadra speciale cobra 11': 'squadra speciale cobra 11',
                # 'criminal minds': 'criminal minds',
                # 'i delitti del barlume': 'i delitti del barlume',
                # 'senza traccia': 'senza traccia',
                # 'hudson e rex': 'hudson e rex',
                # 'ben-hur': 'ben-hur',
                # 'la7': 'la7',
                # 'skytg24': 'skytg24'
            # }
            # for key, value in replacements.items():
                # if key in text:
                    # text = text.replace(key, value)
            # Rimozione pattern specifici
            text = re.sub(r'^\w{2}:', '', text)  # Rimuove "xx:" all'inizio
            text = re.sub(r'^\w{2}\|\w{2}\s', '', text)  # Rimuove "xx|xx" all'inizio
            text = re.sub(r'^.{2}\+? ?- ?', '', text)  # Rimuove "xx -" all'inizio
            text = re.sub(r'^\|\|.*?\|\|', '', text)  # Rimuove contenuti tra "||"
            text = re.sub(r'^\|.*?\|', '', text)  # Rimuove contenuti tra "|"
            text = re.sub(r'\|.*?\|', '', text)  # Rimuove qualsiasi altro contenuto tra "|"
            text = re.sub(r'\(\(.*?\)\)|\(.*?\)', '', text)  # Rimuove contenuti tra "()"
            text = re.sub(r'\[\[.*?\]\]|\[.*?\]', '', text)  # Rimuove contenuti tra "[]"
            text = re.sub(r'\sح\s*\d+', '', text)   # remove episode number in arabic series
            text = re.sub(r'\sج\s*\d+', '', text)   # remove season number in arabic series
            text = re.sub(r'\sم\s*\d+', '', text)   # remove season number in arabic series
            text = re.sub(r'\d+$', '', text)   # remove number in arabic series
            # Rimozione di stringhe non valide
            bad_strings = [
                "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
                "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
                "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
                "uk|", "us|", "yu|",
                "1080p", "4k", "720p", "hdrip", "hindi", "imdb", "vod", "x264"
            ]

            bad_strings.extend(map(str, range(1900, 2030)))  # Anni da 1900 a 2030
            bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
            text = bad_strings_pattern.sub('', text)
            # Rimozione suffissi non validi
            bad_suffix = [
                " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
                " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
            ]
            bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
            text = bad_suffix_pattern.sub('', text)
            # Rimuovi "." "_" "'" e sostituiscili con spazi
            text = re.sub(r'[._\']', ' ', text)
            # Rimuove tutto dopo i ":" (incluso ":")
            text = re.sub(r':.*$', '', text)
            # Pulizia finale
            text = text.partition("(")[0]  # Rimuove contenuti dopo "("
            # text = text.partition(":")[0]
            # text = text + 'FIN'
            # text = sub(r'(odc.\s\d+)+.*?FIN', '', text)
            # text = sub(r'(odc.\d+)+.*?FIN', '', text)
            # text = sub(r'(\d+)+.*?FIN', '', text)
            # text = sub('FIN', '', text)
            # remove episode number in arabic series
            text = sub(r' +ح', '', text)
            # remove season number in arabic series
            text = sub(r' +ج', '', text)
            # remove season number in arabic series
            text = sub(r' +م', '', text)
            text = text.partition(" -")[0]  # Rimuove contenuti dopo "-"
            text = text.strip(' -')
            # Forzature finali
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = text.replace('alessandroborgheseristoranti', 'alessandro borghese - 4 ristoranti')
            text = text.replace('il ritorno di colombo', 'colombo')
            text = text.replace('amicidimariadefilippi', 'amici di maria')
            # text = quote(text, safe="")
            # text = unquote(text)
            print('text safe:', text)

        return text.capitalize()
    except Exception as e:
        print('convtext error:', e)
        return None
