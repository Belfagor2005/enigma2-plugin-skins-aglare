#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
#########################################################
#                                                       #
#  AGP - Advanced Graphics PosteRenderer                #
#  Version: 3.5.0                                       #
#  Created by Lululla (https://github.com/Belfagor2005) #
#  License: CC BY-NC-SA 4.0                             #
#  https://creativecommons.org/licenses/by-nc-sa/4.0    #
#                                                       #
#  Last Modified: {date_modify}                         #
#                                                       #
#  Credits:                                             #
#  - Original concept by Lululla                        #
#  - TMDB API integration                               #
#  - TVDB API integration                               #
#  - OMDB API integration                               #
#  - Advanced caching system                            #
#                                                       #
#  Features:                                            #
#  - Displays age rating icons                          #
#  - Supports multiple rating systems                   #
#  - Integrates with AglarePosterX metadata             #
#                                                       #
#  Usage of this code without proper attribution        #
#  is strictly prohibited.                              #
#  For modifications and redistribution,                #
#  please maintain this credit header.                  #
#########################################################
"""
from __future__ import print_function

# Standard library imports
import os
import re
import json

# Enigma2/Dreambox specific imports
from Components.Renderer.Renderer import Renderer
from Components.config import config

from enigma import ePixmap, eTimer, loadPNG

from .Agp_Utils import get_valid_storage_path, clean_for_tvdb, logger  # , noposter

# Constants
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
PARENTAL_ICON_PATH = f'/usr/share/enigma2/{cur_skin}/parental/'
DEFAULT_RATING = 'UN'


# Rating system mappings
RATING_MAP = {
	# TV Ratings
	"TV-Y": "6", "TV-Y7": "6", "TV-G": "0",
	"TV-PG": "16", "TV-14": "14", "TV-MA": "18",

	# Movie Ratings
	"G": "0", "PG": "16", "PG-13": "16",
	"R": "18", "NC-17": "18",

	# Fallbacks
	"": DEFAULT_RATING, "N/A": DEFAULT_RATING,
	"Not Rated": DEFAULT_RATING, "Unrated": DEFAULT_RATING
}


class AglareParentalX(Renderer):
	"""Parental rating indicator with AGP ecosystem integration"""

	GUI_WIDGET = ePixmap

	def __init__(self):
		Renderer.__init__(self)
		self.timer = eTimer()
		self.storage_path = get_valid_storage_path()
		self._verify_resources()

	def _verify_resources(self):
		"""Ensure required resources exist"""
		if not os.path.exists(PARENTAL_ICON_PATH):
			os.makedirs(PARENTAL_ICON_PATH)
			logger.warning(f"Created parental rating directory: {PARENTAL_ICON_PATH}")

		# Verify default icons exist
		for rating in ['0', '6', '12', '16', '18', 'UN']:
			if not os.path.exists(f"{PARENTAL_ICON_PATH}FSK_{rating}.png"):
				logger.error(f"Missing parental icon: FSK_{rating}.png")

	def changed(self, what):
		"""Handle EPG changes"""
		if not self.instance:
			return

		if what[0] == self.CHANGED_CLEAR:
			self.instance.hide()
			return

		self._start_delay()

	def _start_delay(self):
		"""Delay processing to avoid UI lag"""
		try:
			if hasattr(self.timer, 'timeout'):
				self.timer.timeout.connect(self._show_rating)
			else:  # Fallback for older enigma
				self.timer.callback.append(self._show_rating)
			self.timer.start(10, True)  # 10ms delay
		except Exception as e:
			logger.error(f"Timer error: {str(e)}")
			self._show_rating()

	def _show_rating(self):
		"""Main rating display logic"""
		try:
			event = self.source.event
			if not event:
				self.instance.hide()
				return

			# Try to extract rating from three sources
			rating = (
				self._extract_from_event_text(event) or
				self._extract_from_metadata(event) or
				DEFAULT_RATING
			)

			self._display_rating(rating)

		except Exception as e:
			logger.error(f"Rating error: {str(e)}")
			self.instance.hide()

	def _extract_from_event_text(self, event):
		"""Check event description for age ratings"""
		text = "\n".join([
			event.getEventName() or "",
			event.getShortDescription() or "",
			event.getExtendedDescription() or ""
		])

		match = re.search(r"\b(\d{1,2})\+|\b(FSK|PEGI)\s*(\d{1,2})", text, re.I)
		if match:
			return match.group(1) or match.group(3)
		return None

	def _extract_from_metadata(self, event):
		"""Check PosterX-generated JSON metadata"""
		title = event.getEventName()
		if not title:
			return None

		clean_title = clean_for_tvdb(title)
		meta_file = os.path.join(self.storage_path, f"{clean_title}.json")

		if os.path.exists(meta_file):
			try:
				with open(meta_file, 'r') as f:
					rated = json.load(f).get('Rated', '')
					return RATING_MAP.get(rated, DEFAULT_RATING)
			except Exception as e:
				logger.warning(f"Metadata read error: {str(e)}")
		return None

	def _display_rating(self, rating):
		"""Load and display appropriate rating icon"""
		rating = str(rating).upper()
		icon_path = f"{PARENTAL_ICON_PATH}FSK_{rating}.png"

		if not os.path.exists(icon_path):
			icon_path = f"{PARENTAL_ICON_PATH}FSK_{DEFAULT_RATING}.png"
			logger.debug(f"Using default icon for rating: {rating}")

		if os.path.exists(icon_path):
			self.instance.setPixmap(loadPNG(icon_path))
			self.instance.show()
		else:
			logger.error(f"Missing icon: {icon_path}")
			self.instance.hide()


# Skin configuration example
"""
<widget render="AglareParentalX"
	source="session.Event_Now"
	position="315,874"
	size="50,50"
	zPosition="3"
	transparent="1"
	alphatest="blend"/>
"""
"""
Icons
/usr/share/enigma2/<skin>/parental/
├── FSK_0.png
├── FSK_6.png
├── FSK_12.png
├── FSK_16.png
├── FSK_18.png
└── FSK_UN.png
"""
