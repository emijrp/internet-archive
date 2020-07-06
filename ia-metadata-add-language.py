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

import time
import internetarchive

def main():
    #https://meta.wikimedia.org/wiki/List_of_Wikipedias
    langs = {
        'ca': 'Catalan', 
        'de': 'German', 
        'en': 'English', 
        'es': 'Spanish', 
        #'fr': 'French', 
        'hu': 'Hungarian', 
        'it': 'Italian', 
        'ja': 'Japanese', 
        'ko': 'Korean', 
        'nl': 'Dutch', 
        'pl': 'Polish', 
        'pt': 'Portuguese', 
        'ru': 'Russian', 
        'sv': 'Swedish', 
        'vi': 'Vietnamese', 
    }
    for langid, langword in langs.items():
        #https://archive.org/services/docs/api/internetarchive/quickstart.html#searching
        for i in internetarchive.search_items('subject:"kiwix" AND subject:"zim" AND subject:"%s"' % (langid)):
            itemid = i['identifier']
            print(itemid)
            if '_%s_' % (langid) in itemid:
                r = internetarchive.modify_metadata(itemid, metadata=dict(language=langword))
                if r.status_code == 200:
                    print('Language added: %s' % (langword))
                else:
                    print('Error (%s) adding language: %s' % (r.status_code, langword))
            else:
                print('Unknown language')

if __name__ == '__main__':
    main()
