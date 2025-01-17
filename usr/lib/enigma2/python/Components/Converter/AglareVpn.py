from os.path import exists
from subprocess import run, CalledProcessError
from Components.Converter.Converter import Converter
from Components.Element import cached

class AglareVpn(Converter):
	VPNLOAD = 0

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "vpn":
			self.type = self.VPNLOAD
		self.has_wireguard = exists("/usr/bin/wg")
		self.has_openvpn = exists("/var/run/openvpn")

	@cached
	def getBoolean(self):
		try:
			if self.has_wireguard:
				result = run(['ip', 'link', 'show', 'wg0'], capture_output=True, text=True)
				if result.returncode == 0 and "wg0" in result.stdout:
					return True

			if self.has_openvpn:
				result = run(['ip', 'link', 'show', 'tun0'], capture_output=True, text=True)
				if result.returncode == 0 and "tun0" in result.stdout:
					return True
		except (CalledProcessError, FileNotFoundError, Exception):
			pass

		return False

	boolean = property(getBoolean)

	def changed(self, what):
		Converter.changed(self, what)
