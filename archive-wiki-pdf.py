#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 emijrp <emijrp@gmail.com>
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
import os
import time
import urllib.parse

import internetarchive

from archiveteamfun import *
from wikidatafun import *

#https://meta.wikimedia.org/wiki/List_of_Wikipedias
langs = {
    "ab": "Abkhazian", 
    "ace": "Acehnese", 
    "ady": "Adyghe", 
    "af": "Afrikaans", 
    "ak": "Akan", 
    "am": "Amharic", 
    "an": "Aragonese", 
    "ang": "Anglo-Saxon", 
    "ar": "Arabic", 
    "arc": "Aramaic", 
    "arz": "Egyptian Arabic", 
    "as": "Assamese", 
    "ast": "Asturian", 
    "atj": "Atikamekw", 
    "av": "Avar", 
    "ay": "Aymara", 
    "az": "Azerbaijani", 
    "azb": "South Azerbaijani", 
    "ba": "Bashkir", 
    "bar": "Bavarian", 
    "bcl": "Central Bicolano", 
    "be": "Belarusian", 
    "bg": "Bulgarian", 
    "bi": "Bislama", 
    "bjn": "Banjar", 
    "bm": "Bambara", 
    "bn": "Bengali", 
    "bo": "Tibetan", 
    "bpy": "Bishnupriya Manipuri", 
    "br": "Breton", 
    "bs": "Bosnian", 
    "bug": "Buginese", 
    "bxr": "Buryat", 
    "ca": "Catalan", 
    "cdo": "Min Dong", 
    "ce": "Chechen", 
    "ceb": "Cebuano", 
    "ch": "Chamorro", 
    "cho": "Choctaw", 
    "chr": "Cherokee", 
    "chy": "Cheyenne", 
    "ckb": "Sorani", 
    "co": "Corsican", 
    "cr": "Cree", 
    "crh": "Crimean Tatar", 
    "cs": "Czech", 
    "csb": "Kashubian", 
    "cu": "Old Church Slavonic", 
    "cv": "Chuvash", 
    "cy": "Welsh", 
    "da": "Danish", 
    "de": "German", 
    "din": "Dinka", 
    "diq": "Zazaki", 
    "dsb": "Lower Sorbian", 
    "dty": "Doteli", 
    "dv": "Divehi", 
    "dz": "Dzongkha", 
    "ee": "Ewe", 
    "el": "Greek", 
    "eml": "Emilian-Romagnol", 
    "en": "English", 
    "eo": "Esperanto", 
    "es": "Spanish", 
    "et": "Estonian", 
    "eu": "Basque", 
    "ext": "Extremaduran", 
    "fa": "Persian", 
    "ff": "Fula", 
    "fi": "Finnish", 
    "fj": "Fijian", 
    "fo": "Faroese", 
    "fr": "French", 
    "frp": "Franco-Provençal", 
    "frr": "North Frisian", 
    "fur": "Friulian", 
    "fy": "West Frisian", 
    "ga": "Irish", 
    "gag": "Gagauz", 
    "gan": "Gan", 
    "gd": "Scottish Gaelic", 
    "gl": "Galician", 
    "glk": "Gilaki", 
    "gn": "Guarani", 
    "gom": "Goan Konkani", 
    "gor": "Gorontalo", 
    "got": "Gothic", 
    "gu": "Gujarati", 
    "gv": "Manx", 
    "ha": "Hausa", 
    "hak": "Hakka", 
    "haw": "Hawaiian", 
    "he": "Hebrew", 
    "hi": "Hindi", 
    "hif": "Fiji Hindi", 
    "ho": "Hiri Motu", 
    "hr": "Croatian", 
    "hsb": "Upper Sorbian", 
    "ht": "Haitian", 
    "hu": "Hungarian", 
    "hy": "Armenian", 
    "ia": "Interlingua", 
    "id": "Indonesian", 
    "ie": "Interlingue", 
    "ig": "Igbo", 
    "ik": "Inupiak", 
    "ilo": "Ilokano", 
    "inh": "Ingush", 
    "io": "Ido", 
    "is": "Icelandic", 
    "it": "Italian", 
    "iu": "Inuktitut", 
    "ja": "Japanese", 
    "jam": "Jamaican Patois", 
    "jbo": "Lojban", 
    "jv": "Javanese", 
    "ka": "Georgian", 
    "kaa": "Karakalpak", 
    "kab": "Kabyle", 
    "kbd": "Kabardian Circassian", 
    "kbp": "Kabiye", 
    "kg": "Kongo", 
    "ki": "Kikuyu", 
    "kj": "Kuanyama", 
    "kk": "Kazakh", 
    "kl": "Greenlandic", 
    "km": "Khmer", 
    "kn": "Kannada", 
    "ko": "Korean", 
    "koi": "Komi-Permyak", 
    "kr": "Kanuri", 
    "krc": "Karachay-Balkar", 
    "ks": "Kashmiri", 
    "ksh": "Ripuarian", 
    "ku": "Kurdish", 
    "kv": "Komi", 
    "kw": "Cornish", 
    "ky": "Kirghiz", 
    "la": "Latin", 
    "lad": "Ladino", 
    "lb": "Luxembourgish", 
    "lbe": "Lak", 
    "lez": "Lezgian", 
    "lfn": "Lingua Franca Nova", 
    "lg": "Luganda", 
    "li": "Limburgish", 
    "lij": "Ligurian", 
    "lmo": "Lombard", 
    "ln": "Lingala", 
    "lo": "Lao", 
    "lrc": "Northern Luri", 
    "lt": "Lithuanian", 
    "ltg": "Latgalian", 
    "lv": "Latvian", 
    "mai": "Maithili", 
    "mdf": "Moksha", 
    "mg": "Malagasy", 
    "mh": "Marshallese", 
    "mhr": "Meadow Mari", 
    "mi": "Maori", 
    "min": "Minangkabau", 
    "mk": "Macedonian", 
    "ml": "Malayalam", 
    "mn": "Mongolian", 
    "mr": "Marathi", 
    "mrj": "Hill Mari", 
    "ms": "Malay", 
    "mt": "Maltese", 
    "mus": "Muscogee", 
    "mwl": "Mirandese", 
    "my": "Burmese", 
    "myv": "Erzya", 
    "mzn": "Mazandarani", 
    "na": "Nauruan", 
    "nah": "Nahuatl", 
    "nap": "Neapolitan", 
    "nds": "Low Saxon", 
    "ne": "Nepali", 
    "new": "Newar", 
    "ng": "Ndonga", 
    "nl": "Dutch", 
    "nn": "Norwegian (Nynorsk)", 
    "no": "Norwegian (Bokmål)", 
    "nov": "Novial", 
    "nrm": "Norman", 
    "nso": "Northern Sotho", 
    "nv": "Navajo", 
    "ny": "Chichewa", 
    "oc": "Occitan", 
    "olo": "Livvi-Karelian", 
    "om": "Oromo", 
    "or": "Oriya", 
    "os": "Ossetian", 
    "pa": "Punjabi", 
    "pag": "Pangasinan", 
    "pam": "Kapampangan", 
    "pap": "Papiamentu", 
    "pcd": "Picard", 
    "pdc": "Pennsylvania German", 
    "pfl": "Palatinate German", 
    "pi": "Pali", 
    "pih": "Norfolk", 
    "pl": "Polish", 
    "pms": "Piedmontese", 
    "pnb": "Western Punjabi", 
    "pnt": "Pontic", 
    "ps": "Pashto", 
    "pt": "Portuguese", 
    "qu": "Quechua", 
    "rm": "Romansh", 
    "rmy": "Romani", 
    "rn": "Kirundi", 
    "ro": "Romanian", 
    "ru": "Russian", 
    "rue": "Rusyn", 
    "rw": "Kinyarwanda", 
    "sa": "Sanskrit", 
    "sah": "Sakha", 
    "sat": "Santali", 
    "sc": "Sardinian", 
    "scn": "Sicilian", 
    "sco": "Scots", 
    "sd": "Sindhi", 
    "se": "Northern Sami", 
    "sg": "Sango", 
    "sh": "Serbo-Croatian", 
    "shn": "Shan", 
    "si": "Sinhalese", 
    "sk": "Slovak", 
    "sl": "Slovenian", 
    "sm": "Samoan", 
    "sn": "Shona", 
    "so": "Somali", 
    "sq": "Albanian", 
    "sr": "Serbian", 
    "srn": "Sranan", 
    "ss": "Swati", 
    "st": "Sesotho", 
    "stq": "Saterland Frisian", 
    "su": "Sundanese", 
    "sv": "Swedish", 
    "sw": "Swahili", 
    "szl": "Silesian", 
    "ta": "Tamil", 
    "tcy": "Tulu", 
    "te": "Telugu", 
    "tet": "Tetum", 
    "tg": "Tajik", 
    "th": "Thai", 
    "ti": "Tigrinya", 
    "tk": "Turkmen", 
    "tl": "Tagalog", 
    "tn": "Tswana", 
    "to": "Tongan", 
    "tpi": "Tok Pisin", 
    "tr": "Turkish", 
    "ts": "Tsonga", 
    "tt": "Tatar", 
    "tum": "Tumbuka", 
    "tw": "Twi", 
    "ty": "Tahitian", 
    "tyv": "Tuvan", 
    "udm": "Udmurt", 
    "ug": "Uyghur", 
    "uk": "Ukrainian", 
    "ur": "Urdu", 
    "uz": "Uzbek", 
    "ve": "Venda", 
    "vec": "Venetian", 
    "vep": "Vepsian", 
    "vi": "Vietnamese", 
    "vls": "West Flemish", 
    "vo": "Volapük", 
    "wa": "Walloon", 
    "war": "Waray-Waray", 
    "wo": "Wolof", 
    "wuu": "Wu", 
    "xal": "Kalmyk", 
    "xh": "Xhosa", 
    "xmf": "Mingrelian", 
    "yi": "Yiddish", 
    "yo": "Yoruba", 
    "za": "Zhuang", 
    "zea": "Zeelandic", 
    "zh": "Chinese", 
    "zu": "Zulu", 
}
genres = {
    "wikibooks": "Course", 
    "wikinews": "News", 
    "wikipedia": "Encyclopedia", 
    "wikiquote": "Quotes", 
    "wikisource": "Literature", 
    #"wikispecies": "Encyclopedia", 
    "wikiversity": "Course", 
    "wikivoyage": "Travel", 
    "wiktionary": "Dictionary", 
}
projects = {
    "wikibooks": "wikibooks", 
    "wikinews": "wikinews", 
    "wikipedia": "wiki", 
    "wikiquote": "wikiquote", 
    "wikisource": "wikisource", 
    #"wikispecies": "wikispecies", 
    "wikiversity": "wikiversity", 
    "wikivoyage": "wikivoyage", 
    "wiktionary": "wiktionary", 
}

def archivefromwikidatasparql(sparql='', project='wikipedia'):
    if not sparql:
        return
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql?query=%s' % (urllib.parse.quote(sparql))
    url = '%s&format=json' % (url)
    print("Loading...", url)
    sparql = getURL(url=url)
    json1 = loadSPARQL(sparql=sparql)
    for result in json1['results']['bindings']:
        q = 'item' in result and result['item']['value'].split('/entity/')[1] or ''
        if not q:
            break
        archivefromwikidata(q=q, project='wikipedia')

def archivefromwikidata(q='', project='wikipedia'):
    if not re.search(r'(?m)^Q\d+$', q):
        print("Error in Q", q)
        return
    qfile =  '%s.json' % (q)
    os.system('wget "https://www.wikidata.org/wiki/Special:EntityData/%s.json" -O %s' % (q, qfile))
    qjson = {}
    with open(qfile, 'r') as f:
        jsonraw = f.read()
        qjson = json.loads(jsonraw)
    print(len(qjson['entities'][q]['sitelinks'].keys()))
    sitelinks = list(qjson['entities'][q]['sitelinks'].keys())
    sitelinks.sort()
    for sitelink in sitelinks:
        if project:
            m = re.findall(r'(?im)^([a-z]{2,3})%s$' % (projects[project]), sitelink)
            wikilang = m and m[0] or ''
            if not wikilang or wikilang not in langs.keys():
                continue
        else:
            continue
        #print(wikilang, project)
        archivewikipdf(wikilang=wikilang, project=project, pagetitle=qjson['entities'][q]['sitelinks'][sitelink]['title'])
    
    if os.path.exists(qfile):
        os.remove(qfile)

def archivewikipdf(wikilang='', project='', pagetitle=''):
    if re.search(r'(?im)[^a-z0-9_ ]', pagetitle):
        print('-'*30)
        print("Error unsupported title", pagetitle)
        return
    
    langword = ''
    if wikilang in langs.keys():
        langword = langs[wikilang]
    else:
        print("Error unknown lang", wikilang)
        return
    projectucfirst = project[0].upper()+project[1:]
    pagetitle_ = re.sub(' ', '_', pagetitle)
    print('\n', '-'*30, '\n', wikilang, pagetitle)
    pdfurl = 'https://%s.%s.org/api/rest_v1/page/pdf/%s' % (wikilang, project, pagetitle_)
    dateiso = datetime.datetime.now().isoformat().split('T')[0]
    dateiso2 = re.sub('-', '', dateiso)
    pdfname = '%s%s-%s-%s.pdf' % (wikilang, projects[project], pagetitle_, dateiso2)
    originalurl = 'https://%s.%s.org/wiki/%s' % (wikilang, project, pagetitle_)
    itemid = pdfname
    itemurl = 'https://archive.org/details/' + itemid
    itemhtml = getURL(url=itemurl, retry=False)
    if itemhtml and not 'Item cannot be found' in itemhtml:
        print('Skiping. Item exists', itemurl)
        return
    
    try:
        os.system('wget "%s" -O "%s"' % (pdfurl, pdfname))
        if os.path.exists(pdfname) and os.path.getsize(pdfname) < 1:
            print("Error generating PDF")
            os.remove(pdfname)
            return
    except:
        print("Error generating PDF")
        return
    
    md = {
        'mediatype': 'texts', 
        'creator': projectucfirst,
        'licenseurl': 'https://creativecommons.org/licenses/by-sa/3.0/', 
        'language': langword, 
        'genre': genres[project], 
        'date': dateiso, 
        'year': dateiso[:4], 
        'description': '%s page.' % (projectucfirst), 
        'subject': '%s; offline; pdf; page; mediawiki; %s; %s; %s; %s%s; %s' % (project.lower(), dateiso, wikilang, langword, wikilang, projects[project], pagetitle), 
        'originalurl': originalurl, 
    }
    try:
        internetarchive.upload(itemid, pdfname, metadata=md)
        print('Uploaded to https://archive.org/details/%s' % (itemid))
    except:
        print("Error uploading file to", itemid)
    
    if pdfname and '.pdf' in pdfname and os.path.exists(pdfname):
        os.remove(pdfname)

def main():
    """os.system('wget "https://www.wikidata.org/wiki/Special:SiteMatrix" -O sitematrix.html')
    raw = ''
    with open('sitematrix.html', 'r') as f:
        raw = f.read()
    
    for project in ['wiktionary', ]:
        projectucfirst = project[0].upper()+project[1:]
        wikilangs = re.findall(r'(?im)<td><a href="//([a-z]{2,3})\.%s\.org">\1</a>' % (project), raw)
        wikilangs = list(set(wikilangs))
        wikilangs.sort()
    """
    """
    archivewikipdf(wikilang='en', project='wikipedia', pagetitle='Earth')
    archivewikipdf(wikilang='nn', project='wikipedia', pagetitle='Jorda')
    archivewikipdf(wikilang='ab', project='wikipedia', pagetitle='Адгьыл')
    archivewikipdf(wikilang='he', project='wikipedia', pagetitle='כדור הארץ')
    archivewikipdf(wikilang='zh', project='wikipedia', pagetitle='地球')
    """
    
    """
    #archivefromwikidata(q='Q2', project='wikipedia') #earth
    archivefromwikidata(q='Q1', project='wikipedia') #universe
    archivefromwikidata(q='Q167', project='wikipedia') #pi
    
    #Vital 1
    archivefromwikidata(q='Q2', project='wikipedia') #earth
    archivefromwikidata(q='Q5', project='wikipedia') #human
    archivefromwikidata(q='Q200325', project='wikipedia') #human history
    archivefromwikidata(q='Q315', project='wikipedia') #language
    archivefromwikidata(q='Q3', project='wikipedia') #life
    archivefromwikidata(q='Q395', project='wikipedia') #mathematics
    archivefromwikidata(q='Q5891', project='wikipedia') #philosophy
    archivefromwikidata(q='Q336', project='wikipedia') #science
    archivefromwikidata(q='Q11016', project='wikipedia') #technology
    archivefromwikidata(q='Q2018526', project='wikipedia') #arts
    """
    
    """
    #other
    archivefromwikidata(q='Q309', project='wikipedia') #history
    archivefromwikidata(q='Q11756', project='wikipedia') #prehistory
    archivefromwikidata(q='Q15', project='wikipedia') #africa
    archivefromwikidata(q='Q48', project='wikipedia') #asia
    archivefromwikidata(q='Q46', project='wikipedia') #europe
    archivefromwikidata(q='Q49', project='wikipedia') #north america
    archivefromwikidata(q='Q18', project='wikipedia') #south america
    archivefromwikidata(q='Q538', project='wikipedia') #oceania
    """
    """
    #more
    for year in range(1001, 2040):
        archivewikipdf(wikilang='en', project='wikipedia', pagetitle='%s' % (year))
    
    archivefromwikidata(q='Q48584', project='wikipedia') #rosetta stone
    """
    #ideas
    #idiomas
    sparql = """
    SELECT ?item
    WHERE {
      ?item wdt:P31 wd:Q34770.
      ?item wikibase:sitelinks ?sitelinks.
    }
    ORDER BY DESC(?sitelinks) LIMIT 1000
    """
    archivefromwikidatasparql(sparql=sparql, project='wikipedia')

if __name__ == '__main__':
    main()
