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

import os
import re
import sys
import time

def main():
    feeds = [
        'https://www.archiveteam.org/index.php?title=List_of_current_heads_of_state_and_government/websites-list&action=raw', 
        'https://www.archiveteam.org/index.php?title=List_of_current_heads_of_state_and_government/facebook-list&action=raw', 
        'https://www.archiveteam.org/index.php?title=List_of_current_heads_of_state_and_government/instagram-list&action=raw', 
        'https://www.archiveteam.org/index.php?title=List_of_current_heads_of_state_and_government/twitter-list&action=raw', 
    ]
    tmpfile = "archive-social.tmp"
    for feed in feeds:
        os.system("curl '%s' > %s" % (feed, tmpfile))
        badfile = False
        with open(tmpfile, 'r') as f:
            for l in f.read().strip().splitlines():
                if not l.startswith('http'):
                    badfile = True
        if badfile:
            print("Error in feed, skiping...")
            continue
        os.system("python3 archive.py %s force" % (tmpfile))

if __name__ == '__main__':
    main()
