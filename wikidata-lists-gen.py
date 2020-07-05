#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2019 emijrp <emijrp@gmail.com>
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
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import pywikibot
import pywikibot.pagegenerators as pagegenerators

from archiveteamfun import *

def main():
    queries = {
        "facebook": 
            """
            SELECT DISTINCT ?item ?facebook
            WHERE {
                { ?item wdt:P4003 ?facebook. } UNION { ?item wdt:P2013 ?facebook. }
            }
            ORDER BY ?facebook
            """, 
        "twitter":
            """
            SELECT DISTINCT ?item ?twitter
            WHERE {
                ?item wdt:P2002 ?twitter.
            }
            ORDER BY ?twitter
            """, 
        "vk":
            """
            SELECT DISTINCT ?item ?vk
            WHERE {
                ?item wdt:P3185 ?vk.
            }
            ORDER BY ?vk
            """, 
        "youtube":
            """
            SELECT DISTINCT ?item ?youtube
            WHERE {
                ?item wdt:P2397 ?youtube.
            }
            ORDER BY ?youtube
            """, 
        "youtube-expanded":
            """
            SELECT DISTINCT ?item ?youtube
            WHERE {
                ?item wdt:P2397 ?youtube.
            }
            ORDER BY ?youtube
            """, 
    }
    queryname = ''
    if len(sys.argv) > 1:
        queryname = sys.argv[1].lower()
    if queryname in queries.keys():
        queryurl = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(queries[queryname]))
        queryurl = '%s&format=json' % (queryurl)
        sparql = getURL(url=queryurl)
        json1 = loadSPARQL(sparql=sparql)
        
        c = 0
        urls = []
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            if not q:
                continue
            qurl = ''
            qurls = []
            if queryname == "facebook":
                qparam = 'facebook' in result and result['facebook']['value'] or ''
                if not re.search(r'(?m)^t\d{7,}$', qparam):
                    qurl = 'https://www.facebook.com/' + qparam
            elif queryname == "twitter":
                qparam = 'twitter' in result and result['twitter']['value'] or ''
                if not re.search(r'(?m)^t\d{7,}$', qparam):
                    qurl = 'https://twitter.com/' + qparam
            elif queryname == "vk":
                qparam = 'vk' in result and result['vk']['value'] or ''
                if not re.search(r'(?m)^t\d{7,}$', qparam):
                    qurl = 'https://vk.com/' + qparam
            elif queryname == "youtube":
                qparam = 'youtube' in result and result['youtube']['value'] or ''
                if not re.search(r'(?m)^t\d{7,}$', qparam):
                    qurl = 'https://www.youtube.com/channel/' + qparam
            elif queryname == "youtube-expanded":
                qparam = 'youtube' in result and result['youtube']['value'] or ''
                if not re.search(r'(?m)^t\d{7,}$', qparam):
                    qurl = 'https://www.youtube.com/channel/' + qparam
                    qurls = [
                        'https://youtube.com/channel/' + qparam, 
                        'https://www.youtube.com/channel/' + qparam + '?disable_polymer=1', 
                        'https://www.youtube.com/channel/' + qparam + '/', 
                        'https://www.youtube.com/channel/' + qparam + '/?disable_polymer=1', 
                        'https://www.youtube.com/channel/' + qparam + '/feed', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=1', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=2', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=3', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=4', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=5', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=6', 
                        'https://www.youtube.com/channel/' + qparam + '/feed?activity_view=7', 
                        'https://www.youtube.com/channel/' + qparam + '/videos', 
                        'https://www.youtube.com/channel/' + qparam + '/videos?disable_polymer=1', 
                        'https://www.youtube.com/channel/' + qparam + '/videos?view=0&flow=grid', 
                        'https://www.youtube.com/channel/' + qparam + '/videos?view=0&sort=da&flow=grid', 
                        'https://www.youtube.com/channel/' + qparam + '/videos?view=0&sort=dd&flow=grid', 
                        'https://www.youtube.com/channel/' + qparam + '/playlists', 
                        'https://www.youtube.com/channel/' + qparam + '/channels', 
                        'https://www.youtube.com/channel/' + qparam + '/community', 
                        'https://www.youtube.com/channel/' + qparam + '/discussion', 
                        'https://www.youtube.com/channel/' + qparam + '/about', 
                    ]
            
            if qurl:
                urls.append(qurl)
                c += 1
            if qurls:
                [urls.append(x) for x in qurls]
        outfilename = 'wikidata-%s-%s-%.0dk' % (queryname, datetime.datetime.utcnow().strftime('%Y%m%d'), c/1000)
        with open(outfilename, 'w') as f:
            f.write('\n'.join(urls))
        print('Saved in', outfilename)
    else:
        print("Choose a query:", ', '.join(queries.keys()))

if __name__ == '__main__':
    main()
