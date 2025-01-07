#!/usr/bin/env python
#DESCRIPTION=SRVID-FLYSAT
header = """
#######################################################################
###     Simple python-script for create the 'oscam.srvid' file      ###
###         by parsing the https://www.FLYSAT.com web page.         ###
#######################################################################
###   Script written by s3n0, 2021-03-03, https://github.com/s3n0   ###
#######################################################################
"""

output_file = '/tmp/oscam.srvid'

packages = {
    'https://flysat.com/en/package/skylink-1/astra-3b': '0D96,0624',
    'https://flysat.com/en/package/sky-deutschland-2/astra-19': '1833,1834,1702,1722,09C4,09AF',
    # 'https://flysat.com/en/package/antiksat-1/eutelsat-16a': '0B00',
    # 'https://flysat.com/en/package/maxtv-sat-1/eutelsat-16a': '1830',
}

from sys import version_info as py_version
if py_version.major == 3:
    import urllib.request as urllib2
    import html
    htmlParser = html
else:
    import urllib2
    from HTMLParser import HTMLParser
    htmlParser = HTMLParser()

import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

from datetime import datetime

def htmlContent(url):
    print(f'Downloading web page: {url}')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'}
    try:
        req = urllib2.Request(url, data=None, headers=headers)
        handler = urllib2.urlopen(req, timeout=15)
        data = handler.read().decode('utf-8')
    except Exception as e:
        print(f'ERROR! Failed to request and download the web page: {url} ({e})')
        data = ''
    print('...done.')
    return data

if __name__ == '__main__':
    result = []
    for pckg in packages:
        webpage = htmlContent(pckg)
        
        if webpage:
            pckg_name = pckg.split('/')[5]
            if pckg_name[-2:] in ('-1', '-2', '-3', '-4'):
                pckg_name = pckg_name[:-2]
            
            print(f'Processing "{pckg_name}" package, please wait...')
            
            i = 2000
            while i < len(webpage) - 1000:
                i = webpage.find('30px', i)
                if i == -1:
                    break
                i = webpage.find('<b>', i) + 3
                CHN = webpage[i:webpage.find('</b>', i)].strip()
                CHN = htmlParser.unescape(CHN)
                
                if CHN == '*':
                    CHN = '**CENSORED**'
                
                for x in range(4):
                    i = webpage.find('<td', i+1)
                i = webpage.find('size="1">', i) + 9
                SIDS = webpage[i:webpage.find('</font>', i)].replace('\n', '').replace('\t', '')
                
                if len(SIDS.split('<br>')) == 2:
                    SIDS = [SIDS.split('<')[0]]
                else:
                    SIDS = SIDS.split('<br>')
                SIDS = ["%04X" % int(s) for s in SIDS if s.isdigit()]
                
                i += 20
                
                for SID in SIDS:
                    result.append(packages[pckg] + ':' + SID + '|' + pckg_name.upper() + '|' + CHN)
            
            print('...done.')
        else:
            print(f'Web page download FAILED! - package: {pckg}')
    
    if result:
        data = header + '\n### File creation date: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n\n' + '\n'.join(result)
        with open(output_file, 'w') as f:
            f.write(data)
            print(f'File "{output_file}" was stored.')
    
    print('Goodbye.')

