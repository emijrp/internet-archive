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
import re
import sys
import time
import urllib.parse
import urllib.request
import pywikibot
import pywikibot.pagegenerators as pagegenerators

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
            maxsleep = 0
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

def cleanwiki(wtext):
    wtext = re.sub(r"(?im)<!--.*?-->", r"", wtext)
    wtext = re.sub(r"(?im)\[\[[^\[\]]+?\|([^\[\]]+?)\]\]", r"\1", wtext)
    wtext = re.sub(r"(?im)\[\[([^\[\]]+?)\]\]", r"\1", wtext)
    wtext = re.sub(r"(?im)<ref[^<>]*?>[^<>]*?</ref>", r"", wtext)
    wtext = re.sub(r"(?im)(<ref[^<>]*?>|</ref>)", r"", wtext)
    wtext = re.sub(r"(?im)\{\{[^\{\}]*?\}\}", r"", wtext)
    wtext = re.sub(r"(?im)\([\:\;\,\. ]*?\)", r"", wtext)
    wtext = re.sub(r"(?im)  *", r" ", wtext)
    wtext = re.sub(r"(?im)\'\'+", r"", wtext)
    return wtext

def getIntro(wtext, wtitle):
    intro = re.findall(r"(?im)(^[^=\n\r]*?\'\'%s\'\'[^\n\r]+)" % (wtitle), wtext)
    if intro:
        intro = intro[0]
    else:
        intro = ''
    return cleanwiki(intro)

def getArchiveBotViewer(url=''):
    if url and '//' in url:
        domain = url.split('//')[1].split('/')[0]
        viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
        raw = getURL(url=viewerurl)
        if raw and '</form>' in raw:
            raw = raw.split('</form>')[1]
        else:
            return False, viewerurl
        if re.search(r'No search results', raw):
            return False, viewerurl
        else:
            if len(url.split(domain)[1]) > 1: #domain.com/more
                if re.search(r'(?im)(%s)' % (url), raw):
                    return True, viewerurl
                else:
                    return False, viewerurl
            elif re.search(r'(?im)(%s)' % (domain), raw):
                return True, viewerurl
            else:
                return False, viewerurl
    else:
        return False, 'https://archive.fart.website/archivebot/viewer/'

def main():
    enwpsite = pywikibot.Site('en', 'wikipedia')
    atsite = pywikibot.Site('archiveteam', 'archiveteam')
    
    year1 = 2015 #datetime.datetime.now().year
    year2 = 2020
    if len(sys.argv) >= 2:
        year1 = int(sys.argv[1])
        year2 = int(sys.argv[2])
    
    start = ''
    years = range(year1, year2) 
    limit = 100
    
    for year in years:
        category = pywikibot.Category(enwpsite, "Category:%s disestablishments" % (year))
        gen = pagegenerators.CategorizedPageGenerator(category=category, start=start, namespaces=[0], recurse=2)
        pre = pagegenerators.PreloadingGenerator(gen, pageNumber=50)
        
        rows = []
        c = 0
        for page in pre:
            if not page.exists() or page.isRedirectPage():
                continue
            wtext = page.text
            wtitle = page.title()
            print('\n\n==', wtitle, '==\n')
            if not re.search(r'(?im)disestablishments', wtext):
                print("Not in disestablishments categories. Skiping...", wtitle)
                continue
            
            if 'Canton of' in wtitle:
                continue
            
            cats = re.findall(r'(?im)\[\[Category:([^\[\]]*?)\]\]', wtext)
            cats2 = []
            for cat in cats:
                if re.search(r'(?im)disestablishments', cat) and cat != "%s disestablishments" % (year):
                    cats2.append(cat)
            cats = cats2
            
            try:
                item = pywikibot.ItemPage.fromPage(page)
            except:
                continue
            q = str(item).split(':')[1].split(']')[0]
            print(wtitle, item)
            itemcontent = item.get()
            #print(itemcontent['descriptions'])
            intro = getIntro(wtext, wtitle)
            print(intro)
            
            p31 = ''
            if 'P31' in itemcontent['claims']:
                for instanceof in itemcontent['claims']['P31']:
                    p31item = instanceof.getTarget().get()
                    if 'en' in p31item['labels']:
                        print(p31item['labels']['en'])
                        p31 = p31item['labels']['en']
                        break
            
            websites = []
            viewer = []
            if 'P856' in itemcontent['claims']:
                for website in itemcontent['claims']['P856']:
                    web = website.getTarget()
                    print(web)
                    if re.search(r'(?im)(discount)', web):
                        print("Skiping url, word filter")
                        continue
                    websites.append(web)
                    viewer.append(getArchiveBotViewer(url=web))
            
            if not websites:
                continue
            
            rows.append([wtitle, q, p31, intro, cats, websites, viewer])
            c += 1
            if c >= limit:
                break
        
        c = 1
        rowsplain = ""
        for row in rows:
            wtitle, q, p31, intro, cats, websites, viewer = row
            viewerplain = []
            for v in viewer:
                if v[0]:
                    viewerplain.append("[%s {{saved}}]" % (v[1]))
                else:
                    viewerplain.append("[%s {{nosaved}}]" % (v[1]))
            viewerplain = '<br/>'.join(viewerplain)
            rowsplain += "\n|-\n| %s || '''[[:wikipedia:en:%s|%s]]'''<br/><small>([[:wikipedia:wikidata:%s|%s]])</small> || %s || %s%s || %s || %s " % (c, wtitle, wtitle, q, q, p31, intro, cats and "<br/><small>''%s''</small>" % (', '.join(cats)) or '', websites and '<br/>'.join(websites) or '-', viewerplain and viewerplain or '-')
            c += 1
        output = """This page is based on Wikipedia articles in '''[[:wikipedia:en:Category:%s disestablishments|Category:%s disestablishments]]'''. The websites for these entities could vanish in the foreseable future.

* '''Statistics''': {{saved}} (%s){{·}} {{nosaved}} (%s)

{| class="wikitable sortable"
! # !! Title !! Topic !! Description !! Website(s) !! width=100px | [[ArchiveBot]] %s
|}

{{disestablishments}}

[[Category:Archive Team]]""" % (year, year, len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{nosaved}}', rowsplain)), rowsplain)
        print(output)
        
        page = pywikibot.Page(atsite, "Disestablishments in %s" % (year))
        page.text = output
        page.save("BOT - Updating page: {{saved}} (%s), {{nosaved}} (%s)" % (len(re.findall(r'{{saved}}', rowsplain)), len(re.findall(r'{{nosaved}}', rowsplain))))

if __name__ == '__main__':
    main()

