#!/usr/bin/env python3
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

import json
import os
import re
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
    try:
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        sleep = 10 # seconds
        maxsleep = 30
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

def loadSPARQL(sparql=''):
    json1 = ''
    if sparql:
        try:
            json1 = json.loads(sparql)
            return json1
        except:
            print('Error downloading SPARQL? Malformatted JSON? Skiping\n')
            return 
    else:
        print('Server return empty file')
        return 
    return

def getArchiveBotViewerDetails(url='', singleurl=False):
    viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
    origdomain = url.split('//')[1].split('/')[0]
    origdomain2 = re.sub(r'(?im)^(www\d*)\.', '.', origdomain)
    rawdomains = getURL(url=viewerurl)
    domains = re.findall(r"(?im)/archivebot/viewer/domain/([^<>\"]+)", rawdomains)
    details = []
    totaljobsize = 0
    for domain in domains:
        if domain != origdomain and not domain in origdomain and not origdomain2 in domain:
            continue
        urljobs = "https://archive.fart.website/archivebot/viewer/domain/" + domain
        rawjobs = getURL(url=urljobs)
        jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", rawjobs)
        for job in jobs[:25]: #limit, to avoid twitter, facebook and other with many jobs
            urljob = "https://archive.fart.website/archivebot/viewer/job/" + job
            rawjob = getURL(url=urljob)
            
            if singleurl:
                jsonfile = re.findall(r'(?im)<a href="(https://archive\.org/download/[^"<> ]+\.json)">', rawjob)
                if jsonfile:
                    jsonurl = jsonfile[0]
                    jsonraw = getURL(url=jsonurl)
                    if not url in jsonraw:
                        continue
            
            warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-\d{6}-%s[^<> ]*?-\d+\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (job), rawjob)
            jobdate = ''
            jobsize = 0
            for warc in warcs:
                jobdate = warc[0]
                jobsize += int(warc[1])
            if not jobdate:
                if re.search(r"(?im)-(\d{8})-\d{6}-", rawjob):
                    jobdate = re.findall(r"-(\d{8})-\d{6}-", rawjob)[0]
                else:
                    jobdate = 'nodate'
            if jobsize < 1024*1024:
                jobdetails = "[https://archive.fart.website/archivebot/viewer/domain/%s %s] - [https://archive.fart.website/archivebot/viewer/job/%s %s] - %s - {{red|%0.1d&nbsp;MB}}" % (domain, domain, job, job, jobdate, jobsize/(1024.0*1024))
            else:
                jobdetails = "[https://archive.fart.website/archivebot/viewer/domain/%s %s] - [https://archive.fart.website/archivebot/viewer/job/%s %s] - %s - %0.1d&nbsp;MB" % (domain, domain, job, job, jobdate, jobsize/(1024.0*1024))
            totaljobsize += jobsize
            details.append(jobdetails)
    return '<br/>'.join(details), totaljobsize

def getArchiveBotViewer(url=''):
    if url and '//' in url:
        domain = url.split('//')[1].split('/')[0]
        viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
        raw = getURL(url=viewerurl)
        if raw and '</form>' in raw:
            raw = raw.split('</form>')[1]
        else:
            return False, viewerurl, '', 0
        if re.search(r'No search results', raw):
            return False, viewerurl, '', 0
        else:
            if len(url.split(domain)[1]) > 1: #url is domain.ext/more
                details, totaljobsize = getArchiveBotViewerDetails(url=url, singleurl=True)
                return details and True or False, viewerurl, details, totaljobsize
            elif domain.lower() in raw.lower(): #url is domain.ext
                details, totaljobsize = getArchiveBotViewerDetails(url=url)
                return True, viewerurl, details, totaljobsize
            else:
                details, totaljobsize = getArchiveBotViewerDetails(url=url)
                return False, viewerurl, details, totaljobsize
    else:
        return False, 'https://archive.fart.website/archivebot/viewer/', '', 0
