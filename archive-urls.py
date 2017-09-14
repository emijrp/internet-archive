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

def archiveurl(url='', force=False):
    if url:
        #check if available in IA
        prefix = 'https://archive.org/wayback/available?url='
        checkurl = prefix + url
        f = urllib.request.urlopen(checkurl)
        raw = f.read().decode('utf-8')
        if '{"archived_snapshots":{}}' in raw or force:
            #not available, archive it
            #print('Archiving URL',url)
            prefix2 = 'https://web.archive.org/save/'
            saveurl = prefix2 + url
            try:
                f = urllib.request.urlopen(saveurl)
                raw = f.read().decode('utf-8')
                print('Archived at https://web.archive.org/web/*/%s' % (url))
            except:
                print('URL 404 archived at https://web.archive.org/web/*/%s' % (url))
        else:
            print('Previously archived at https://web.archive.org/web/*/%s' % (url))
            #print(raw)

def main():
    urls = []
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        urls = f.readlines()
    
    force = False
    if len(sys.argv) > 2:
        if 'force' in sys.argv[2:]:
            force = True
    
    for url in urls:
        archiveurl(url, force=force)
        
if __name__ == '__main__':
    main()
