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

import re
import internetarchive

def main():
    for i in internetarchive.search_items('subject:"kiwix" AND subject:"zim"').iter_as_items():
        try:
            itemid = i.item_metadata['metadata']['identifier']
            print(itemid)
        except:
            print('Error in', i)
            continue
        
        if not 'date' in i.item_metadata['metadata']:
            date = re.findall(r'(?im)_(20\d\d-\d\d)\.zim', itemid)
            if date and len(date[0]) == 7:
                date = date[0]
            else:
                print('Error in date')
                continue
            r = internetarchive.modify_metadata(itemid, metadata=dict(date=date))
            if r.status_code == 200:
                print('Date added: %s' % (date))
            else:
                print('Error (%s) adding date: %s' % (r.status_code, date))
        else:
            print('Already has date: %s' % (i.item_metadata['metadata']['date']))
        
        if not 'year' in i.item_metadata['metadata']:
            year = re.findall(r'(?im)_(20\d\d)-\d\d\.zim', itemid)
            if year and len(year[0]) == 4:
                year = year[0]
            else:
                print('Error in year')
                continue
            r = internetarchive.modify_metadata(itemid, metadata=dict(year=year))
            if r.status_code == 200:
                print('Year added: %s' % (year))
            else:
                print('Error (%s) adding year: %s' % (r.status_code, year))
        else:
            print('Already has year: %s' % (i.item_metadata['metadata']['year']))

if __name__ == '__main__':
    main()
