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
        
        if not wtitle.startswith('ArchiveBot/'):
            continue
        wlist = pywikibot.Page(atsite, '%s/list' % (wtitle))
        if not wlist.exists():
            print("Page %s/list doesnt exist" % (wtitle))
            continue
        raw = wlist.text.strip().splitlines()
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
            viewer = [getArchiveBotViewer(url=website)]
            viewerplain = []
            viewerdetailsplain = []
            for v in viewer:
                if v[0]:
                    viewerplain.append("[%s {{saved}}]" % (v[1]))
                    viewerdetailsplain.append(v[2])
                else:
                    viewerplain.append("[%s {{nosaved}}]" % (v[1]))
                totaljobsize += v[3]
            viewerplain = '<br/>'.join(viewerplain)
            viewerdetailsplain = '<br/>'.join(viewerdetailsplain)
            
            rowsplain += "\n|-\n| %s || %s || %s " % (website, viewerplain and viewerplain or '-', viewerdetailsplain and viewerdetailsplain or '-')
            c += 1
        
        output = """
* '''Statistics''': {{saved}} (%s){{·}} {{nosaved}} (%s){{·}} Total size (%0.1d&nbsp;MB)

Do not edit this table, it is automatically updated by bot. There is a [[{{FULLPAGENAME}}/list|raw list]] of URLs that you can edit.

{| class="wikitable sortable plainlinks"
! width=150px | Website !! [[ArchiveBot]] !! Archive details %s
|}
""" % (len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{nosaved}}', rowsplain)), totaljobsize/(1024.0*1024), rowsplain)
        before = wtext.split('<!-- bot -->')[0]
        after = wtext.split('<!-- /bot -->')[1]
        newtext = '%s<!-- bot -->%s<!-- /bot -->%s' % (before, output, after)
        if wtext != newtext:
            pywikibot.showDiff(wtext, newtext)
            page.text = newtext
            page.save("BOT - Updating page: {{saved}} (%s), {{nosaved}} (%s), Total size (%0.1d MB)" % (len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{nosaved}}', rowsplain)), totaljobsize/(1024.0*1024)))
        else:
            print("No changes needed in", page.title())
    

if __name__ == '__main__':
    main()
