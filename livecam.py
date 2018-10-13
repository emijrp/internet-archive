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

import datetime
import os
import subprocess
import sys
import time
from internetarchive import get_item

# You need a file with access and secret keys, in two different lines
iakeysfilename = '%s/.iakeys' % (os.path.expanduser('~'))
if os.path.exists(iakeysfilename):
    accesskey = open(iakeysfilename, 'r').readlines()[0].strip()
    secretkey = open(iakeysfilename, 'r').readlines()[1].strip()
else:
    print('Error, no %s file with S3 keys for Internet Archive account' % (iakeysfilename))
    sys.exit()

def getDescription(livecam='', url=''):
    description = ""
    descfile = "livecam-%s.description" % (livecam)
    os.system("python youtube-dl --get-description %s > %s" % (url, descfile))
    with open(descfile, 'r') as f:
        description = f.read()
    return description

def main():
    now = datetime.datetime.utcnow()
    today = now.strftime("%Y%m%d")
    today_ = now.strftime("%Y-%m-%d")
    year = now.strftime("%Y")
    yearmonth = now.strftime("%Y-%m")
    todayandhour = now.strftime("%Y%m%d-%H0000")
    commontags = ["youtube", "live cam", "live", "cam", "video", year, yearmonth, today_]
    
    livecams = {
        'tokyo1': {
            'originalurl': 'https://www.youtube.com/watch?v=nKMuBisZsZI', 
            'licenseurl': 'https://creativecommons.org/licenses/by/3.0/', 
            'tags': ["tokyo", "japan", "shibuya", "scramble crossing"], 
            'source': 'https://www.youtube.com/channel/UCgdHxnHSXvcAi4PaMIY1Ltg', 
            'uploader': 'SHIBUYA COMMUNITY NEWS', 
        }, 
    }
    
    livecam = ""
    if len(sys.argv) > 1:
        livecam = sys.argv[1] in livecams.keys() and sys.argv[1] or ''
        
    if livecam:        
        originalurl = livecams[livecam]['originalurl']
        destfile = "livecam-%s-%s.mp4" % (livecam, todayandhour)
        timeout = 60*60+60 #in seconds, 1 hour + 1 minute
        #timeout = 20 #in seconds, 20 seconds for tests
        os.system("timeout -s 15 %ss python youtube-dl %s -o %s" % (timeout, originalurl, destfile))
        os.system("mv %s.part %s" % (destfile, destfile))
        
        itemid = "livecam-%s-%s" % (livecam, today)
        itemtags = commontags + livecams[livecam]['tags']
        description = getDescription(livecam=livecam, url=originalurl)
        description = """%s<br><br>Source: <a href="%s" rel="nofollow">%s</a><br>Uploader: <a href="%s" rel="nofollow">%s</a>""" % (description, originalurl, originalurl, livecams[livecam]['source'], livecams[livecam]['uploader'])
        md = {
            'mediatype': 'movies',
            'collection': 'opensource_movies',
            'title': itemid,
            'description': description,
            #'language': '', 
            'last-updated-date': today_, 
            'date': today_, 
            'year': year, 
            'subject': '; '.join(itemtags), 
            'licenseurl': livecams[livecam]['licenseurl'], 
            'originalurl': originalurl,
        }
        item = get_item(itemid)
        item.upload(destfile, metadata=md, access_key=accesskey, secret_key=secretkey, verbose=True, queue_derive=False)
        item.modify_metadata(md)
        print('You can find it in https://archive.org/details/%s' % (itemid))
        os.remove(destfile)
    else:
        livecamslist = list(livecams.keys())
        livecamslist.sort()
        print("Choose a live cam:", ', '.join(livecamslist))

if __name__ == "__main__":
    main()
