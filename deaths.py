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
    enwpsite = pywikibot.Site('en', 'wikipedia')
    atsite = pywikibot.Site('archiveteam', 'archiveteam')
    
    year1 = 2015
    year2 = datetime.datetime.now().year
    if len(sys.argv) >= 2:
        year1 = int(sys.argv[1])
        year2 = int(sys.argv[2])
    
    start = ''
    years = range(year1, year2+1) 
    limit = 1000
    
    for year in years:
        query = """
        SELECT ?item ?itemLabel ?itemDescription ?causeLabel ?birthdate ?deathdate ?website
        WHERE
        {
            ?item wdt:P31 wd:Q5.
            ?item wdt:P856 ?website.
            OPTIONAL { ?item wdt:P569 ?birthdate. }
            OPTIONAL { ?item wdt:P1196 ?cause. }
            ?item wdt:P570 ?deathdate.
            FILTER (?deathdate >= "%s-01-01T00:00:00Z"^^xsd:dateTime).
            FILTER (?deathdate <= "%s-12-31T23:59:59Z"^^xsd:dateTime).
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        ORDER BY ?deathdate
        """ % (year, year)
        url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(query))
        url = '%s&format=json' % (url)
        print("Loading...", url)
        sparql = getURL(url=url)
        json1 = loadSPARQL(sparql=sparql)
        
        rows = []
        for result in json1['results']['bindings']:
            q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
            if not q:
                continue
            itemLabel = 'itemLabel' in result and result['itemLabel']['value'] or q
            itemDescription = 'itemDescription' in result and result['itemDescription']['value'] or ''
            causeLabel = 'causeLabel' in result and result['causeLabel']['value'] or ''
            birthdate = 'birthdate' in result and result['birthdate']['value'].split('T')[0] or ''
            deathdate = 'deathdate' in result and result['deathdate']['value'].split('T')[0] or ''
            website = 'website' in result and result['website']['value'] or ''
            
            viewer = [getArchiveBotViewer(url=website)]
            
            if not website:
                continue
            
            row = [q, itemLabel, itemDescription, causeLabel, birthdate, deathdate, website, viewer]
            print(row)
            rows.append(row)
            
            if len(rows) >= limit:
                break
        
        c = 1
        rowsplain = ""
        for row in rows:
            q, itemLabel, itemDescription, causeLabel, birthdate, deathdate, website, viewer = row
            viewerplain = []
            for v in viewer:
                if v[0]:
                    viewerplain.append("[%s {{saved}}]" % (v[1]))
                else:
                    viewerplain.append("[%s {{nosaved}}]" % (v[1]))
            viewerplain = '<br/>'.join(viewerplain)
            rowsplain += "\n|-\n| %s || '''[[:wikipedia:wikidata:%s|%s]]''' || %s || %s || %s || %s || %s || %s " % (c, q, itemLabel, itemDescription, birthdate, deathdate, causeLabel, website, viewerplain and viewerplain or '-')
            c += 1
        output = """This page is based on Wikipedia articles in '''[[:wikipedia:en:Category:%s deaths|Category:%s deaths]]'''. The websites for these entities could vanish in the foreseable future.

* '''Statistics''': {{saved}} (%s){{·}} {{nosaved}} (%s)

Do not edit this page, it is automatically updated by bot.

{| class="wikitable sortable"
! # !! Name !! Description !! Birth date !! Death date !! Cause of death !! Website(s) !! width=100px | [[ArchiveBot]] %s
|}

{{deathwatch}}

[[Category:Archive Team]]""" % (year, year, len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{nosaved}}', rowsplain)), rowsplain)
        print(output)
        
        page = pywikibot.Page(atsite, "Deaths in %s" % (year))
        if page.text != output:
            pywikibot.showDiff(page.text, output)
            page.text = output
            page.save("BOT - Updating page: {{saved}} (%s), {{nosaved}} (%s)" % (len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{nosaved}}', rowsplain))))

if __name__ == '__main__':
    main()

