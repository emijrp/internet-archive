#!/usr/bin/env python   
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Archive Team
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

# Instructions:
# 1) virtualenv -p python3.6 snscrapebot
# 2) cd snscrapebot; source bin/activate
# 3) pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
# 4) copy this file in snscrapebot directory
# 5) screen
# 6) python snscrape-ircbot.py
# 7) Ctrl-A Ctrl-D

server = "irc.efnet.nl"
port = 6667
channel = "#archivebot2"
botnick = "savebot%d" % (random.randint(10, 99))

def command_twitter_user(conn='', message='', nick=''):
    if not message:
        return
    params = message.split(' ')
    if len(params) == 1:
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Where is the user for twitter-user?\r\n' % (nick), "UTF-8"))
        return
    twitter_user = ''
    if len(params) >= 2:
        twitter_user = params[1].strip().strip('@').strip()
    if not twitter_user or re.search(r'(?im)[^a-z0-9_]', twitter_user):
        conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: User error: %s\r\n' % (nick, twitter_user), "UTF-8"))
    destfile = "twitter-user-%s" % (twitter_user)
    conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Downloading twitter-user %s\r\n' % (nick, twitter_user), "UTF-8"))
    #os.system("snscrape twitter-user %s > %s" % (twitter_user, destfile))
    os.system("echo 'https://twitter.com/%s' > %s" % (twitter_user, destfile))
    with open(destfile, 'r') as f:
        destfileraw = f.read().strip()
        destfilenumlines = len(destfileraw.splitlines())
        if len(re.findall(r'(?im)^http', destfileraw)) != destfilenumlines:
            conn.sendall(bytes('PRIVMSG ' + channel + ' :%s: Error while downloading twitter-user %s\r\n' % (nick, twitter_user), "UTF-8"))
            return
        url = os.popen('curl --upload-file "./%s" "https://transfer.notkiska.pw/%s"' % (destfile, destfile)).read().strip()
        if url:
            conn.sendall(bytes('PRIVMSG ' + channel + ' :!ao https://twitter.com/%s\r\n' % (twitter_user), "UTF-8"))
            conn.sendall(bytes('PRIVMSG ' + channel + ' :chromebot: a https://twitter.com/%s\r\n' % (twitter_user), "UTF-8"))
            conn.sendall(bytes('PRIVMSG ' + channel + ' :!ao < %s --concurrency 6 --delay 0\r\n' % (url), "UTF-8"))

def run():
    #http://toolserver.org/~bryan/TsLogBot/TsLogBot.py (MIT License)
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server, port))
    
    conn.sendall(bytes('USER %s * * %s\r\n' % (botnick, botnick), "UTF-8"))
    conn.sendall(bytes('NICK %s\r\n' % (botnick), "UTF-8"))
    
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
                        if curatedmessage.startswith('twitter-user '):
                            command_twitter_user(conn=conn, message=curatedmessage, nick=nick)
                        elif curatedmessage.startswith('twitter-list-members '):
                            pass
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
