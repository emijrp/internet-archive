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

import json
import sys
import time
import urllib.request
from archive import *

def download(url='', filename=''):
    if url and filename:
        print('Downloading %s' % (url))
        urllib.request.urlretrieve(url, filename)
        print('Saved in %s' % (filename))
    else:
        print('No url or filename')

def main():
    if len(sys.argv) < 2:
        print('Need username param')
        sys.exit()
    username = sys.argv[1]
    repos = []
    for pagenum in range(1,1000):
        url = 'https://api.github.com/users/emijrp/repos?page=%d' % (pagenum)
        print(url)
        raw = getURL(url=url)
        json1 = json.loads(raw)
        if not json1:
            break
        for repo in json1:
            #print(repo['fork'], repo['name'], repo['id'], repo)
            if not repo['fork']:
                urlzip = 'https://github.com/%s/%s/archive/master.zip' % (username, repo['name'])
                filename = '%s.zip' % (repo['name'])
                download(url=urlzip, filename=filename)
        time.sleep(1)

if __name__ == '__main__':
    main()
