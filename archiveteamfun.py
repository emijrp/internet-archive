#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2019 Archive Team
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
import gzip
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
NarabotCache = {}
WikiteamCache = {}
YoutubearchiveCache = {}

# Ideas:
# Mirrortube (no channel info in metadata :()
# Videobot
#
# Fix:
# https://archiveteam.org/index.php?title=ArchiveBot/2018_Brazilian_general_elections (portal.imprensanacional.gov.br no json = no saved?)
#
# Error no json:
"""Retry in 20 seconds...
Retrieving: https://archive.fart.website/archivebot/viewer/?q=https://transfer.notkiska.pw/kqFhq/twitter-@mattiastesfaye  
Retrieving: https://archive.org/download/archiveteam_archivebot_go_20190514190001/urls-transfer.notkiska.pw-berries.space-accounts-09-May-2019-inf-20190511-012325-8grwh.json
"""

def convertsize(b=0): #bytes
    if type(b) is int:
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
    else:
        return b

def loadArchivebotCache():
    c = {}
    if os.path.exists('archivebot.cache'):
        with open('archivebot.cache', 'rb') as f:
            c = pickle.load(f)
    return c.copy()

def removeFromArchivebotCache(url='', save=True):
    global ArchivebotCache
    if url and url in ArchivebotCache:
        del ArchivebotCache[url]
        if save:
            saveArchivebotCache()

def saveArchivebotCache():
    global ArchivebotCache
    with open('archivebot.cache', 'wb') as f:
        pickle.dump(ArchivebotCache, f)

def cleanArchiveBotCache():
    global ArchivebotCache
    ArchivebotCache2 = ArchivebotCache.copy()
    
    for url, raw in ArchivebotCache2.items():
        #remove from cache urls without results
        #we need to check for results in the next run
        if url.startswith("https://archive.fart.website/archivebot/viewer/?q="):
            if re.search(r'(?im)<em>No search results.</em>', raw):
                removeFromArchivebotCache(url=url, save=False)
        
        #remove from cache domains with many jobs (FB, TW, etc)
        #these result pages change frequently
        if url.startswith("https://archive.fart.website/archivebot/viewer/domain/"):
            domain = url.split("https://archive.fart.website/archivebot/viewer/domain/")[1]
            jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", raw)
            if len(jobs) >= 10:
                removeFromArchivebotCache(url=url, save=False)
        
        #remove from cache jobs with problems or in progress
        #we need to check wether problems were solved in the next run
        if url.startswith("https://archive.fart.website/archivebot/viewer/job/"):
            job = url.split("https://archive.fart.website/archivebot/viewer/job/")[1]
            jsonfileurls = re.findall(r'(?im)<a href="(https://archive\.org/download/[^"<> ]+\.json)">', raw)
            if not jsonfileurls and re.search(r'-%s\d{4}-\d{6}-' % (datetime.datetime.today().year), raw): #job in progress
                removeFromArchivebotCache(url=url, save=False)
            warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-(\d{6})-%s[^<> ]*?\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (job), raw)
            if not warcs and re.search(r'-%s\d{4}-\d{6}-' % (datetime.datetime.today().year), raw): #job in progress
                removeFromArchivebotCache(url=url, save=False)
        
        if 'borg.xyz:82/logs/' in url and not '.log' in url:
            removeFromArchivebotCache(url=url, save=False)
        
    saveArchivebotCache()

def loadChromebotCache():
    c = {}
    if os.path.exists('chromebot.cache'):
        with open('chromebot.cache', 'rb') as f:
            c = pickle.load(f)
    firstcached = datetime.datetime(2019, 5, 7)
    today = datetime.datetime.today()
    iaquery = 'https://archive.org/advancedsearch.php?q=chromebot&fl[]=identifier&sort[]=publicdate+desc&sort[]=&sort[]=&rows=5000000&page=1&output=json'
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
                urlitem = 'https://archive.org/download/%s' % (itemname)
                raw2 = getURL(url=urlitem, cache=False)
                print('Loading .json for', item, itemdate)
                urljson = ''
                if '"jobs.json"' in raw2:
                    urljson = 'https://archive.org/download/%s/jobs.json' % (itemname)
                elif '"jobs.json.gz"' in raw2:
                    urljson = 'https://archive.org/download/%s/jobs.json.gz' % (itemname)
                if urljson:
                    raw3 = getURL(url=urljson, cache=False)
                    for line in raw3.splitlines():
                        if line.startswith('{"id":'):
                            json2 = json.loads(line)
                            json2['item'] = itemname
                            c[itemdate.isoformat()].append(json2)
                            #print(c[itemdate.isoformat()][-1]['id'])
    return c.copy()

def saveChromebotCache():
    global ChromebotCache
    with open('chromebot.cache', 'wb') as f:
        pickle.dump(ChromebotCache, f)

def loadNarabotCache():
    c = {}
    if os.path.exists('narabot.cache'):
        with open('narabot.cache', 'rb') as f:
            c = pickle.load(f)
    iaquery = 'https://archive.org/advancedsearch.php?q=collection%3Agithub_narabot_mirror&fl[]=identifier&fl[]=originalurl&sort[]=&sort[]=&sort[]=&rows=5000000&page=1&output=json'
    raw = getURL(url=iaquery, cache=False)
    json1 = json.loads(raw)
    for item in json1["response"]["docs"]:
        if not 'originalurl' in item:
            continue
        itemname = item['identifier']
        originalurl = item['originalurl']
        if type(originalurl) is list:
            originalurl = originalurl[0]
        c[itemname] = { 'originalurl': originalurl }
    return c.copy()

def saveNarabotCache():
    global NarabotCache
    with open('narabot.cache', 'wb') as f:
        pickle.dump(NarabotCache, f)

def loadWikiteamCache():
    c = {}
    if os.path.exists('wikiteam.cache'):
        with open('wikiteam.cache', 'rb') as f:
            c = pickle.load(f)
    iaquery = 'https://archive.org/advancedsearch.php?q=collection%3Awikiteam&fl[]=identifier&fl[]=originalurl&sort[]=&sort[]=&sort[]=&rows=5000000&page=1&output=json'
    raw = getURL(url=iaquery, cache=False)
    json1 = json.loads(raw)
    for item in json1["response"]["docs"]:
        if not 'originalurl' in item:
            continue
        itemname = item['identifier']
        originalurl = item['originalurl']
        if type(originalurl) is list:
            originalurl = originalurl[0]
        #if not itemname.startswith('wiki-'):
        #    continue
        c[itemname] = { 'originalurl': originalurl }
    return c.copy()

def saveWikiteamCache():
    global WikiteamCache
    with open('wikiteam.cache', 'wb') as f:
        pickle.dump(WikiteamCache, f)

def loadYoutubearchiveCache():
    pass

def saveYoutubearchiveCache():
    pass

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
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' }
    request = urllib.request.Request(url, headers=headers)
    try:
        print("Retrieving: %s" % (url))
        response = urllib.request.urlopen(request)
        if url.endswith('.gz'):
            gzipFile = gzip.GzipFile(fileobj=response)
            raw = gzipFile.read().strip().decode('utf-8')
        else:
            raw = response.read().strip().decode('utf-8')
        if cache: #refresh cache
            ArchivebotCache[url] = raw
            if not random.randint(0, 100):
                saveArchivebotCache()
    except:
        sleep = 10 # seconds
        maxsleep = 30
        while retry and sleep <= maxsleep:
            print('Error while retrieving: %s' % (url))
            print('Retry in %s seconds...' % (sleep))
            time.sleep(sleep)
            try:
                response = urllib.request.urlopen(request)
                if url.endswith('.gz'):
                    gzipFile = gzip.GzipFile(fileobj=response)
                    raw = gzipFile.read().strip().decode('utf-8')
                else:
                    raw = response.read().strip().decode('utf-8')
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

def genJobDetails(tool='', domainlink='', joburl='', jobdate='', jobsize='', jobobjects='', jobaborted=False, jobproblem=False):
    jobdetails = ""
    if type(jobsize) is int:
        if jobsize < 1024:
            jobdetails = "| %s || %s || %s || %s || data-sort-value=%d | {{red|%s}} || data-sort-value=%s | %s" % (tool, domainlink, joburl, jobdate, jobsize, convertsize(b=jobsize), jobobjects.split(' ')[0], jobobjects)
        else:
            jobcolor = 'green'
            if jobaborted:
                jobcolor = 'orange'
            if jobproblem:
                jobcolor = 'purple'
            jobdetails = "| %s || %s || %s || %s || data-sort-value=%d | {{%s|%s}} || data-sort-value=%s | %s" % (tool, domainlink, joburl, jobdate, jobsize, jobcolor, convertsize(b=jobsize), jobobjects.split(' ')[0], jobobjects)
    else:
        jobdetails = "| %s || %s || %s || %s || data-sort-value=0 | %s || data-sort-value=%s | %s" % (tool, domainlink, joburl, jobdate, convertsize(b=jobsize), jobobjects.split(' ')[0], jobobjects)
    return jobdetails

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
    tool = '[[ArchiveBot]]'
    for domain in domains:
        if domain != origdomain and not domain in origdomain and not origdomain2 in domain:
            continue
        urljobs = "https://archive.fart.website/archivebot/viewer/domain/" + domain
        rawjobs = getURL(url=urljobs, cache=True)
        jobs = re.findall(r"(?im)/archivebot/viewer/job/([^<>\"]+)", rawjobs)
        for jobid in jobs[:jobslimit]: 
            urljob = "https://archive.fart.website/archivebot/viewer/job/" + jobid
            rawjob = getURL(url=urljob, cache=True)
            jsonfileurls = re.findall(r'(?im)<a href="(https://archive\.org/download/[^"<> ]+\.json)">', rawjob)
            for jsonfileurl in jsonfileurls:
                if singleurl:
                    jsonraw = getURL(url=jsonfileurl, cache=True) #cache json from internet archive
                    jsonfileloaded = json.loads(jsonraw)
                    if not 'url' in jsonfileloaded or ('url' in jsonfileloaded and jsonfileloaded['url'] != url):
                        continue
                
                jobproblem = False
                warcs = re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-(\d{6})-%s[^<> ]*?\.warc\.gz\s*</a>\s*</td>\s*<td>(\d+)</td>" % (jobid), rawjob)
                if not warcs:
                    jobproblem = True
                jobdatetimes = []
                for warc in warcs:
                    jobdatetimes.append("%s-%s" % (warc[0], warc[1]))
                jobdatetimes = list(set(jobdatetimes))
                for jobdatetime in jobdatetimes:
                    if not jobdatetime in jsonfileurl:
                        continue
                    warcsnometa = len(re.findall(r"(?im)>\s*[^<>\"]+?-(\d{8})-(\d{6})-%s-?\d*\.warc\.gz\s*</a>" % (jobid), rawjob))
                    jobaborted = False
                    if ('%s-%s-aborted-' % (jobdatetime, jobid)) in rawjob or ('%s-%s-aborted.json' % (jobdatetime, jobid)) in rawjob:
                        jobaborted = True
                    jobdate = '-' in jobdatetime and jobdatetime.split('-')[0] or 'nodate'
                    jobsize = sum([jobdatetime == '%s-%s' % (warc[0], warc[1]) and int(warc[2]) or 0 for warc in warcs])
                    if jobdate and jobdate != 'nodate':
                        jobdate = '%s-%s-%s' % (jobdate[0:4], jobdate[4:6], jobdate[6:8])
                    jobdetails = genJobDetails(tool=tool, domainlink="[https://archive.fart.website/archivebot/viewer/domain/%s %s]" % (domain, domain), joburl="[https://archive.fart.website/archivebot/viewer/job/%s %s]" % (jobid, jobid), jobdate=jobdate, jobsize=jobsize, jobobjects="%d warcs" % (warcsnometa))
                    totaljobsize += jobsize
                    details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsChromebot(url='', singleurl=False):
    global ChromebotCache
    details = []
    totaljobsize = 0
    if not ChromebotCache: #empty dict
        ChromebotCache = loadChromebotCache()
        saveChromebotCache()
    #{"id": "bajop-tomur-fagok-huzol", "user": "eientei95", "date": "2019-05-21T11:51:09.286515", "warcsize": 2775866, "url": "https://twitter.com/...", "urlcount": 1}
    tool = '[[Chromebot]]'
    for date, jobs in ChromebotCache.items():
        for job in jobs:
            if job['url'] == url or ('urlseed' in job and job['urlseed'] == url):
                domain = url.split('://')[1].split('/')[0]
                jobid = job['id'].split('-')[-1] # last chunk seems unique
                jobdate = '-'
                if 'date' in job:
                    jobdate = job['date'].split('T')[0]
                elif 'queued' in job:
                    jobdate = job['queued'].split('T')[0]
                jobsize = '-'
                if 'warcsize' in job:
                    jobsize = int(job['warcsize'])
                jobobjects = '1 urls'
                if 'urlcount' in job:
                    jobobjects = "%s urls" % (int(job['urlcount']))
                itemname = job['item']
                jobdetails = genJobDetails(tool=tool, domainlink=domain, joburl="[https://archive.org/download/%s %s]" % (itemname, jobid), jobdate=jobdate, jobsize=jobsize, jobobjects=jobobjects)
                totaljobsize += jobsize
                details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsNarabot(url='', singleurl=False):
    global NarabotCache
    details = []
    totaljobsize = 0
    if not NarabotCache: #empty dict
        NarabotCache = loadNarabotCache()
        saveNarabotCache()
    tool = '[[Narabot]]'
    for itemname, props in NarabotCache.items():
        if props['originalurl'].strip('/').startswith(url.strip('/')):
            domain = props['originalurl'].split('://')[1].split('/')[0]
            urlfiles = 'https://archive.org/download/%s/%s_files.xml' % (itemname, itemname)
            rawfiles = getURL(url=urlfiles, cache=True)
            jobid = 'job'
            jobdate = itemname.split('_-_')[1].split('_')[0]
            jobsize = sum([int(x) for x in re.findall(r'(?im)<size>(\d+)</size>', rawfiles)])
            jobdetails = genJobDetails(tool=tool, domainlink=domain, joburl="[https://archive.org/download/%s %s]" % (itemname, jobid), jobdate=jobdate, jobsize=jobsize, jobobjects="1 repo")
            totaljobsize += jobsize
            details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsWikiteam(url='', singleurl=False):
    global WikiteamCache
    details = []
    totaljobsize = 0
    if not WikiteamCache: #empty dict
        WikiteamCache = loadWikiteamCache()
        saveWikiteamCache()
    tool = '[[WikiTeam]]'
    for itemname, props in WikiteamCache.items():
        itemname_ = re.sub(r'(?im)^wiki-', '', itemname)
        if props['originalurl'].strip('/').startswith(url.strip('/')):
            #if item files follows wikidump/history filename style, we use every file in item like a different job
            #otherwise we count just 1 job and sum all file sizes
            domain = props['originalurl'].split('://')[1].split('/')[0]
            urlfiles = 'https://archive.org/download/%s/%s_files.xml' % (itemname, itemname)
            rawfiles = getURL(url=urlfiles, cache=True)
            isstandard = re.search(r'(?im)<file name="((%s)-(\d{8})-(wikidump|history)\.[^ ]+?)" source="original">' % (itemname_), rawfiles) and True or False
            if isstandard:
                for xfile in rawfiles.split('</file>'):
                    jobid = 'job'
                    jobdate = 'date'
                    jobsize = re.findall(r'(?im)<size>(\d+)</size>', xfile) and int(re.findall(r'(?im)<size>(\d+)</size>', xfile)[0]) or 0
                    m = re.findall(r'(?im)<file name="((%s)-(\d{8})-(wikidump|history)\.[^ ]+?)" source="original">' % (itemname_), xfile)
                    if m:
                        m = m[0]
                        jobid = m[3]
                        jobdate = '%s-%s-%s' % (m[2][0:4], m[2][4:6], m[2][6:8])
                        jobdetails = genJobDetails(tool=tool, domainlink=domain, joburl="[https://archive.org/download/%s %s]" % (itemname, jobid), jobdate=jobdate, jobsize=jobsize, jobobjects="1 dump")
                        totaljobsize += jobsize
                        details.append(jobdetails)
            else:
                jobid = 'other'
                jobdate = re.findall(r'(?im)<mtime>(\d+)</mtime>', rawfiles) and int(re.findall(r'(?im)<mtime>(\d+)</mtime>', rawfiles)[0]) or 'date'
                if type(jobdate) is int:
                    jobdate = datetime.datetime.utcfromtimestamp(jobdate).strftime('%Y-%m-%d')
                jobsize = sum([int(x) for x in re.findall(r'(?im)<size>(\d+)</size>', rawfiles)])
                jobdetails = genJobDetails(tool=tool, domainlink=domain, joburl="[https://archive.org/download/%s %s]" % (itemname, jobid), jobdate=jobdate, jobsize=jobsize)
                totaljobsize += jobsize
                details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsYoutubearchive(url='', singleurl=False):
    global YoutubearchiveCache
    details = []
    totaljobsize = 0
    if not YoutubearchiveCache: #empty dict
        YoutubearchiveCache = loadYoutubearchiveCache()
        saveYoutubearchiveCache()
    tool = '[[YouTube|ytarchive]]'
    if re.search(r'https://www\.youtube\.com/(channel|user)/[^/]+', url):
        domain = url.split('://')[1].split('/')[0]
        channelid = url.split('/')[4].split('/')[0]
        urlytarchive = 'http://borg.xyz:82/logs/dl/?C=M;O=D'
        rawytarchive = getURL(url=urlytarchive, cache=True)
        channels = re.findall(r'(?im)<a href="([^/]+)/">', rawytarchive)
        if channelid in channels:
            urlytarchive2 = 'http://borg.xyz:82/logs/dl/%s/?C=M;O=D' % (channelid)
            rawytarchive2 = getURL(url=urlytarchive2, cache=True)
            logs = re.findall(r'(?im)<a href="([^<>]*?\.log[^<>]*?)">', rawytarchive2)
            if logs:
                logfilename = logs[0]
                urlytarchive3 = 'http://borg.xyz:82/logs/dl/%s/%s' % (channelid, logfilename)
                rawytarchive3 = getURL(url=urlytarchive3, cache=True)
                if re.search(r'Finished downloading playlist', rawytarchive3):
                    jobid = '-'
                    jobdate = logfilename.split('T')[0]
                    jobsize = '-'
                    jobobjects = '-'
                    if re.search(r'(?im)Downloading video (\d+) of \1$', rawytarchive3):
                        numvideos = int(re.findall(r'(?im)Downloading video (\d+) of \1$', rawytarchive3)[0])
                        numerrors = re.findall(r'ERROR: ', rawytarchive3) and len(re.findall(r'ERROR: ', rawytarchive3)[0]) or 0
                        jobobjects = "%s videos" % (numvideos-numerrors)
                    jobdetails = genJobDetails(tool=tool, domainlink=domain, joburl="%s" % (jobid), jobdate=jobdate, jobsize=jobsize, jobobjects=jobobjects)
                    if type(jobsize) is int:
                        totaljobsize += jobsize
                    details.append(jobdetails)
    return details, totaljobsize

def getArchiveDetailsCore(url='', singleurl=False):
    detailsArchivebot, totaljobsizeArchivebot = getArchiveDetailsArchivebot(url=url, singleurl=singleurl)
    detailsChromebot, totaljobsizeChromebot = getArchiveDetailsChromebot(url=url, singleurl=singleurl)
    detailsNarabot, totaljobsizeNarabot = getArchiveDetailsNarabot(url=url, singleurl=singleurl)
    detailsWikiteam, totaljobsizeWikiteam = getArchiveDetailsWikiteam(url=url, singleurl=singleurl)
    detailsYoutubearchive, totaljobsizeYoutubearchive = getArchiveDetailsYoutubearchive(url=url, singleurl=singleurl)
    
    details = detailsArchivebot + detailsChromebot + detailsNarabot + detailsWikiteam + detailsYoutubearchive
    totaljobsize = totaljobsizeArchivebot + totaljobsizeChromebot + totaljobsizeNarabot + totaljobsizeWikiteam + totaljobsizeYoutubearchive
    
    detailsplain = '\n|-\n'.join(details)
    return detailsplain, totaljobsize

def getArchiveDetails(url=''):
    if url and '://' in url:
        if '://archive.org/' in url or \
           '://www.webcitation.org/' in url:
            return False, '', 0
        
        domain = url.split('://')[1].split('/')[0]
        if len(url.split(domain)[1]) > 1: #url is domain.ext/more
            details, totaljobsize = getArchiveDetailsCore(url=url, singleurl=True)
            return details and True or False, details, totaljobsize
        
        #url is domain.ext
        details, totaljobsize = getArchiveDetailsCore(url=url, singleurl=False)
        return details and True or False, details, totaljobsize
    
    return False, '', 0
