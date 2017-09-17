#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
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

from archive import *

def radiopuertofm():
    statuses = []
    for i in range(0, 1000):
        url = 'http://radiopuerto.fm/noticias?page=' + str(i)
        raw = getURL(url=url)
        urls = re.findall(r'<a href="(/noticias/[^<>]+?)">', raw)
        if not urls:
            break
        archiveurl(url=url)
        for url in urls:
            url = 'http://radiopuerto.fm' + url
            status = archiveurl(url=url)
            statuses.append(status)
    stats(statuses=statuses)

def sanasy():
    statuses = []
    for i in range(0, 10000):
        url = 'http://www.sana.sy/es/?s=a&paged=' + str(i)
        raw = getURL(url=url)
        if '<h2 class="post-title">Not Found</h2>' in raw or '404 :(' in raw:
            break
        urls = re.findall(r'(?im)<h2 class="post-box-title">\s*<a href="([^<>]+?)">', raw)
        if not urls:
            break
        archiveurl(url=url)
        for url in urls:
            status = archiveurl(url=url)
            statuses.append(status)
    stats(statuses=statuses)

def main():
    #radiopuertofm()
    sanasy()

if __name__ == '__main__':
    main()
