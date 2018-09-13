#!/usr/bin/env python   
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

import os
import re
import sys
import time
import urllib.parse
import urllib.request

def getURL(url=''):
    html = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        html = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        try:
            html = urllib.request.urlopen(req).read().strip().decode('latin-1')
        except:
            sleep = 10 # seconds
            maxsleep = 0
            while sleep <= maxsleep:
                print('Error while retrieving: %s' % (url))
                print('Retry in %s seconds...' % (sleep))
                time.sleep(sleep)
                try:
                    html = urllib.request.urlopen(req).read().strip().decode('utf-8')
                except:
                    pass
                sleep = sleep * 2
    return html

def main():
    minyear = int(sys.argv[1])
    maxyear = int(sys.argv[2])
    print(minyear)
    print(maxyear)
    for year in range(minyear, maxyear+1):
        for pagenum in range(1, 100):
            time.sleep(2)
            url = 'https://www.filmaffinity.com/es/advsearch.php?page=%s&stype[]=title&fromyear=%s&toyear=%s' % (pagenum, year, year)
            print(url)
            html = getURL(url=url)
            m = re.findall(r'<div class="mc-title"><a *?href="/es/(film\d+\.html)"', html)
            if not m:
                break
            for n in m:
                mid = n.split('film')[1].split('.html')[0]
                url2 = 'https://www.filmaffinity.com/es/%s' % (n)
                print(url2)
                html2 = getURL(url=url2)
                if '>Tráilers' in html2:
                    mtitle = re.findall(r'(?im)<h1 id="main-title">\s*<span itemprop="name">([^<>]*?)</span>', html2)
                    mtitle = mtitle and mtitle[0].strip() or ''
                    mtitle_ = mtitle.replace(' ', '_')
                    mtitleorig = re.findall(r'(?im)<dt>Título original</dt>\s*<dd>([^<>]*?)<', html2)
                    mtitleorig = mtitleorig and mtitleorig[0].split('<span')[0].strip() or ''
                    mduration = re.findall(r'(?im)<dd itemprop="duration">(\d+) [^<>]+?</dd>', html2)
                    mduration = mduration and mduration[0].strip() or ''
                    myear = re.findall(r'(?im)<dd itemprop="datePublished">([^<>]+?)</dd>', html2)
                    myear = myear and myear[0].strip() or ''
                    mcountry = re.findall(r'(?im)<dd><span id="country-img"><img src="/imgs/countries/[^ ]+?\.jpg" alt="([^<>"]+?)"', html2)
                    mcountry = mcountry and mcountry[0].strip() or ''
                    mdirector = ', '.join(re.findall(r'(?im)director&sn&stext=[^ ]*?" title="([^<>]*?)">', html2)).replace('"', '')
                    print(mtitle, mduration, myear, mcountry, 'https://www.filmaffinity.com/es/evideos.php?movie_id=%s' % (mid))
                    if int(myear) >= minyear and int(myear) <= maxyear:
                        metadata = ''
                        if myear:
                            metadata += ' --metadata="year:%s"' % (myear)
                        if mcountry:
                            metadata += ' --metadata="country:%s"' % (mcountry)
                        if mdirector:
                            metadata += ' --metadata="director:%s"' % (mdirector)
                        command = 'tubeup "https://www.filmaffinity.com/es/evideos.php?movie_id=%s" %s --use-download-archive' % (mid, metadata)
                        print(command)
                        os.system(command)
                else:
                    time.sleep(2)

if __name__ == '__main__':
    main()

