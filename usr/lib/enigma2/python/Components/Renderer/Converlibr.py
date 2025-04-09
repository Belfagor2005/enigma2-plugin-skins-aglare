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
from re import compile, I, escape
import sys
from functools import lru_cache

date_modify = datetime.now().strftime("%d/%m/%Y")

# System Configuration
PY3 = sys.version_info[0] >= 3
DEBUG = False  # Debug flag - set to True for troubleshooting


class TitleNormalizer:
	"""
	Advanced Title Normalization with comprehensive patterns and error handling
	"""
	def __init__(self):
		# Define replacement patterns
		self.REPLACEMENTS = (
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
			('station 19', 'station19'),
		)

		# Title-specific fixes
		self.TITLE_FIXES = {
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
		}

		# Precompile all regex patterns
		self._compile_patterns()

	def _compile_patterns(self):
		"""Compile all regex patterns for better performance"""
		self.TECH_TERMS = compile(r'\b(1080p|4k|720p|hdtv|webrip|bluray)\b', I)
		self.EPISODE = compile(r'[sS]\d{1,2}[eE]\d{1,2}|\d{1,2}x\d{1,2}', I)
		self._EPISODE_INFO = compile(
			r'([ ._-]*(ep|episodio|st|stag|odc|parte|pt|series?|s\d{1,2}e\d{1,2}|\d{1,2}x\d{1,2})[ ._-]*\d+)',
			I
		)
		self.BRACKETS = compile(r'\(.*?\)|\[.*?\]')
		self.ARABIC_EPISODE = compile(r' +ح')
		self.ARABIC_SEASON = compile(r' +ج')
		self.ARABIC_SEASON_ALT = compile(r' +م')
		self.SPECIAL_CHARS = compile(r'[._\']')
		self.MULTI_SPACES = compile(r'\s+')

		# Precompile replacements
		self.PRE_COMPILED_REPLACEMENTS = [
			(compile(r'\b{}\b'.format(escape(old)), I), new)
			for old, new in self.REPLACEMENTS
		]

	@lru_cache(maxsize=1000)  # Cache up to 1000 unique titles
	def normalize(self, title):
		"""
		Normalize and clean a title with comprehensive processing
		Returns cleaned title or None if invalid input
		"""
		if not title or not isinstance(title, (str, bytes)):
			if DEBUG:
				print(f"Invalid title input: {title}")
			return None

		try:
			text = str(title).lower().strip()
			if not text:
				return None

			# Apply precompiled replacements
			for pattern, replacement in self.PRE_COMPILED_REPLACEMENTS:
				text = pattern.sub(replacement, text)

			# Handle 'the' at end
			if text.endswith("the"):
				text = "the " + text[:-4]

			# Apply direct title fixes
			for pattern, fix in self.TITLE_FIXES.items():
				if pattern in text:
					text = fix
					break

			# Remove technical terms and formatting
			text = self.TECH_TERMS.sub('', text)
			text = self.EPISODE.sub('', text)
			text = self._EPISODE_INFO.sub('', text)
			text = self.BRACKETS.sub('', text)

			# Clean Arabic numbering
			text = self.ARABIC_EPISODE.sub('', text)
			text = self.ARABIC_SEASON.sub('', text)
			text = self.ARABIC_SEASON_ALT.sub('', text)

			# Final cleanup
			text = self.SPECIAL_CHARS.sub(' ', text)
			text = self.MULTI_SPACES.sub(' ', text).strip()

			return text.capitalize() if text else None

		except Exception as e:
			if DEBUG:
				print(f'Title normalization error: {str(e)}')
			return None


# Create a global instance for easy access
title_normalizer = TitleNormalizer()


def Converlibr(title):
	"""Public interface for title normalization"""
	return title_normalizer.normalize(title)
