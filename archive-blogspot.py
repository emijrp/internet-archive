#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2016 emijrp <emijrp@gmail.com>
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
import time
import urllib.request

def archiveurls(urls):
    for url in urls:
        time.sleep(1)
        #check if available in IA
        prefix = 'https://archive.org/wayback/available?url='
        checkurl = prefix + url
        f = urllib.request.urlopen(checkurl)
        raw = f.read().decode('utf-8')
        if '{"archived_snapshots":{}}' in raw:
            #not available, archive it
            print('Archiving URL',url)
            prefix2 = 'https://web.archive.org/save/'
            saveurl = prefix2 + url
            f = urllib.request.urlopen(saveurl)
            raw = f.read().decode('utf-8')
        else:
            print('URL is archived in IA','https://web.archive.org/web/*/'+url)
            print(raw)

def main():
    blogspot = 'http://.blogspot.com.es'
    skip = ''
    
    f = urllib.request.urlopen(blogspot)
    raw = f.read().decode('utf-8')
    postsurls = re.findall(r"<h\d class='post-title entry-title' itemprop='name'>\s*?<a href='([^<>]*?)'>[^<>]*?</a>\s*</h\d>", raw)
    if skip:
        if skip in postsurls:
            archiveurls(postsurls)
            skip = ''
    else:
        archiveurls(postsurls)
    
    #print('\n'.join(postsurls))
    while re.findall(r"<a class='blog-pager-older-link' href='([^<>]*?)' id='Blog1_blog-pager-older-link'", raw):
        time.sleep(1)
        print('Retrieving more pages...')
        nextlink = re.findall(r"<a class='blog-pager-older-link' href='([^<>]*?)' id='Blog1_blog-pager-older-link'", raw)
        if nextlink:
            f = urllib.request.urlopen(nextlink[0])
            raw = f.read().decode('utf-8')
            postsurls = re.findall(r"<h\d class='post-title entry-title' itemprop='name'>\s*?<a href='([^<>]*?)'>[^<>]*?</a>\s*</h\d>", raw)
            if skip:
                if skip in postsurls:
                    archiveurls(postsurls)
                    skip = ''
            else:
                archiveurls(postsurls)
        
if __name__ == '__main__':
    main()
