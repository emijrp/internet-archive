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
    
    enwppage = pywikibot.Page(enwpsite, "List of current heads of state and government")
    people = re.findall(r"\[\[([^\[\]]+?)(\|[^\[\]]+?)?]]&nbsp;–\s*\[\[([^\[\|]+?)[\|\]]", enwppage.text)
    weblist = []
    facebooklist = []
    instagramlist = []
    twitterlist = []
    c = 0
    rows = []
    for person in people:
        personart = person[2]
        personpos = person[1].strip('|')
        personcountry = 'Other'
        if ' of ' in person[0]:
            personcountry = person[0].split(' of ')[1]
            personcountry = re.sub(r'(?im) *the ', '', personcountry)
        else:
            personcountry = 'Other'
        if personcountry:
            if personcountry[0] == personcountry[0].lower():
                personcountry = 'Other'
        personpage = pywikibot.Page(enwpsite, personart)
        if not personpage.exists() or personpage.isRedirectPage():
            continue
        print('\n\n==', personart, '==\n')
        print(personcountry, personpos)
        try:
            item = pywikibot.ItemPage.fromPage(personpage)
        except:
            continue
        q = str(item).split(':')[1].split(']')[0]
        print(item)
        itemcontent = item.get()
        #print(itemcontent['descriptions'])
        
        webs = []
        if 'P856' in itemcontent['claims']:
            for website in itemcontent['claims']['P856']:
                web = website.getTarget()
                if web:
                    #https://www.archiveteam.org/index.php?title=MediaWiki:Spam-blacklist
                    if re.search(r'(?im)(discount|loan|money)', web):
                        print("Skiping url, word in spam filter")
                        continue
                    if not web in weblist:
                        print(web)
                        webs.append(web)
                        weblist.append(web)
        
        tws = []
        if 'P2002' in itemcontent['claims']:
            for twitter in itemcontent['claims']['P2002']:
                tw = twitter.getTarget()
                if tw:
                    if not tw in twitterlist:
                        print(tw)
                        tws.append(tw)
                        twitterlist.append(tw)
        
        fbs = []
        if 'P2013' in itemcontent['claims']:
            for facebook in itemcontent['claims']['P2013']:
                fb = facebook.getTarget()
                if fb:
                    if not fb in facebooklist:
                        print(fb)
                        fbs.append(fb)
                        facebooklist.append(fb)
        
        instas = []
        if 'P2003' in itemcontent['claims']:
            for instagram in itemcontent['claims']['P2003']:
                insta = instagram.getTarget()
                if insta:
                    if not insta in instagramlist:
                        print(insta)
                        instas.append(insta)
                        instagramlist.append(insta)
        
        if webs or fbs or instas or tws:
            row = "| '''%s''' || %s || '''[[:wikipedia:d:%s|%s]]''' || %s || %s || %s || %s\n|-" % (personcountry, personpos, q, personart, '<br/>'.join(webs), '<br/>'.join(['[https://www.facebook.com/%s %s]' % (x, x) for x in fbs]), '<br/>'.join(['[https://www.instagram.com/%s/ %s]' % (x, x) for x in instas]), '<br/>'.join(['[https://twitter.com/%s %s]' % (x, x) for x in tws]))
            rows.append(row)
            print(row)
        
        c += 1
        if c >= 1000:
            break
    
    rows.sort()
    rowsplain = '\n'.join(rows)
    output = """This page is based on Wikipedia article '''[[:wikipedia:en:List of current heads of state and government|List of current heads of state and government]]'''.

Do not edit this page, it is automatically updated by bot. There are raw lists for: [https://www.archiveteam.org/index.php?title={{FULLPAGENAMEE}}/websites-list&action=raw Websites], [https://www.archiveteam.org/index.php?title={{FULLPAGENAMEE}}/facebook-list&action=raw Facebook], [https://www.archiveteam.org/index.php?title={{FULLPAGENAMEE}}/instagram-list&action=raw Instagram], [https://www.archiveteam.org/index.php?title={{FULLPAGENAMEE}}/twitter-list&action=raw Twitter].

{| class="wikitable sortable plainlinks"
! Country !! Position !! Name !! Website(s) !! Facebook !! Instagram !! Twitter
|-
%s
|}

[[Category:Archive Team]]
[[Category:Lists]]""" % (rowsplain)
    print(output)
    
    atpage = pywikibot.Page(atsite, "List of current heads of state and government")
    if atpage.text != output:
        pywikibot.showDiff(atpage.text, output)
        atpage.text = output
        atpage.save("BOT - Updating page")
    else:
        print("No changes needed in", atpage.title())
    
    lists = [
        ["websites-list", weblist], 
        ["facebook-list", facebooklist], 
        ["instagram-list", instagramlist], 
        ["twitter-list", twitterlist], 
    ]
    for lname, llist in lists:
        llist.sort()
        if lname == "facebook-list":
            outputlist = '\n'.join(["https://www.facebook.com/%s" % (x) for x in llist])
        elif lname == "instagram-list":
            outputlist = '\n'.join(["https://www.instagram.com/%s/" % (x) for x in llist])
        elif lname == "twitter-list":
            outputlist = '\n'.join(["https://twitter.com/%s" % (x) for x in llist])
        else:
            outputlist = '\n'.join(llist)
        pagelist = pywikibot.Page(atsite, "List of current heads of state and government/%s" % (lname))
        if pagelist.text != outputlist:
            pywikibot.showDiff(pagelist.text, outputlist)
            pagelist.text = outputlist
            pagelist.save("BOT - Updating list")
        else:
            print("No changes needed in", pagelist.title())

if __name__ == '__main__':
    main()

