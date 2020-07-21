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
import re
import os
import time
import internetarchive

from archiveteamfun import *

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
sisterprojects = {
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

def main():
    os.system('wget "https://www.wikidata.org/wiki/Special:SiteMatrix" -O sitematrix.html')
    raw = ''
    with open('sitematrix.html', 'r') as f:
        raw = f.read()
    
    for sisterproject in ['wiktionary', ]:
        wikilangs = re.findall(r'(?im)<td><a href="//([a-z]{2,3})\.%s\.org">\1</a>' % (sisterproject), raw)
        wikilangs = list(set(wikilangs))
        wikilangs.sort()
        
        for wikilang in wikilangs:
            if wikilang in langs.keys():
                langword = langs[wikilang]
            else:
                continue
            pagetitle = 'Main Page'
            pagetitle_ = re.sub(' ', '_', pagetitle)
            print('-'*30, '\n', wikilang, pagetitle)
            pdfurl = 'https://%s.%s.org/api/rest_v1/page/pdf/%s' % (wikilang, sisterproject, pagetitle_)
            dateiso = datetime.datetime.now().isoformat().split('T')[0]
            dateiso2 = re.sub('-', '', dateiso)
            pdfname = '%s%s-%s-%s.pdf' % (wikilang, sisterprojects[sisterproject], pagetitle_, dateiso2)
            itemid = pdfname
            
            itemurl = 'https://archive.org/details/' + itemid
            itemhtml = getURL(url=itemurl, retry=False)
            if itemhtml and not 'Item cannot be found' in itemhtml:
                print('Skiping. Item exists', itemurl)
                continue
            
            try:
                os.system('wget "%s" -O "%s"' % (pdfurl, pdfname))
                if os.path.exists(pdfname) and os.path.getsize(pdfname) < 1:
                    print("Error generating PDF")
                    continue
            except:
                print("Error generating PDF")
                continue
            
            md = {
                'mediatype': 'texts', 
                'licenseurl': 'https://creativecommons.org/licenses/by-sa/3.0/', 
                'language': langword, 
                'genre': genres[sisterproject], 
                'date': dateiso, 
                'year': dateiso[:4], 
                'description': '%s page.' % (sisterproject[0].upper()+sisterproject[1:]), 
                'subject': '%s; offline; pdf; page; mediawiki; %s; %s; %s' % (sisterproject.lower(), dateiso, wikilang, pagetitle), 
            }
            internetarchive.upload(itemid, pdfname, metadata=md)
            print('Uploaded to https://archive.org/details/%s' % (itemid))
            if pdfname and '.pdf' in pdfname and os.path.exists(pdfname):
                os.remove(pdfname)

if __name__ == '__main__':
    main()
