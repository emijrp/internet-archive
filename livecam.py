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

# Requirements and install:
#   * enough free space, live cams consumes lots of space
#   * virtualenv -p python3 livecams
#   * cd livecams;source bin/activate
#   * pip install internetarchive
#   * deactivate
#   * create .iakeys file in user home
#   * save this script and youtube-dl in livecams directory
# Instructions:
#   * cd livecams
#   * source bin/activate
#   * python livecam.py cam-name (it archives 1 hour)
#   * or using cron (to archive 1 hour chunks hourly): 0 *    * * *    cd /path/livecams && . bin/activate && python livecam.py cam-name && deactivate

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
        'japan1': {
            'originalurl': 'https://www.youtube.com/watch?v=nKMuBisZsZI', 
            'licenseurl': 'https://creativecommons.org/licenses/by/3.0/', 
            'tags': ["tokyo", "japan", "shibuya", "scramble crossing"], 
            'source': 'https://www.youtube.com/channel/UCgdHxnHSXvcAi4PaMIY1Ltg', 
            'uploader': 'SHIBUYA COMMUNITY NEWS', 
        }, 
        'spain1': {
            'originalurl': 'https://www.youtube.com/watch?v=2qAQ1DUFWhY', 
            'licenseurl': 'https://creativecommons.org/licenses/by/3.0/', 
            'tags': ["madrid", "spain", "Sierra de Guadarrama", "birds", "aves", "bird feeder", "comedero"], 
            'source': 'https://www.youtube.com/channel/UCg6OElsAGYmkuSySkZpaNGw', 
            'uploader': 'SEOBirdLife - Sociedad Española de Ornitología', 
        }, 
    }
    
    livecam = ""
    if len(sys.argv) > 1:
        livecam = sys.argv[1] in livecams.keys() and sys.argv[1] or ''
        
    if livecam:        
        maxretries = 5
        originalurl = livecams[livecam]['originalurl']
        destfile = "livecam-%s-%s.mp4" % (livecam, todayandhour)
        destfilepart = destfile + ".part"
        destthumbfile = "livecam-%s-%s-thumb.jpg" % (livecam, today)
        timeout = 60*60+60 #in seconds, 1 hour + 1 minute
        #timeout = 20 #in seconds, 20 seconds for tests
        os.system("timeout -s 15 %ss python youtube-dl %s -o %s" % (timeout, originalurl, destfile))
        if os.path.exists(destfilepart):
            os.system("mv %s %s" % (destfilepart, destfile))
        os.system("python youtube-dl %s --skip-download --write-thumbnail -o %s" % (originalurl, destthumbfile))
        
        itemid = "livecam-%s-%s" % (livecam, today)
        itemtags = commontags + livecams[livecam]['tags'] + [livecam]
        description = getDescription(livecam=livecam, url=originalurl)
        description = """%s<br><br>Source: <a href="%s" rel="nofollow">%s</a><br>Uploader: <a href="%s" rel="nofollow">%s</a>""" % (description, originalurl, originalurl, livecams[livecam]['source'], livecams[livecam]['uploader'])
        md = {
            'mediatype': 'movies',
            'collection': 'opensource_movies',
            'creator': livecams[livecam]['uploader'],
            'title': itemid,
            'description': description,
            #'language': '', 
            'last-updated-date': today_, 
            'date': today_, 
            'year': year, 
            'subject': '; '.join(itemtags), 
            'licenseurl': 'licenseurl' in livecams[livecam] and livecams[livecam]['licenseurl'] or '', 
            'originalurl': originalurl,
        }
        retries = 1
        uploaded = False
        while retries <= maxretries:
            try:
                item = get_item(itemid)
                item.upload(files=[destfile, destthumbfile], metadata=md, access_key=accesskey, secret_key=secretkey, verbose=True, queue_derive=False)
                item.modify_metadata(md)
                uploaded = True
                break
            except:
                pass
            time.sleep(600*retries)
            retries += 1
        if uploaded:
            print('You can find it in https://archive.org/details/%s' % (itemid))
            os.remove(destfile)
        else:
            print('Error while uploading. Upload it manually later.')
    else:
        livecamslist = list(livecams.keys())
        livecamslist.sort()
        print("Choose a live cam:", ', '.join(livecamslist))

if __name__ == "__main__":
    main()
