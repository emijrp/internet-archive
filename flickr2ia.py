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

import csv
import datetime
import json
import re
import sys
import time
import urllib
from xml.etree import ElementTree as ET # para ver los XMl que devuelve flickrapi con ET.dump(resp)

import flickrapi

usertosave = '96396586@N07' #it isn't secret, don't worry
mode = 'usersetzip' #usersetzip (1 item per user, all sets in different zips in the same item); set (1 item per set); all (1 item per image or video)

def getUserPhotosetIds(flickr='', user_id=''):
    userphotosetids = []
    page = 1
    pages = 1
    while page <= pages:
        resp = flickr.photosets.getList(user_id=user_id, page=page)
        xmlraw = ET.tostring(resp, method='xml').decode('utf-8')
        pages = int(re.findall(r' pages="(\d+)"', xmlraw)[0])
        userphotosetids += re.findall(r' id="(\d+)"', xmlraw)
        page += 1
    return userphotosetids

def main():
    with open('flickr.token', 'r') as f:
        api_key, api_secret = f.read().strip().splitlines()
    
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    print('Authenticate')
    if not flickr.token_valid(perms='read'):
        flickr.get_request_token(oauth_callback='oob')
        authorize_url = flickr.auth_url(perms='read')
        print(authorize_url)
        verifier = input(u'Verifier code: ')
        flickr.get_access_token(verifier)
    
    if mode == 'usersetzip':
        print("Loading sets for user", usertosave)
        photosetids = getUserPhotosetIds(flickr=flickr, user_id=usertosave)
        print(len(photosetids), "sets found for", usertosave)
        for photosetid in photosetids:
            print(photosetid)
            try: #error in set ids, broken sets?
                resp2 = flickr.photosets.getPhotos(photoset_id=photosetid, user_id=usertosave) #, extras='date_taken')
            except:
                continue
            xmlraw2 = ET.tostring(resp2, method='xml').decode('utf-8')
            photoids = re.findall(r'(?im) id="(\d+)"', xmlraw2)
            print(len(photoids), "files")
            time.sleep(0.2)
        

if __name__ == '__main__':
    main()
