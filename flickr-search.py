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

import json
import re
import sys
import time
import urllib.parse
import urllib.request

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        try:
            raw = urllib.request.urlopen(req).read().strip().decode('latin-1')
        except:
            sleep = 10 # seconds
            maxsleep = 60
            while sleep <= maxsleep:
                print('Error while retrieving: %s' % (url))
                print('Retry in %s seconds...' % (sleep))
                time.sleep(sleep)
                try:
                    raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
                except:
                    pass
                sleep = sleep * 2
    return raw

def main():
    apikey = "450008f3bf5bd9ee24f309d40a5ddc89" # public
    text = sys.argv[1]
    maxpages = 100
    perpage = 500
    printed = []
    for page in range(1, maxpages+1): #api returns up to 4000 results, 100 * 500
        time.sleep(1)
        url = "https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%s&text=%s&license=1,2,3,4,5,6&sort=date-taken-desc&safe_search=1&media=videos&per_page=%s&page=%s&format=json&nojsoncallback=1" % (apikey, text, perpage, page)
        raw = getURL(url=url)
        json1 = json.loads(raw)
        if not "photos" in json1:
            print("Expired apikey? Get new apikey https://www.flickr.com/services/api/explore/flickr.photos.search")
            sys.exit()
        if json1["photos"]["photo"]:
            for photo in json1["photos"]["photo"]:
                if not photo in printed:
                    print("https://www.flickr.com/photos/%s/%s" % (photo["owner"], photo["id"]))
                    printed.append(photo["id"])
        else:
            break
        
        if json1["photos"]["page"] == json1["photos"]["pages"]:
            #we are in the last page of results, exit
            break

if __name__ == "__main__":
    main()

