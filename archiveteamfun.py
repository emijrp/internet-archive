#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2019 emijrp <emijrp@gmail.com>
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

ArchivebotCache = {}
ChromebotCache = {}

def convertsize(b=0): #bytes
    if b < 1024: #<1KiB
        return '0&nbsp;KiB'
    elif b < 1024*1024: #<1MiB
        return '%d&nbsp;KiB' % (b/(1024))
    elif b < 1024*1024*1024: #<1GiB
        return '%d&nbsp;MiB' % (b/(1024*1024))
    elif b < 1024*1024*1024*1024: #<1TiB
        return '%.1f&nbsp;GiB' % (b/(1024.0*1024*1024))
    elif b < 1024*1024*1024*1024*1024: #<1PiB
        return '%.1f&nbsp;TiB' % (b/(1024.0*1024*1024*1024))
    elif b < 1024*1024*1024*1024*1024*1024: #<1EiB
        return '%.1f&nbsp;PiB' % (b/(1024.0*1024*1024*1024*1024))

def loadArchivebotCache():
    c = {}
    if os.path.exists('archivebot.cache'):
        with open('archivebot.cache', 'rb') as f:
            c = pickle.load(f)
    return c.copy()

def removeFromArchivebotCache(url=''):
    global ArchivebotCache
    
    if url and url in ArchivebotCache:
        del ArchivebotCache[url]
        saveArchivebotCache(c=ArchivebotCache)

def saveArchivebotCache(c={}):
    with open('archivebot.cache', 'wb') as f:
        pickle.dump(c, f)

def cleanArchiveBotCache():
    global ArchivebotCache
    ArchivebotCache2 = ArchivebotCache.copy()
    
    for url, raw in ArchivebotCache2.items():
        if url.startswith("https://archive.fart.website/archivebot/viewer/domain/"):
            domain = url.split("https://archive.fart.website/archivebot/viewer/domain/")[1]
            jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", raw)
            if domain == 'twitter.com' or \
                domain == 'www.facebook.com' or \
                domain == 'instagram.com' or domain == 'www.instagram.com' or \
                domain == 'www.youtube.com' or \
                len(jobs) >= 10:
                removeFromArchivebotCache(url=url)
        
        if url.startswith("https://archive.fart.website/archivebot/viewer/job/"):
            jsonfiles = re.findall(r'(?im)<a href="(https://archive\.org/download/[^"<> ]+\.json)">', raw)
            if not jsonfiles and re.search(r'-%s\d{4}-\d{6}-' % (datetime.datetime.today().year), raw): #job in progress, remove cache
                removeFromArchivebotCache(url=url)
            warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-(\d{6})-%s[^<> ]*?\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (job), raw)
            if not warcs and re.search(r'-%s\d{4}-\d{6}-' % (datetime.datetime.today().year), raw): #job in progress, remove cache
                removeFromArchivebotCache(url=urljob)

def loadChromebotCache():
    c = {}
    if os.path.exists('chromebot.cache'):
        with open('chromebot.cache', 'rb') as f:
            c = pickle.load(f)
    firstcached = datetime.datetime(2019, 5, 7)
    today = datetime.datetime.today()
    iaquery = 'https://archive.org/advancedsearch.php?q=chromebot&fl[]=identifier&sort[]=publicdate+desc&sort[]=&sort[]=&rows=50000&page=1&output=json'
    raw = getURL(url=iaquery, cache=False)
    json1 = json.loads(raw)
    for item in json1["response"]["docs"]:
        itemname = item['identifier']
        if not re.search(r'chromebot-\d\d\d\d-\d\d-\d\d-', itemname):
            continue
        itemdate = itemname.split('chromebot-')[1][:10]
        itemdate = datetime.datetime(int(itemdate.split('-')[0]), int(itemdate.split('-')[1]), int(itemdate.split('-')[2]))
        if itemdate >= firstcached and itemdate <= today:
            if not itemdate.isoformat() in c:
                c[itemdate.isoformat()] = []
                print('Loading .json for', item, itemdate)
                urljson = 'https://archive.org/download/%s/jobs.json' % (itemname)
                raw2 = getURL(url=urljson, cache=False)
                for line in raw2.splitlines():
                    if line.startswith('{"id":'):
                        json2 = json.loads(line)
                        json2['item'] = itemname
                        c[itemdate.isoformat()].append(json2)
                        #print(c[itemdate.isoformat()][-1]['id'])
    return c.copy()

def saveChromebotCache(c={}):
    with open('chromebot.cache', 'wb') as f:
        pickle.dump(c, f)

def getURL(url='', cache=False, retry=True):
    global ArchivebotCache
    
    if cache: #do not download if it is cached
        if not ArchivebotCache: #empty dict
            ArchivebotCache = loadArchivebotCache()
        if url:
            if url in ArchivebotCache:
                #print("Using cached page for %s" % (url))
                return ArchivebotCache[url]
    
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
    try:
        print("Retrieving: %s" % (url))
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
        if cache: #refresh cache
            ArchivebotCache[url] = raw
            if not random.randint(0, 100):
                saveArchivebotCache(c=ArchivebotCache)
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
                    ArchivebotCache[url] = raw
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

def getArchiveDetailsArchivebot(url='', singleurl=False):
    viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
    origdomain = url.split('//')[1].split('/')[0]
    origdomain2 = re.sub(r'(?im)^(www\d*)\.', '.', origdomain)
    rawdomains = getURL(url=viewerurl, cache=True)
    domains = re.findall(r"(?im)/archivebot/viewer/domain/([^<>\"]+)", rawdomains)
    if not domains: #no results for this url, remove cache
        removeFromArchivebotCache(url=viewerurl)
    details = []
    totaljobsize = 0
    jobslimit = 100000
    tool = 'ArchiveBot'
    for domain in domains:
        if domain != origdomain and not domain in origdomain and not origdomain2 in domain:
            continue
        urljobs = "https://archive.fart.website/archivebot/viewer/domain/" + domain
        rawjobs = getURL(url=urljobs, cache=True)
        jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", rawjobs)
        for job in jobs[:jobslimit]: 
            urljob = "https://archive.fart.website/archivebot/viewer/job/" + job
            rawjob = getURL(url=urljob, cache=True)
            jsonfiles = re.findall(r'(?im)<a href="(https://archive\.org/download/[^"<> ]+\.json)">', rawjob)
            for jsonfile in jsonfiles:
                if singleurl:
                    if jsonfile:
                        jsonurl = jsonfile
                        jsonraw = getURL(url=jsonurl, cache=True) #cache json from internet archive
                        if not url in jsonraw:
                            continue
                    else:
                        continue
                
                jobproblem = False
                warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-(\d{6})-%s[^<> ]*?\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (job), rawjob)
                if not warcs:
                    jobproblem = True
                jobdatetimes = []
                for warc in warcs:
                    jobdatetimes.append("%s-%s" % (warc[0], warc[1]))
                jobdatetimes = list(set(jobdatetimes))
                for jobdatetime in jobdatetimes:
                    if not jobdatetime in jsonfile:
                        continue
                    jobaborted = False
                    if ('%s-%s-aborted-' % (jobdatetime, job)) in rawjob or ('%s-%s-aborted.json' % (jobdatetime, job)) in rawjob:
                        jobaborted = True
                    jobdate = '-' in jobdatetime and jobdatetime.split('-')[0] or 'nodate'
                    jobsize = sum([jobdatetime == '%s-%s' % (warc[0], warc[1]) and int(warc[2]) or 0 for warc in warcs])
                    if jobdate and jobdate != 'nodate':
                        jobdate = '%s-%s-%s' % (jobdate[0:4], jobdate[4:6], jobdate[6:8])
                    if jobsize < 1024:
                        jobdetails = "| [[%s]] || [https://archive.fart.website/archivebot/viewer/domain/%s %s] || [https://archive.fart.website/archivebot/viewer/job/%s %s] || %s || data-sort-value=%d | {{red|%s}}" % (tool, domain, domain, job, job, jobdate, jobsize, convertsize(b=jobsize))
                    else:
                        if jobaborted or jobproblem:
                            jobdetails = "| [[%s]] || [https://archive.fart.website/archivebot/viewer/domain/%s %s] || [https://archive.fart.website/archivebot/viewer/job/%s %s] || %s || data-sort-value=%d | {{orange|%s}}" % (tool, domain, domain, job, job, jobdate, jobsize, convertsize(b=jobsize))
                        else:
                            jobdetails = "| [[%s]] || [https://archive.fart.website/archivebot/viewer/domain/%s %s] || [https://archive.fart.website/archivebot/viewer/job/%s %s] || %s || data-sort-value=%d | {{green|%s}}" % (tool, domain, domain, job, job, jobdate, jobsize, convertsize(b=jobsize))
                    totaljobsize += jobsize
                    details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsChromebot(url='', singleurl=False):
    global ChromebotCache
    details = []
    totaljobsize = 0
    if not ChromebotCache: #empty dict
        ChromebotCache = loadChromebotCache()
        saveChromebotCache(c=ChromebotCache)
    #{"id": "bajop-tomur-fagok-huzol", "user": "eientei95", "date": "2019-05-21T11:51:09.286515", "warcsize": 2775866, "url": "https://twitter.com/...", "urlcount": 1}
    tool = 'Chromebot'
    for date, jobs in ChromebotCache.items():
        for job in jobs:
            if url == job['url']:
                domain = job['url'].split('://')[1].split('/')[0]
                jobid = job['id'].split('-')[-1] # last chunk seems unique
                jobdate = job['date'].split('T')[0]
                jobsize = int(job['warcsize'])
                itemname = job['item']
                if job['warcsize'] < 1024:
                    jobdetails = "| [[%s]] || %s || [https://archive.org/download/%s %s] || %s || data-sort-value=%d | {{red|%s}}" % (tool, domain, itemname, jobid, jobdate, jobsize, convertsize(b=jobsize))
                else:
                    jobdetails = "| [[%s]] || %s || [https://archive.org/download/%s %s] || %s || data-sort-value=%d | {{green|%s}}" % (tool, domain, itemname, jobid, jobdate, jobsize, convertsize(b=jobsize))
                totaljobsize += jobsize
                details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsCore(url='', singleurl=False):
    detailsArchivebot, totaljobsizeArchivebot = getArchiveDetailsArchivebot(url=url, singleurl=singleurl)
    detailsChromebot, totaljobsizeChromebot = getArchiveDetailsChromebot(url=url, singleurl=singleurl)
    
    details = detailsArchivebot + detailsChromebot
    totaljobsize = totaljobsizeArchivebot + totaljobsizeChromebot
    
    detailsplain = '\n|-\n'.join(details)
    return detailsplain, totaljobsize

def getArchiveDetails(url=''):
    if url and '://' in url:
        if '://archive.org/' in url or \
           '://www.webcitation.org/' in url:
            return False, '', 0
        
        domain = url.split('://')[1].split('/')[0]
        viewerurl = 'https://archive.fart.website/archivebot/viewer/?q=' + url
        raw = getURL(url=viewerurl, cache=True)
        if raw and '</form>' in raw:
            raw = raw.split('</form>')[1]
        else:
            return False, '', 0
        if re.search(r'No search results', raw):
            return False, '', 0
        else:
            if len(url.split(domain)[1]) > 1: #url is domain.ext/more
                details, totaljobsize = getArchiveDetailsCore(url=url, singleurl=True)
                return details and True or False, details, totaljobsize
            elif domain.lower() in raw.lower(): #url is domain.ext
                details, totaljobsize = getArchiveDetailsCore(url=url)
                return True, details, totaljobsize
            else:
                details, totaljobsize = getArchiveDetailsCore(url=url)
                return False, details, totaljobsize
    else:
        return False, '', 0

def main():
    ChromebotCache = loadChromebotCache()
    saveChromebotCache(c=ChromebotCache)

if __name__ == "__main__":
    main()
