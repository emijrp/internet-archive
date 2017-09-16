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

from archive import *

def revistahistoriaelpuerto():
    statuses = []
    for i in range(1, 57):
        url = 'http://www.revistadehistoriade-elpuerto.org/contenido/atrasados/sumario_%d.htm' % (i)
        raw = getURL(url=url)
        urls = re.findall(r'href="\.\.(/revistas/[^<>" ]+?)"', raw)
        if not urls:
            break
        archiveurl(url=url)
        for url in urls:
            url = 'http://www.revistadehistoriade-elpuerto.org/contenido' + url
            status = archiveurl(url=url)
            statuses.append(status)
    stats(statuses=statuses)

def main():
    revistahistoriaelpuerto()

if __name__ == '__main__':
    main()
