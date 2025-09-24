from Components.Converter.Converter import Converter
from Components.Element import cached
import NavigationInstance
from enigma import iPlayableService, iServiceInformation, eServiceReference
import urllib


class AglareStreamInfo(Converter):
    STREAMURL = 0
    STREAMTYPE = 1

    def __init__(self, type):
        Converter.__init__(self, type)
        self.type = self._get_type(type)

    def _get_type(self, type):
        """Determine the stream type based on the passed type."""
        if 'StreamUrl' in type:
            return self.STREAMURL
        elif 'StreamType' in type:
            return self.STREAMTYPE
        return None

    def _is_stream_service(self, refstr):
        """Check if the service is a stream service."""
        return refstr and ('%3a//' in refstr or '://' in refstr)

    def streamtype(self):
        playref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        if playref:
            refstr = playref.toString()
            if self._is_stream_service(refstr):
                if refstr.startswith('1:0:'):
                    if any(x in refstr for x in ('0.0.0.0:', '127.0.0.1:', 'localhost:')):
                        return 'Stream Relay'
                    else:
                        return 'GStreamer'
                elif refstr.startswith('4097:0:'):
                    return 'MediaPlayer'
                elif refstr.startswith('5001:0:'):
                    return 'GstPlayer'
                elif refstr.startswith('5002:0:'):
                    return 'ExtePlayer3'
                else:
                    # Generic stream type for other stream references
                    return 'Stream'
        return ''

    def streamurl(self):
        playref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
        if playref:
            refstr = playref.toString()
            if self._is_stream_service(refstr):
                # Extract and decode the stream URL
                try:
                    # For all stream types, extract the URL part
                    if '%3a//' in refstr:
                        # Handle URL-encoded streams
                        stream_url = ' '.join(refstr.split(':')[10:])
                        decoded_url = urllib.unquote(stream_url).decode('utf-8')
                        # Ensure it starts with http
                        if decoded_url.startswith('http'):
                            return decoded_url
                        # If not, try to find the http part
                        http_index = decoded_url.find('http')
                        if http_index >= 0:
                            return decoded_url[http_index:]
                        return decoded_url
                    elif '://' in refstr:
                        # Handle already decoded streams
                        stream_url = ' '.join(refstr.split(':')[10:])
                        # Ensure it starts with http
                        if stream_url.startswith('http'):
                            return stream_url
                        # If not, try to find the http part
                        http_index = stream_url.find('http')
                        if http_index >= 0:
                            return stream_url[http_index:]
                        return stream_url
                except:
                    # If extraction fails, try to find http in the raw refstr
                    http_index = refstr.find('http')
                    if http_index >= 0:
                        return refstr[http_index:]
                    return refstr
        return ''

    @cached
    def getText(self):
        service = self.source.service
        if service:
            if self.type == self.STREAMURL:
                return str(self.streamurl())
            elif self.type == self.STREAMTYPE:
                return str(self.streamtype())
        return ''

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
            Converter.changed(self, what)