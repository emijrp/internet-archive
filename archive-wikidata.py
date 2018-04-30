#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
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

import sys
from archive import *

def main():
    statuses = []
    start = int(sys.argv[1])
    for i in range(start, 40000000):
        url = 'https://www.wikidata.org/wiki/Q' + str(i)
        if i % 10000 == 0:
            statuses = []
        status = archiveurl(url=url, force=True)
        statuses.append(status)
        if i % 100 == 0:
            stats(statuses=statuses)
    stats(statuses=statuses)

if __name__ == '__main__':
    main()
