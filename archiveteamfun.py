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

def getArchiveBotViewerDetails(viewerurl=''):
    rawdomains = getURL(url=viewerurl)
    domains = re.findall(r"(?im)/archivebot/viewer/domain/([^<>\"]+)", rawdomains)
    details = []
    for domain in domains:
        urljobs = "https://archive.fart.website/archivebot/viewer/domain/" + domain
        rawjobs = getURL(url=urljobs)
        jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", rawjobs)
        for job in jobs:
            urljob = "https://archive.fart.website/archivebot/viewer/job/" + job
            rawjob = getURL(url=urljob)
            warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-\d{6}-%s-\d+\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (job), rawjob)
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
            details.append(jobdetails)
    return '<br/>'.join(details)

def getArchiveBotViewer(url=''):
    if url and '//' in url:
        domain = url.split('//')[1].split('/')[0]
        viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
        raw = getURL(url=viewerurl)
        if raw and '</form>' in raw:
            raw = raw.split('</form>')[1]
        else:
            return False, viewerurl
        if re.search(r'No search results', raw):
            return False, viewerurl
        else:
            if len(url.split(domain)[1]) > 1: #domain.com/more
                if re.search(r'(?im)(%s)' % (url), raw):
                    details = getArchiveBotViewerDetails(viewerurl=viewerurl)
                    return True, viewerurl, details
                else:
                    return False, viewerurl, ''
            elif re.search(r'(?im)(%s)' % (domain), raw):
                details = getArchiveBotViewerDetails(viewerurl=viewerurl)
                return True, viewerurl, details
            else:
                details = getArchiveBotViewerDetails(viewerurl=viewerurl)
                return False, viewerurl, details
    else:
        return False, 'https://archive.fart.website/archivebot/viewer/', ''
