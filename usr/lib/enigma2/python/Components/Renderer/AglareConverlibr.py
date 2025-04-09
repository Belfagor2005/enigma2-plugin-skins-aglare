#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
"""
#########################################################
#                                                       #
#  AGP - Advanced Graphics PosteRenderer                #
#  Version: 3.5.0                                       #
#  Created by Lululla (https://github.com/Belfagor2005) #
#  License: CC BY-NC-SA 4.0                             #
#  https://creativecommons.org/licenses/by-nc-sa/4.0    #
#                                                       #
#  Last Modified: "15:14 - 20250401" )                  #
#                                                       #
#  Credits:                                             #
#  - Original concept by Lululla                        #
#  - TMDB API integration                               #
#  - TVDB API integration                               #
#  - OMDB API integration                               #
#  - Advanced caching system                            #
#                                                       #
#  Usage of this code without proper attribution        #
#  is strictly prohibited.                              #
#  For modifications and redistribution,                #
#  please maintain this credit header.                  #
#########################################################
"""
__author__ = "Lululla"
__copyright__ = "AGP Team"
from datetime import datetime
from re import compile, sub, I, escape, DOTALL
import sys
from functools import lru_cache
from six import text_type

date_modify = datetime.now().strftime("%d/%m/%Y")

# System Configuration
PY3 = sys.version_info[0] >= 3  # Python version check
DEBUG = False  # Debug flag

"""
Advanced Title Normalization Module - Fixed Version
"""

# 1 Replacement mappings - optimized for TV series
REPLACEMENTS = (
	# Format fixes
	('1/2', 'mezzo'),
	('c.s.i.', 'csi'),
	('c.s.i:', 'csi'),
	('n.c.i.s.', 'ncis'),
	('chicago med', 'chicagomed'),

	# Common patterns
	(' - prima tv', ''),
	(' - primatv', ''),
	('primatv', ''),
	('18+', ''),
	('16+', ''),
	('12+', ''),
	('ore 14', ''),

	# Special cases
	('colombo', 'columbo'),
	('il ritorno di colombo', 'colombo'),
	('superman & lois', 'superman e lois'),
	('lois & clark', 'superman e lois'),
	('1/2', 'mezzo'),
	('ritorno al futuro:', 'ritorno al futuro'),
	('lois & clark', 'superman e lois'),
	('john q', 'johnq'),
	('the flash', 'theflash'),
	('station 19', 'station19')

)


# 2 Title-specific fixes
TITLE_FIXES = {
	'john q': 'johnq',
	'il ritorno di colombo': 'colombo',
	'e.r.': 'er medici in prima linea',
	'avanti un altro': 'avanti un altro',
	'tg1': 'tg1 edition',
	'grande fratello': 'grande fratello',
	'amici di maria': 'amici di maria',
	'josephine angelo custode': 'josephine guardian angel',
	'josephine angie gardien': 'josephine guardian angel',
	'lingo: parole': 'lingo',
	'heartland': 'heartland',
	'io & marilyn': 'io e marilyn',
	'giochi olimpici parigi': 'olimpiadi di parigi',
	'anni 60': 'anni 60',
	'cortesie per gli ospiti': 'cortesieospiti',
	'tg regione': 'tg3',
	'planet earth': 'planet earth',
	'josephine ange gardien': 'josephine ange gardien',
	'elementary': 'elementary',
	'squadra speciale cobra 11': 'squadra speciale cobra 11',
	'criminal minds': 'criminal minds',
	'i delitti del barlume': 'i delitti del barlume',
	'senza traccia': 'senza traccia',
	'hudson e rex': 'hudson e rex',
	'ben-hur': 'ben-hur',
	'csi miami': 'csi miami',
	'csi: miami': 'csi miami',
	'csi: scena del crimine': 'csi scena del crimine',
	'csi scena del crimine': 'csi scena del crimine',
	'csi: new york': 'csi new york',
	'csi new york': 'csi new york',
	'csi: vegas': 'csi vegas',
	'csi vegas': 'csi vegas',
	'csi: cyber': 'csi cyber',
	'csi cyber': 'csi cyber',
	'csi: immortality': 'csi immortality',
	'csi immortality': 'csi immortality',
	'csi: crime scene talks': 'csi crime scene talks',
	'ncis unità anticrimine': 'ncis unità anticrimine',
	'ncis new orleans': 'ncis new orleans',
	'ncis los angeles': 'ncis los angeles',
	'ncis origins': 'ncis origins',
	'ncis hawai': 'ncis hawai',
	'ncis sydney': 'ncis sydney',
	'walker, texas ranger': 'walker texas ranger',
	'alexa: vita da detective': 'alexa vita da detective',
	'delitti in paradiso': 'delitti in paradiso',
	'modern family': 'modern family',
	'shaun: vita da pecora': 'shaun',
	'calimero': 'calimero',
	'i puffi': 'i puffi',
	'stuart little': 'stuart little',
	'gf daily': 'grande fratello',
	'castle': 'castle',
	'seal team': 'seal team',
	'fast forward': 'fast forward',
	'un posto al sole': 'un posto al sole',
	'station19': 'station 19',
	'theflash': 'the flash',
	'colombo': 'columbo',
	'chicagomed': 'chicago med',
	'theequalizer': 'the equalizer',
	# 'che tempo che fa': 'che tempo che fa',
	'miss marple': 'miss marple',

}


REGEX = compile(
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
	DOTALL)


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


# Precompiled regex patterns
TECH_TERMS = compile(r'\b(1080p|4k|720p|hdtv|webrip|bluray)\b', I)
EPISODE = compile(
	r'([ ._-]*('
	r'ep|episodio|st|stagione|season|saison|staffel|capitolo|parte|pt|serie|episod|'
	r's\d{1,2}e\d{1,2}|\d{1,2}x\d{1,2}|'
	r'season\s?\d{1,2}[ _-]*episode\s?\d{1,2}|'
	r'saison\s?\d{1,2}[ _-]*episode\s?\d{1,2}|'
	r'staffel\s?\d{1,2}[ _-]*folge\s?\d{1,2}|'
	r'ep\.?\s?\d+|s\d{1,2}\s?e\d{1,2}|'
	r's\d{1,2}\s?episode\s?\d{1,2}|'
	r'episodio\s?\d{1,2}|serie\s?\d{1,2}[ _-]*episodio\s?\d{1,2}|'
	r'season\s?[\d]+[\s]*ep\.?\s?[\d]+|'
	r'episódio\s?\d+|episodio\s?\d+|'
	r'epizoda\s?\d+|sezione\s?\d+|'
	r'episodios?\s?\d+'
	r')[ ._-]*\d+)', I
)

BRACKETS = compile(r'\(.*?\)|\[.*?\]')

PRE_COMPILED_REPLACEMENTS = [
	(compile(r'\b{}\b'.format(escape(old))), new)  # Parentesi chiuse correttamente
	for old, new in REPLACEMENTS
]


"""
# @lru_cache(maxsize=1000)
# def clean_for_tvdb_cached(title):
	# return clean_for_tvdb(title)
"""


@lru_cache(maxsize=1000)  # Memorizza fino a xxx titoli unici
def convtext(title):
	if not title:
		return title

	try:
		text = title.lower().strip()

		# title = title.split('-')[0]

		# Applica sostituzioni con regex precompilate
		"""
		for pattern, replacement in PRE_COMPILED_REPLACEMENTS:
			text = pattern.sub(replacement, text)
		"""
		if text.endswith("the"):
			text = "the " + text[:-4]

		text = remove_accents(text)

		# title = title.split('-')[0]  # .split(':')[0].strip()

		# # Apply direct replacements
		for old, new in REPLACEMENTS:
			text = text.replace(old, new)

		# Check for full title overrides
		for pattern, fix in TITLE_FIXES.items():
			if pattern in text:
				text = fix
				break

		# Remove technical terms
		text = TECH_TERMS.sub('', text)

		# Remove episode/season markers
		text = EPISODE.sub('', text)
		# text = _EPISODE_INFO.sub('', text)

		# Remove content in brackets
		text = BRACKETS.sub('', text)

		# remove episode number in arabic series
		text = sub(r' +ح', '', text)
		# remove season number in arabic series
		text = sub(r' +ج', '', text)
		# remove season number in arabic series
		text = sub(r' +م', '', text)

		# Final cleanup
		text = sub(r'[._\']', ' ', text)
		text = sub(r'\s+', ' ', text).strip()

		# aggiunto da me
		# text = remove_accents(text)
		# text = REGEX.findall(text)

		# title = title.split('-')[0]  # .split(':')[0].strip()

		return text.lower() if text.strip() else title

	except Exception as e:
		if DEBUG:
			print(f'clean_title error: {str(e)}')
		return None
