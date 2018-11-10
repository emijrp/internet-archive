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
    atsite = pywikibot.Site('archiveteam', 'archiveteam')
    cat = pywikibot.Category(atsite, "Category:ArchiveBot")
    gen = pagegenerators.CategorizedPageGenerator(cat, start="!")
    pre = pagegenerators.PreloadingGenerator(gen, pageNumber=60)
    
    for page in pre:
        wtitle = page.title()
        wtext = page.text
        
        if not 'Reddit' in wtitle:
            continue
        
        if not wtitle.startswith('ArchiveBot/'):
            continue
        wlist = pywikibot.Page(atsite, '%s/list' % (wtitle))
        if not wlist.exists():
            print("Page %s/list doesnt exist" % (wtitle))
            continue
        raw = wlist.text.strip().splitlines()
        raw = list(set(raw)) #remove dupes
        raw.sort()
        raw = '\n'.join(raw)
        if wlist.text != raw:
            wlist.text = raw
            wlist.save("BOT - Sorting list")
        
        print('\n===', wtitle, '===')
        websites = []
        for line in wlist.text.strip().splitlines():
            line = line.strip().lstrip('*').strip()
            if line.startswith('#'):
                continue
            websites.append(line)
            
        c = 1
        rowsplain = ""
        totaljobsize = 0
        for website in websites:
            viewerplain = ''
            viewerdetailsplain = ''
            viewer = [getArchiveBotViewer(url=website)]
            if viewer[0][0]:
                viewerplain = "[%s {{saved}}]" % (viewer[0][1])
                viewerdetailsplain = viewer[0][2]
            else:
                viewerplain = "[%s {{notsaved}}]" % (viewer[0][1])
                viewerdetailsplain = ''
            totaljobsize += viewer[0][3]
            rowspan = len(re.findall(r'\|-', viewerdetailsplain))+1
            rowspanplain = rowspan>1 and 'rowspan=%d | ' % (rowspan) or ''
            rowsplain += "\n|-\n| %s%s || %s%s\n%s " % (rowspanplain, website, rowspanplain, viewerplain and viewerplain or ' ', viewerdetailsplain and viewerdetailsplain or '|  ||  ||  || ')
            c += 1
        
        output = """
* '''Statistics''': {{saved}} (%s){{·}} {{notsaved}} (%s){{·}} Total size (%s)

Do not edit this table, it is automatically updated by bot. There is a [[{{FULLPAGENAME}}/list|raw list]] of URLs that you can edit.

{| class="wikitable sortable plainlinks"
! rowspan=2 | Website !! rowspan=2 | [[ArchiveBot]] !! colspan=4 | Archive details
|-
! Domain !! Job !! Date !! Size %s
|}
""" % (len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{notsaved}}', rowsplain)), convertsize(b=totaljobsize), rowsplain)
        before = wtext.split('<!-- bot -->')[0]
        after = wtext.split('<!-- /bot -->')[1]
        newtext = '%s<!-- bot -->%s<!-- /bot -->%s' % (before, output, after)
        if wtext != newtext:
            pywikibot.showDiff(wtext, newtext)
            page.text = newtext
            page.save("BOT - Updating page: {{saved}} (%s), {{notsaved}} (%s), Total size (%s)" % (len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{notsaved}}', rowsplain)), convertsize(b=totaljobsize)))
        else:
            print("No changes needed in", page.title())

if __name__ == '__main__':
    main()
