#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import re
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
    try:
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        sleep = 10 # seconds
        maxsleep = 30
        while sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            try:
                raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
            except:
                pass
            sleep = sleep * 2
    return raw

def loadSPARQL(sparql=''):
    json1 = ''
    if sparql:
        try:
            json1 = json.loads(sparql)
            return json1
        except:
            print('Error downloading SPARQL? Malformatted JSON? Skiping\n')
            return 
    else:
        print('Server return empty file')
        return 
    return

def getArchiveBotViewer(url=''):
    if url and '//' in url:
        domain = url.split('//')[1].split('/')[0]
        viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
        raw = getURL(url=viewerurl)
        if raw and '</form>' in raw:
            raw = raw.split('</form>')[1]
        else:
            return False, viewerurl
        if re.search(r'No search results', raw):
            return False, viewerurl
        else:
            if len(url.split(domain)[1]) > 1: #domain.com/more
                if re.search(r'(?im)(%s)' % (url), raw):
                    return True, viewerurl
                else:
                    return False, viewerurl
            elif re.search(r'(?im)(%s)' % (domain), raw):
                return True, viewerurl
            else:
                return False, viewerurl
    else:
        return False, 'https://archive.fart.website/archivebot/viewer/'
