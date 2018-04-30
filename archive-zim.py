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

import time
from archive import *

def main():
    wikisites = [
        #'wikibooks', 
        'wikinews', 
        #'wikipedia', 
        'wikiquote', 
        #'wikisource', 
        'wikispecies', 
        'wikiversity', 
        'wikivoyage', 
        #'wiktionary', 
    ]
    tags = [
        'kiwix', 
        'mediawiki', 
        'offline', 
        'zim', 
    ]
    c = 0
    for wikisite in wikisites:
        url = 'https://ftp.acc.umu.se/mirror/kiwix.org/zim/%s/' % (wikisite)
        html = getURL(url=url)
        zims = re.findall(r'href="([^ ]*?\.zim)\"', html)
        for zim in zims:
            print('"Downloading %s' % (zim))
            zimurl = url + zim
            os.system('wget "%s" -O zim/%s' % (zimurl, zim))
            year = zim.split('.zim')[0].split('_')[1].split('-')[0]
            tags2 = tags + zim.split('.zim')[0].split('_') + [year]
            metadata = ' '.join(["--metadata='subject:%s'" % (tag) for tag in tags2])
            os.system('ia upload %s zim/%s %s' % (zim, zim, metadata))
            os.remove('zim/%s' % (zim))
            time.sleep(1)

if __name__ == '__main__':
    main()
