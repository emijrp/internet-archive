#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2017 emijrp <emijrp@gmail.com>
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

import re
import sys
import time
import urllib.request

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        raw = urllib.request.urlopen(req).read()
        try:
            raw = raw.strip().decode('utf-8')
        except:
            try:
                raw = raw.strip().decode('latin-1')
            except:
                pass
    except:
        sleep = 10 # seconds
        maxsleep = 100
        while sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            raw = urllib.request.urlopen(req).read()
            try:
                raw = raw.strip().decode('utf-8')
            except:
                try:
                    raw = raw.strip().decode('latin-1')
                except:
                    pass
            sleep = sleep * 2
    return raw

def archiveurl(url='', force=False):
    if url:
        #check if available in IA
        prefix = 'https://archive.org/wayback/available?url='
        checkurl = prefix + url
        raw = getURL(url=checkurl)
        #print(raw)
        if '"archived_snapshots": {}' in raw or force:
            #not available, archive it
            #print('Archiving URL',url)
            prefix2 = 'https://web.archive.org/save/'
            saveurl = prefix2 + url
            try:
                f = urllib.request.urlopen(saveurl)
                raw = f.read().decode('utf-8')
                print('Archived at https://web.archive.org/web/*/%s' % (url))
                return 'ok'
            except:
                print('URL 404 archived at https://web.archive.org/web/*/%s' % (url))
                return '404'
        else:
            print('Previously archived at https://web.archive.org/web/*/%s' % (url))
            return 'previously'
            #print(raw)

def stats(statuses=[]):
    ok = 0
    e404 = 0
    previously = 0
    for status in statuses:
        if status == 'ok':
            ok += 1
        elif status == '404':
            e404 += 1
        elif status == 'previously':
            previously += 1
    print('ok=%d, e404=%d, previously=%d' % (ok, e404, previously))

def main():
    urls = []
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        urls = f.readlines()
    
    force = False
    if len(sys.argv) > 2:
        if 'force' in sys.argv[2:]:
            force = True
    
    statuses = []
    for url in urls:
        status = archiveurl(url, force=force)
        statuses.append(status)
    stats(statuses=statuses)
        
if __name__ == '__main__':
    main()
