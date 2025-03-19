#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2025 emijrp <emijrp@gmail.com>
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
	lang2name = {
		"ar": "Arabic", 
		"arz": "Egyptian Arabic", 
		"ca": "Catalan", 
		"ceb": "Cebuano", 
		"de": "German", 
		"en": "English", 
		"es": "Spanish", 
		"fa": "Persian", 
		"fr": "French", 
		"it": "Italian", 
		"ja": "Japanese", 
		"nl": "Dutch", 
		"pl": "Polish", 
		"pt": "Portuguese", 
		"ru": "Russian", 
		"sv": "Swedish", 
		"uk": "Ukrainian", 
		"vi": "Vietnamese", 
		"war": "Waray", 
		"zh": "Chinese", 
	}
	sisterprojects = [
		"Wiktionary", 
		"Wikipedia", 
	]
	topics = {
		"Wiktionary": { "singular": "Dictionary", "plural": "Dictionaries" }, 
		"Wikipedia": { "singular": "Encyclopedia", "plural": "Encyclopedias" }, 
	}
	fandomsite = pywikibot.Site('wikiteam.fandom.com', 'wikiteam.fandom.com')
	
	for sisterproject in sisterprojects:
		for lang in lang2name.keys():
			wiki = "%swiki" % (lang)
			if sisterproject != "Wikipedia":
				wiki = "%s%s" % (lang, sisterproject.lower())
			commonstab = getURL(url="https://commons.wikimedia.org/w/index.php?title=Data:Wikipedia_statistics/data.tab&action=raw")
			commonstab = json.loads(commonstab)
			#print(commonstab["data"])
			projectstats = []
			for project in commonstab["data"]:
				if project[0] == "%s.%s" % (lang, sisterproject.lower()):
					projectstats = project
			
			if not projectstats:
				print("No project stats for", wiki)
				continue
			
			#jsonurl = "https://archive.org/advancedsearch.php?q=%28subject%3Aspecieswiki+AND+-subject%3Aincremental%29+OR+%28subject%3Akiwix+AND+subject%3Awikispecies%29&fl%5B%5D=date&fl%5B%5D=identifier&fl%5B%5D=item_size&fl%5B%5D=title&sort%5B%5D=&sort%5B%5D=&sort%5B%5D=&rows=5000&page=1&output=json"
			#jsonurl = "https://archive.org/advancedsearch.php?q=%28subject%3Afrwiki+subject%3Awikipedia+-subject%3Aincremental+-subject%3Apdf%29+OR+%28subject%3Afr+subject%3Awikipedia+subject%3Azim%29&fl%5B%5D=date&fl%5B%5D=identifier&fl%5B%5D=item_size&fl%5B%5D=title&sort%5B%5D=&sort%5B%5D=&sort%5B%5D=&rows=5000&page=1&output=json"
			
			jsonurl = "https://archive.org/advancedsearch.php?q=%28subject%3A"+wiki+"+subject%3A"+sisterproject.lower()+"+-subject%3Aincremental+-subject%3Apdf%29+OR+%28subject%3A"+lang+"+subject%3A"+sisterproject.lower()+"+subject%3Azim%29&fl%5B%5D=date&fl%5B%5D=identifier&fl%5B%5D=item_size&fl%5B%5D=title&sort%5B%5D=&sort%5B%5D=&sort%5B%5D=&rows=50000&page=1&output=json"
			
			jsonraw = getURL(url=jsonurl)
			json1 = json.loads(jsonraw)
			
			itemrows = { "ZIM": [], "HTML": [], "Database": [] }
			totalsize = { "ZIM": 0, "HTML": 0, "Database": 0 }
			years = []
			for item in json1["response"]["docs"]:
				date = "date" in item and item["date"].split("T")[0] or ""
				if not date:
					m = re.findall(r"(20\d\d-?\d?\d-?\d?\d?)", item["identifier"])
					if m:
						date = m[0]
				if date:
					years.append(date[:4])
					years = list(set(years))
				dumptype = "Unknown"
				if re.search(r"(?im)zim", item["identifier"]+" "+item["title"]):
					dumptype = "ZIM"
				elif re.search(r"(?im)database", item["identifier"]+" "+item["title"]):
					dumptype = "Database"
				elif re.search(r"(?im)html", item["identifier"]+" "+item["title"]):
					dumptype = "HTML"
				if dumptype == "ZIM":
					dumpsubtype = "nopic" in item["identifier"] and "No images/videos" or "Images & videos"
					dumpsubtype = "novid" in item["identifier"] and "No videos" or dumpsubtype
					dumpsubtype2 = "_all_" in item["identifier"] and "All articles" or "All"
					dumpsubtype2 = "_" in item["identifier"] and item["identifier"].split("_")[2] or dumpsubtype2
					dumpsubtype2 = dumpsubtype2[0].upper() + dumpsubtype2[1:]
					line = "| [https://archive.org/details/%s %s] || %s || %s || %s || data-sort-value=%s | %s" % (item["identifier"], item["identifier"], date, dumpsubtype, dumpsubtype2, item["item_size"], convertsize(b=item["item_size"]))
				else:
					line = "| [https://archive.org/details/%s %s] || %s || data-sort-value=%s | %s" % (item["identifier"], item["identifier"], date, item["item_size"], convertsize(b=item["item_size"]))
				if dumptype in itemrows.keys():
					itemrow = [date, item["identifier"], item["item_size"], line]
					itemrows[dumptype].append(itemrow)
					totalsize[dumptype] += item["item_size"]
			
			years.sort()
			
			newtext = """The '''%s %s''' is the [[:Category:%s-language wikis|%s-language]] edition of [[:Category:%s|%s]], a free online [[:Category:%s|%s]].

As of {{subst:CURRENTYEAR}}, it has {{formatnum:%d}} articles ({{formatnum:%d}} pages) and {{formatnum:%d}} active users ({{formatnum:%d}} registered users).<ref>[https://%s.%s.org/wiki/Special:Statistics Special:Statistics]</ref>

== Archive ==

The following dumps from different dates and in several formats are available at Internet Archive.

{|
| valign=top | 
""" % (lang2name[lang], sisterproject, lang2name[lang], lang2name[lang], sisterproject, sisterproject, topics[sisterproject]["plural"], topics[sisterproject]["singular"].lower(), projectstats[3], projectstats[6], projectstats[1], projectstats[7], lang, sisterproject.lower())
			
			for dumptype in ["HTML", "Database", "ZIM"]:
				itemrows[dumptype].sort()
				if dumptype == "ZIM":
					newtext += """
| valign=top | 
"""
					newtext += """
{| class="wikitable sortable plainlinks" style="text-align: center;"
! %s dump !! Date !! Content !! Topic !! Size
|-
%s
|-
! colspan=4 | Total size !! %s
|}""" % (dumptype, "\n|-\n".join([line for x,y,z,line in itemrows[dumptype]]), convertsize(b=totalsize[dumptype]))
				else:
					newtext += """
{| class="wikitable sortable plainlinks" style="text-align: center;"
! %s dump !! Date !! Size
|-
%s
|-
! colspan=2 | Total size !! %s
|}""" % (dumptype, "\n|-\n".join([line for x,y,z,line in itemrows[dumptype]]), convertsize(b=totalsize[dumptype]))
			newtext += """
|}

== References ==
{{reflist}}

== External links ==
* https://%s.%s.org/

[[Category:All wikis]]
[[Category:%s]]
[[Category:%s-language wikis|%s]]""" % (lang, sisterproject.lower(), sisterproject, lang2name[lang], sisterproject)
			print(newtext)
			page = pywikibot.Page(fandomsite, "%s %s" % (lang2name[lang], sisterproject))
			if not page.exists() or (page.exists() and newtext.strip() != page.text.strip()):
				page.text = newtext
				page.save("BOT - Updating page")
				time.sleep(5)
			redpage = pywikibot.Page(fandomsite, "%s.%s.org" % (lang, sisterproject.lower()))
			if not redpage.exists():
				redpage.text = "#REDIRECT [[%s %s]]" % (lang2name[lang], sisterproject)
				redpage.save("BOT - Creating redirect")
				time.sleep(5)
			catlang = pywikibot.Page(fandomsite, "Category:%s-language wikis" % (lang2name[lang]))
			if not catlang.exists():
				catlang.text = "[[Category:Wikis by language|%s]]" % (lang2name[lang])
				catlang.save("BOT - Creating category")
				time.sleep(5)

if __name__ == '__main__':
	main()
