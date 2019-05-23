#!/usr/bin/env python   
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
import os
import pickle
import random
import re
import socket
import sys
import threading
import time
import urllib.request

server = "irc.efnet.nl"
port = 6667
channel = "#archivebot"
botnick = "savebot%d" % (random.randint(10, 99))
SaveCron = {}

def loadSaveCron():
    c = {}
    if os.path.exists('savebot.cron'):
        with open('savebot.cron', 'rb') as f:
            c = pickle.load(f)
    return c.copy()

def saveSaveCron(c={}):
    with open('savebot.cron', 'wb') as f:
        pickle.dump(c, f)

def getURL(url=''):
    raw = ''
    req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    try:
        raw = urllib.request.urlopen(req).read().strip().decode('utf-8')
    except:
        try:
            raw = urllib.request.urlopen(req).read().strip().decode('latin-1')
        except:
            sleep = 10 # seconds
            maxsleep = 60
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

def archiveurl(url='', force=False):
    if url:
        #check if available in IA
        prefix = 'https://archive.org/wayback/available?url='
        checkurl = prefix + url
        raw = getURL(url=checkurl)
        #print(raw)
        if '"archived_snapshots": {}' in raw or force:
            #not available, archive it
            #print('Archiving URL',url)
            prefix2 = 'https://web.archive.org/save/'
            saveurl = prefix2 + url
            try:
                f = urllib.request.urlopen(saveurl)
                raw = f.read().decode('utf-8')
                print('Archived at https://web.archive.org/web/*/%s' % (url))
                return 'ok'
            except:
                print('URL 404 archived at https://web.archive.org/web/*/%s' % (url))
                return '404'
        else:
            print('Previously archived at https://web.archive.org/web/*/%s' % (url))
            return 'previously'
            #print(raw)

def parseFrequency(frequency=''):
    if re.search(r'(?im)^\d+(m|minutes?|mins?|h|hours?|d|days?)$', frequency):
        frequency = re.sub(r'(?im)(m|minutes?|mins?)$', 'mins', frequency)
        frequency = re.sub(r'(?im)(h|hours?)$', 'hours', frequency)
        frequency = re.sub(r'(?im)(d|days?)$', 'days', frequency)
        if frequency.endswith('mins') and int(frequency.split('mins')[0]) < 5:
            frequency = '5mins'
        return frequency
    return ''

def parseEnddate(enddate=''):
    enddate = enddate.lower()
    if re.search(r'(?im)^20[12][0-9]-\d\d-\d\d$', enddate):
        return datetime.datetime(int(enddate.split('-')[0]), int(enddate.split('-')[1]), int(enddate.split('-')[2]), 23, 59, 59)
    elif re.search(r'(?im)today\+\d+days?$', enddate):
        return datetime.datetime.today() + datetime.timedelta(days=int(enddate.split('today+')[1].split('day')[0]))
    return ''

def command_delete(conn='', message='', nick=''):
    global SaveCron
    params = message.split(' ')
    if len(params) == 1:
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Where is the URL?\r\n' % (nick), "UTF-8"))
        return
    action = ''
    url = ''
    if len(params) >= 2:
        action = params[0]
        url = params[1].strip()
    
    if url in SaveCron:
        del SaveCron[url]
        saveSaveCron(c=SaveCron)
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: URL deleted from savecron.\r\n' % (nick), "UTF-8"))
    else:
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: URL not in savecron.\r\n' % (nick), "UTF-8"))

def command_save(conn='', message='', nick=''):
    global SaveCron
    if not message:
        return
    params = message.split(' ')
    if len(params) == 1:
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Where is the URL?\r\n' % (nick), "UTF-8"))
        return
    action = ''
    url = ''
    if len(params) >= 2:
        action = params[0]
        url = params[1].strip()
    
    frequency = 'once'
    if len(params) >= 3:
        frequency = parseFrequency(frequency=params[2])
        if not frequency:
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Invalid frequency (%s). Examples: 5min, 30min, 1hour, 5hour, 1day, 3day.\r\n' % (nick, params[2]), "UTF-8"))
            return
    
    enddate = datetime.datetime.today() + datetime.timedelta(days=1) # 24 hours
    if len(params) >= 4:
        enddate = parseEnddate(enddate=params[3])
        if not enddate:
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Invalid end date (%s). Examples: today, today+3day, YYYY-MM-DD.\r\n' % (nick, params[3]), "UTF-8"))
            return
    
    if not url or (not url.lower().startswith('http://') and not url.lower().startswith('https://')):
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Only http and https are allowed.\r\n' % (nick), "UTF-8"))
        return
    
    if url in SaveCron:
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: URL is already in savecron: %s. Use d command to delete this URL and set new frequency/enddate.\r\n' % (nick, SaveCron[url]), "UTF-8"))
        return
    else:
        if frequency and frequency != 'once':
            SaveCron[url] = { 'frequency': frequency, 'enddate': enddate, 'lastsave': datetime.datetime.now() }
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: This URL %s will be saved every %s until %s.\r\n' % (nick, url, frequency, enddate.isoformat()), "UTF-8"))
            saveSaveCron(c=SaveCron)
    
    if len(params) >= 2:
        status = archiveurl(url=url, force=True)
        if status == 'ok':
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: URL saved in https://web.archive.org/web/*/%s \r\n' % (nick, url), "UTF-8"))
        elif status == '404':
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Error while retrieving URL %s \r\n' % (nick, url), "UTF-8"))
        elif status == 'previously':
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: URL was in WaybackMachine https://web.archive.org/web/*/%s \r\n' % (nick, url), "UTF-8"))

def frequency2delta(frequency=''):
    m = re.findall(r'(?im)^(\d+)(m|mins?|h|hours?|d|days?)$', frequency.lower())
    if m:
        num = int(m[0][0])
        step = m[0][1]
        if step in ['m', 'min', 'minute', 'mins', 'minutes']:
            if num < 5:
                num = 5 #minimum 5 minutes
            return datetime.timedelta(minutes=num)
        elif step in ['h', 'hour', 'hours']: 
            return datetime.timedelta(hours=num)
        elif step in ['d', 'day', 'days']: 
            return datetime.timedelta(days=num)
    return datetime.timedelta(seconds=0)

def runcroncore():
    global SaveCron
    print('Running savecron', datetime.datetime.now())
    for url, props in SaveCron.items():
        if datetime.datetime.now() >= props['lastsave'] + frequency2delta(frequency=props['frequency']):
            status = archiveurl(url=url, force=True)
            props2 = props
            props2['lastsave'] = datetime.datetime.now()
            SaveCron[url] = props2
            #print(props2)
            #print(SaveCron)
            print('Saved (status=%s): %s' % (status, url))

def runcron():
    t1 = time.time()
    cronfreq = 300 # 300 seconds = 5 minutes, minimum for /save/
    while True:
        time.sleep(10)
        if time.time() - t1 >= cronfreq:
            t1 = time.time()
            thread = threading.Thread(target=runcroncore, args=())
            thread.start()

def run():
    global SaveCron
    #http://toolserver.org/~bryan/TsLogBot/TsLogBot.py (MIT License)
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server, port))
    
    conn.sendall(bytes('USER %s * * %s\r\n' % (botnick, botnick), "UTF-8"))
    conn.sendall(bytes('NICK %s\r\n' % (botnick), "UTF-8"))
    
    SaveCron = loadSaveCron()
    thread = threading.Thread(target=runcron, args=())
    thread.start()
    
    buffer = ''
    joined = False
    while True:
        time.sleep(0.02)
        if '\n' in buffer:
            line = buffer[:buffer.index('\n')]
            buffer = buffer[len(line) + 1:]
            line = line.strip()
            print(line)

            data = line.split(' ', 3)
            if data[0] == 'PING':
                conn.sendall(bytes('PONG %s\r\n' % data[1], "UTF-8"))
                if not joined:
                    time.sleep(5)
                    conn.sendall(bytes('JOIN %s\r\n' % (channel), "UTF-8"))
                    #conn.sendall(bytes('PRIVMSG %s :helloooo.\r\n' % (channel), "UTF-8"))
                    joined = True
            elif data[1] == 'PRIVMSG':
                nick = data[0][1:data[0].index('!')]
                target = data[2]
                message = data[3][1:]
                if target == channel:
                    if message.startswith('%s:' % (botnick)):
                        curatedmessage = message.lstrip('%s:' % (botnick)).strip()
                        curatedmessage = re.sub(r'  *', ' ', curatedmessage)
                        #print(message)
                        if curatedmessage.startswith('a '):
                            command_save(conn=conn, message=curatedmessage, nick=nick)
                        elif curatedmessage.startswith('d '):
                            command_delete(conn=conn, message=curatedmessage, nick=nick)
                else:
                    #private msgs or msgs from other channels? ignore
                    pass
        else:
            data = conn.recv(1024).decode()
            if not data: raise socket.error
            buffer += data

def main():    
    run()

if __name__ == "__main__":
    main()
