#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2019 emijrp <emijrp@gmail.com>
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

import collections
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


Entry = collections.namedtuple('Entry', ('sorturl', 'url', 'label', 'line'))

truncationpattern = re.compile(r'^[^:/]+://(www\.)?')

def parselistline(line):
    label = None
    if '|' in line:
        url, label = line.split('|')[0:2]
        label = label.strip()
    else:
        url = line
    url = url.strip()
    if '://' in url and not '/' in url.split('://')[1]:
        url = url + '/'
    line = url + (' | ' + label if label else '')
    sorturl = truncationpattern.sub('', url).lower()
    for domain in ('transfer.sh', 'ix.io'):
        if domain == 'ix.io' and '+' not in sorturl:
            # Only apply this stripping to the undocumented trick URLs of format ix.io/code+/filename
            continue
        if sorturl.startswith(domain) and sum(x == '/' for x in sorturl) == 2:
            # For file hosting URLs that contain exactly two slashes, strip the first path component = the random file ID to sort by the filename instead.
            sorturl = domain + sorturl[sorturl.index('/', len(domain) + 1):]
    return Entry(sorturl = sorturl, url = url, label = label, line = line)

def curateurls(wlist=''):
    # Returns a dict of sectionname => list of URLs entries
    # sectionname is None for URLs outside of a section (i.e. on a page without section or before the first section).
    # A "URL entry" in the list is an Entry object (namedtuple); the label is None if it isn't present.

    lines = []
    currentsectionname = None
    currentsectionentries = []
    sectionentries = {}

    def endsection():
        nonlocal currentsectionentries, lines, sectionentries, currentsectionname
        currentsectionentries = list(set(currentsectionentries)) # Deduplicate
        currentsectionentries.sort(key = lambda x: (x.sorturl, x.label if x.label is not None else '', x.url, x.line))
        lines.extend(x.line for x in currentsectionentries)
        sectionentries[currentsectionname] = currentsectionentries
        currentsectionentries = []

    for line in wlist.text.strip().splitlines():
        if line.strip().startswith('='):
            # New section, sort and append previous section
            endsection()
            currentsectionname = line.strip().strip('=').strip()
            if currentsectionname in sectionentries:
                print('Warning: duplicate section name {!r} on page {}'.format(currentsectionname, wlist.title()))
            if lines:
                lines.append('')
            lines.append(line.strip())
        elif line.strip():
            currentsectionentries.append(parselistline(line))
    endsection()

    lines = '\n'.join(lines)
    if wlist.text != lines:
        wlist.text = lines
        wlist.save("BOT - Sorting list")

    return sectionentries


def main():
    atsite = pywikibot.Site('archiveteam', 'archiveteam')
    cat = pywikibot.Category(atsite, "Category:ArchiveBot")
    gen = pagegenerators.CategorizedPageGenerator(cat, start="!")
    pre = pagegenerators.PreloadingGenerator(gen, pageNumber=60)
    
    for page in pre:
        wtitle = page.title()
        wtext = page.text
        
        if len(sys.argv)>1 and not sys.argv[1] in wtitle:
            continue
        
        #if not wtitle.startswith('ArchiveBot/National Film'):
        if not wtitle.startswith('ArchiveBot/'):
            continue
        wlist = pywikibot.Page(atsite, '%s/list' % (wtitle))
        if not wlist.exists():
            print("Page %s/list doesnt exist" % (wtitle))
            continue
        sectionentries = curateurls(wlist=wlist)
        
        print('\n===', wtitle, '===')
        if (not '<!-- bot -->' in wtext and not '<!-- bot:' in wtext) or not '<!-- /bot -->' in wtext:
            print("No <!-- bot --> tag. Skiping...")
            continue

        newtext = []
        totaljobsize = 0
        totalsaved = 0
        totalnotsaved = 0

        # Find blocks of page text that end with a bot tag
        blocks = wtext.split('<!-- /bot -->')

        # The last block must be tag-free, so only iterate over the previous ones
        for block in blocks[:-1]:
            # Find beginning of bot tag
            pos = block.find('<!-- bot')
            if pos == -1:
                print('Block is missing opening tag, skipping...')
                newtext.append(block)
                newtext.append('<!-- /bot -->')
                continue

            if block[pos:].startswith('<!-- bot -->'):
                # Sectionless tag, use section None
                section = None
                openingtag = '<!-- bot -->'
            elif block[pos:].startswith('<!-- bot:'):
                # Extract section name
                openend = block.find('-->', pos)
                if openend == -1:
                    print("Block's opening tag does not have an end, skipping...")
                    newtext.append(block)
                    newtext.append('<!-- /bot -->')
                    continue
                section = block[pos + 9:openend].strip() # 9 = len('<!-- bot:')
                openingtag = block[pos:openend + 3]
            else:
                print('Block has an invalid bot tag, skipping...')
                newtext.append(block)
                newtext.append('<!-- /bot -->')
                continue

            if section not in sectionentries:
                print('Block references section {!r} which does not exist, skipping...'.format(section))
                newtext.append(block)
                newtext.append('<!-- /bot -->')
                continue

            # Add prefixed text (if any)
            newtext.append(block[:pos])

            # Add opening tag (as it was before)
            newtext.append(openingtag)

            # Generate table
            c = 1
            rowsplain = ""
            sectionjobsize = 0
            for entry in sectionentries[section]:
                viewerplain = ''
                viewerdetailsplain = ''
                viewer = [getArchiveBotViewer(url=entry.url)]
                if viewer[0][0]:
                    viewerplain = "[%s {{saved}}]" % (viewer[0][1])
                    viewerdetailsplain = viewer[0][2]
                    sectionjobsize += viewer[0][3]
                else:
                    viewerplain = "[%s {{notsaved}}]" % (viewer[0][1])
                    viewerdetailsplain = ''
                rowspan = len(re.findall(r'\|-', viewerdetailsplain))+1
                rowspanplain = 'rowspan=%d | ' % (rowspan) if rowspan>1 else ''
                if entry.label:
                    rowsplain += "\n|-\n| %s[%s %s] || %s%s\n%s " % (rowspanplain, entry.url, entry.label, rowspanplain, viewerplain, viewerdetailsplain if viewerdetailsplain else '|  ||  ||  || ')
                else:
                    rowsplain += "\n|-\n| %s%s || %s%s\n%s " % (rowspanplain, entry.url, rowspanplain, viewerplain, viewerdetailsplain if viewerdetailsplain else '|  ||  ||  || ')
                c += 1

            totaljobsize += sectionjobsize
            sectionsaved = rowsplain.count('{{saved}}')
            totalsaved += sectionsaved
            sectionnotsaved = rowsplain.count('{{notsaved}}')
            totalnotsaved += sectionnotsaved
            output = """
* '''Statistics''': {{saved}} (%s){{·}} {{notsaved}} (%s){{·}} Total size (%s)

Do not edit this table, it is automatically updated by bot. There is a [[{{FULLPAGENAME}}/list|raw list]] of URLs that you can edit.

{| class="wikitable sortable plainlinks"
! rowspan=2 | Website !! rowspan=2 | [[ArchiveBot]] !! colspan=4 | Archive details
|-
! Domain !! Job !! Date !! Size %s
|}
""" % (sectionsaved, sectionnotsaved, convertsize(b=sectionjobsize), rowsplain)
            newtext.append(output)

            newtext.append('<!-- /bot -->')

        # Add the last, tag-free block
        newtext.append(blocks[-1])

        newtext = ''.join(newtext)

        if wtext != newtext:
            pywikibot.showDiff(wtext, newtext)
            page.text = newtext
            try:
                page.save("BOT - Updating page: {{saved}} (%s), {{notsaved}} (%s), Total size (%s)" % (totalsaved, totalnotsaved, convertsize(b=totaljobsize)))
            except:
                print("Error while saving...")
        else:
            print("No changes needed in", page.title())

if __name__ == '__main__':
    main()
