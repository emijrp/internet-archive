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
    }
    queryname = ''
    if len(sys.argv) > 1:
        queryname = sys.argv[1].lower()
    if queryname in queries.keys():
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(queries[queryname]))
        url = '%s&format=json' % (url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        qurls = []
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            if not q:
                continue
            qurl = ''
            
            if queryname == "facebook":
                qparam = 'facebook' in result and result['facebook']['value'] or ''
                if not re.search(r'(?m)^t\d+$', qparam):
                    qurl = 'https://www.facebook.com/' + qparam
            
            if qurl:
                qurls.append(qurl)
        outfilename = 'wikidata-%s-%s-%.0dk' % (queryname, datetime.datetime.utcnow().strftime('%Y%m%d'), len(qurls)/1000)
        with open(outfilename, 'w') as f:
            f.write('\n'.join(qurls))
        print('Saved in', outfilename)
    else:
        print("Choose a query:", ', '.join(queries.keys()))

if __name__ == '__main__':
    main()
