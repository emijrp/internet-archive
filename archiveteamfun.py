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
import pickle
import random
import re
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse

cached = {}

def convertsize(b=0): #bytes
    if b < 1024: #<1KB
        return '0&nbsp;KB'
    elif b < 1024*1024: #<1MB
        return '%d&nbsp;KB' % (b/(1024))
    elif b < 1024*1024*1024: #<1GB
        return '%d&nbsp;MB' % (b/(1024*1024))
    elif b < 1024*1024*1024*1024: #<1TB
        return '%.1f&nbsp;GB' % (b/(1024.0*1024*1024))
    elif b < 1024*1024*1024*1024*1024: #<1PB
        return '%.1f&nbsp;TB' % (b/(1024.0*1024*1024*1024))
    elif b < 1024*1024*1024*1024*1024*1024: #<1EB
        return '%.1f&nbsp;PB' % (b/(1024.0*1024*1024*1024*1024))

def saveCache(c={}):
    with open('archivebot.cache', 'wb') as f:
        pickle.dump(c, f)

def loadCache():
    c = {}
    if os.path.exists('archivebot.cache'):
        with open('archivebot.cache', 'rb') as f:
            c = pickle.load(f)
    return c.copy()

def removeFromCache(url=''):
    global cached
    
    if url and url in cached:
        del cached[url]
        saveCache(c=cached)

def getURL(url='', cache=False, retry=True):
    global cached
    
    if cache: #do not download if it is cached
        if not cached: #empty dict
            cached = loadCache()
        if url in cached:
            print("Using cached page for %s" % (url))
            return cached[url]
    
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
    try:
        print("Retrieving: %s" % (url))
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
        if cache: #refresh cache
            cached[url] = raw
            if not random.randint(0, 5):
                saveCache(c=cached)
    except:
        sleep = 10 # seconds
        maxsleep = 30
        while retry and sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            try:
                raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
                if cache: #refresh cache
                    cached[url] = raw
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
    rawdomains = getURL(url=viewerurl, cache=True)
    domains = re.findall(r"(?im)/archivebot/viewer/domain/([^<>\"]+)", rawdomains)
    details = []
    totaljobsize = 0
    jobslimit = 500 #limit, to avoid twitter, facebook and other with many jobs
    for domain in domains:
        if domain != origdomain and not domain in origdomain and not origdomain2 in domain:
            continue
        urljobs = "https://archive.fart.website/archivebot/viewer/domain/" + domain
        rawjobs = getURL(url=urljobs, cache=True)
        jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", rawjobs)
        for job in jobs[:jobslimit]: 
            urljob = "https://archive.fart.website/archivebot/viewer/job/" + job
            rawjob = getURL(url=urljob, cache=True)
            jsonfile = re.findall(r'(?im)<a href="(https://archive\.org/download/[^"<> ]+\.json)">', rawjob)
            
            if not jsonfile: #job in progress, remove cache
                removeFromCache(url=urljob)
                continue
            
            if singleurl:
                if jsonfile:
                    jsonurl = jsonfile[0]
                    jsonraw = getURL(url=jsonurl, cache=True)
                    if not url in jsonraw:
                        continue
                else:
                    continue
            
            warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-\d{6}-%s[^<> ]*?\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (job), rawjob)
            if not warcs: #job in progress, remove cache
                removeFromCache(url=urljob)
                continue
            jobaborted = False
            if '-aborted-' in rawjob or '-aborted.json' in rawjob:
                jobaborted = True
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
            if jobdate and jobdate != 'nodate':
                jobdate = '%s-%s-%s' % (jobdate[0:4], jobdate[4:6], jobdate[6:8])
            if jobsize < 1024:
                jobdetails = "| [https://archive.fart.website/archivebot/viewer/domain/%s %s] || [https://archive.fart.website/archivebot/viewer/job/%s %s] || %s || data-sort-value=%d | {{red|%s}}" % (domain, domain, job, job, jobdate, jobsize, convertsize(b=jobsize))
            else:
                if jobaborted:
                    jobdetails = "| [https://archive.fart.website/archivebot/viewer/domain/%s %s] || [https://archive.fart.website/archivebot/viewer/job/%s %s] || %s || data-sort-value=%d | {{orange|%s}}" % (domain, domain, job, job, jobdate, jobsize, convertsize(b=jobsize))
                else:
                    jobdetails = "| [https://archive.fart.website/archivebot/viewer/domain/%s %s] || [https://archive.fart.website/archivebot/viewer/job/%s %s] || %s || data-sort-value=%d | {{green|%s}}" % (domain, domain, job, job, jobdate, jobsize, convertsize(b=jobsize))
            totaljobsize += jobsize
            details.append(jobdetails)
    detailsplain = '\n|-\n'.join(details)
    return detailsplain, totaljobsize

def getArchiveBotViewer(url=''):
    if url and '://' in url:
        if '://archive.org/' in url or '://www.webcitation.org/' in url:
            return False, 'https://archive.fart.website/archivebot/viewer/', '', 0
        """if '://transfer.sh/' in url:
            return False, 'https://archive.fart.website/archivebot/viewer/', '', 0
        if '://facebook.com/' in url or '://www.facebook.com/' in url:
            return False, 'https://archive.fart.website/archivebot/viewer/', '', 0
        if '://twitter.com/' in url or '://www.twitter.com/' in url:
            return False, 'https://archive.fart.website/archivebot/viewer/', '', 0
        if '://instagram.com/' in url or '://www.instagram.com/' in url:
            return False, 'https://archive.fart.website/archivebot/viewer/', '', 0"""
        
        domain = url.split('://')[1].split('/')[0]
        viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
        raw = getURL(url=viewerurl, cache=True)
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
