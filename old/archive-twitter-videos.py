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
from twython import Twython
from archive import *

#deprecated? tubeup allows twitter videos

"""

l tweet-metadata/ -l | cut -d'.' -f1 | rev | cut -d' ' -f1 | rev | sort | uniq | awk '$0="https://twitter.com/web/status/"$0' > videos.txt
python3 archive-twitter-videos.py videos.txt

"""

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        lines = f.read().strip().splitlines()
    print('Loaded %d urls' % (len(lines)))
    
    path = 'tweet-videos'
    if not os.path.exists(path):
        print('Create path: %s' % (path))
        sys.exit()
    
    os.system('python youtube-dl -U')
    for line in lines:
        url = line.strip()
        if not url.startswith('http'):
            url = 'https://twitter.com/web/status/' + url
        status = archiveurl(url=url, force=False)
        videofilename = url.split('/status/')[1].split('/')[0] + '.mp4'
        archivevideoytdl(url=url, filename=path + '/' + videofilename)

if __name__ == '__main__':
    main()
