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

import csv
import datetime
import getopt
import glob
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib
import urllib.request
from xml.etree import ElementTree as ET # para ver los XMl que devuelve flickrapi con ET.dump(resp)

import flickrapi
from internetarchive import upload
from internetarchive import get_item

"""
Installation:
* virtualenv -p python3 flickr2ia
* cd flickr2ia
* source bin/activate
* pip install internetarchive
* ia configure
* pip install flickrapi
* Register an APP in https://www.flickr.com/services/apps/create/apply
* Save apikey and apisecret codes in flickr.token file in the same path of this script
* Run this script: python flickr2ia.py USERID MODE
"""

fslimit = 80 #max length to avoid filesystem issues
tagslimit = 100 #max tags in IA item

def plain(s=''):
    if not s: #None value?
        s = 'None'
    s = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    s = re.sub(r'(?i)[^a-z0-9-]', ' ', s)
    s = re.sub(r'  +', ' ', s.strip())
    s = re.sub(r' ', '_', s.strip())
    return s[:fslimit]

def getUserPhotosets(flickr='', user_id=''):
    photosets = []
    page = 1
    pages = 1
    while page <= pages:
        resp = flickr.photosets.getList(user_id=user_id, page=page)
        root = ET.fromstring(ET.tostring(resp, method='xml'))
        for photoset in root[0].findall('photoset'):
            photosets.append([photoset.get('id'), {
                'title': photoset.find('title').text, 
                'description': photoset.find('description').text, 
                'primary': photoset.get('primary'), 
                'numphotos': int(photoset.get('photos')), 
                'numvideos': int(photoset.get('videos')), 
            }])
        pages = int(root[0].get('pages'))
        page += 1
    photosets.sort()
    photosets.append(['', {'title': 'noset', 'description': '', 'primary': ''}])
    return photosets

def getAllPhotosFromUser(flickr='', user_id=''):
    photos = {}
    page = 1
    pages = 1
    while page <= pages:
        resp = flickr.people.getPublicPhotos(user_id=user_id, extras='url_o,url_sq,url_m') #only public ones
        root = ET.fromstring(ET.tostring(resp, method='xml'))
        for photo in root[0].findall('photo'):
            photos[photo.get('id')] = {
                'title': photo.get('title'), 
                'url_o': photo.get('url_o'), 
                'url_sq': photo.get('url_sq'), 
                'url_m': photo.get('url_m'), 
            }
        pages = int(root[0].get('pages'))
        page += 1
    return photos

def getPhotosFromPhotoset(flickr='', user_id='', photoset_id=''):
    privacy_filter = 1 # 1: Only public, see more https://www.flickr.com/services/api/flickr.photosets.getPhotos.html
    photos = {}
    page = 1
    pages = 1
    while page <= pages:
        resp = flickr.photosets.getPhotos(photoset_id=photoset_id, user_id=user_id, privacy_filter=privacy_filter, extras='url_o,url_sq,url_m')
        root = ET.fromstring(ET.tostring(resp, method='xml'))
        for photo in root[0].findall('photo'):
            photos[photo.get('id')] = {
                'title': photo.get('title'), 
                'url_o': photo.get('url_o'), 
                'url_sq': photo.get('url_sq'), 
                'url_m': photo.get('url_m'), 
            }
        pages = int(root[0].get('pages'))
        page += 1
    return photos

def getPhotoInfoXML(flickr='', photo_id=''):
    resp = flickr.photos.getInfo(photo_id=photo_id)
    xml = ET.tostring(resp, method='xml')
    return xml

def getPhotoOriginalFormat(xml=''):
    root = ET.fromstring(xml)
    return root[0].get('originalformat')

def getPhotoId(xml=''):
    root = ET.fromstring(xml)
    return root[0].get('id')

def getPhotoTitle(xml=''):
    root = ET.fromstring(xml)
    return root[0].findall('title')[0].text

def getPhotoTags(xml=''):
    root = ET.fromstring(xml)
    phototags = []
    for tags in root[0].findall('tags'):
        for tag in tags.findall('tag'):
            phototags.append(tag.get('raw'))
    return phototags

def getUserInfoXML(flickr='', user_id=''):
    resp = flickr.people.getInfo(user_id=user_id)
    xml = ET.tostring(resp, method='xml')
    return xml

def getUserPathalias(flickr='', user_id=''):
    resp = flickr.people.getInfo(user_id=user_id)
    root = ET.fromstring(ET.tostring(resp, method='xml'))
    pathalias = root[0].get('path_alias')
    return pathalias

def getUserUsername(flickr='', user_id=''):
    resp = flickr.people.getInfo(user_id=user_id)
    root = ET.fromstring(ET.tostring(resp, method='xml'))
    username = root[0].findall('username')[0].text
    return username

def getUserRealname(flickr='', user_id=''):
    resp = flickr.people.getInfo(user_id=user_id)
    root = ET.fromstring(ET.tostring(resp, method='xml'))
    realname = root[0].findall('realname')
    if realname:
        realname = realname[0].text
    return realname

def saveXML(xml='', filename=''):
    print("Saving XML...", filename)
    with open(filename, 'w') as f:
        f.write(xml.decode('utf-8'))

def download(url='', filename=''):
    print("Downloading", url)
    urllib.request.urlretrieve(url, filename)

def generateTags(tags=[]):
    tagsdict = {}
    for tag in tags:
        if tag in tagsdict:
            tagsdict[tag] += 1
        else:
            tagsdict[tag] = 1
    tagslist = [[freq, tag] for tag, freq in tagsdict.items()]
    tagslist.sort(reverse=True)
    itemtags = ['Flickr', 'images', ]
    itemtags2 = []
    for freq, tag in tagslist[:tagslimit-len(itemtags)]:
        itemtags2.append(tag)
    itemtags2.sort()
    itemtags += itemtags2
    return itemtags

def main():
    #parse params
    userid = ''
    mode = 'usersetzips' #usersetzips (1 item per user, all sets in different zips in the same item); set (1 item per set); all (1 item per image or video)
    resume = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["userid=", "mode=", "resume"])
    except getopt.GetoptError:
        print('flickr2ia.py --userid=<NUMBER@NXX> --mode=<usersetzips> OPTIONAL[--resume]')
        sys.exit()
    for opt, arg in opts:
        if opt == '--userid':
            userid = arg
        elif opt == "--mode":
            mode = arg
        elif opt == "--resume":
            resume = True
    
    if not userid or not mode:
        print('flickr2ia.py --userid=<NUMBER@NXX> --mode=<usersetzips> OPTIONAL[--resume]')
        sys.exit()
    
    #login flickr
    with open('flickr.token', 'r') as f:
        api_key, api_secret = f.read().strip().splitlines()
    
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    print('Authenticate')
    if not flickr.token_valid(perms='read'):
        flickr.get_request_token(oauth_callback='oob')
        authorize_url = flickr.auth_url(perms='read')
        print(authorize_url)
        verifier = input(u'Verifier code: ')
        flickr.get_access_token(verifier)
    
    #create download directory
    if not os.path.exists(userid):
        os.mkdir(userid)
    os.chdir(userid)
    print('Changed directory to', os.getcwd())
    
    #which mode?
    if mode == 'usersetzips':
        userid_ = re.sub('@', '_', userid)
        itemid = "Flickr-user-%s" % (userid_)
        
        #download all the sets for this user
        print("Loading sets for user", userid)
        photosets = getUserPhotosets(flickr=flickr, user_id=userid)
        print(len(photosets)-1, "sets found for", userid)
        rows = []
        tags = []
        photosinset = []
        for photoset, photosetprops in photosets:
            print(photoset, photosetprops['title'], photosetprops['description'])
            flickrseturl = 'https://www.flickr.com/photos/%s/sets/%s' % (userid, photoset)
            if photoset:
                photosetdirname = '%s-%s' % (plain(photosetprops['title']), photoset)
            else:
                photosetdirname = '%s' % (plain(photosetprops['title']))
            photosetzipfilename = '%s.zip' % (photosetdirname)
            
            if photoset:
                row = '<tr><td><a href="%s">%s</a>%s</td><td><a href="../download/%s/%s">%s</a></td><td><a href="../download/%s/%s/"><img src="../download/%s/%s/thumb.jpg" /></a></td></tr>' % (flickrseturl, photosetprops['title'], photosetprops['description'] and ' - <i>%s</i>' % (photosetprops['description']) or '', itemid, photosetzipfilename, photosetprops['numphotos']+photosetprops['numvideos'], itemid, photosetzipfilename, itemid, photosetzipfilename)
            else:
                row = '<tr><td>%s</td><td><a href="../download/%s/%s">%s</a></td><td><a href="../download/%s/%s/"><img src="../download/%s/%s/thumb.jpg" /></a></td></tr>' % (photosetprops['title'], itemid, photosetzipfilename, 0, itemid, photosetzipfilename, itemid, photosetzipfilename)
            rows.append(row)
            
            if os.path.exists(photosetzipfilename) and resume:
                if photoset:
                    print("Skiping set... It exists a zip file", photosetzipfilename)
                    photos = getPhotosFromPhotoset(flickr=flickr, user_id=userid, photoset_id=photoset)
                    for photo, photoprops in photos.items():
                        photosinset.append(photo)
            else:
                if not os.path.exists(photosetdirname):
                    os.mkdir(photosetdirname)
                os.chdir(photosetdirname)
                print('Changed directory to', os.getcwd())
                
                if photoset:
                    #download all the photos for this set
                    photos = getPhotosFromPhotoset(flickr=flickr, user_id=userid, photoset_id=photoset)
                    print(len(photos.keys()), "files in set")
                    for photo, photoprops in photos.items():
                        xml = getPhotoInfoXML(flickr=flickr, photo_id=photo)
                        photofilename = '%s-%s.%s' % (plain(getPhotoTitle(xml=xml)), getPhotoId(xml=xml), getPhotoOriginalFormat(xml=xml))
                        photoxmlfilename = '%s-%s.xml' % (plain(getPhotoTitle(xml=xml)), getPhotoId(xml=xml))
                        download(url=photoprops['url_o'], filename=photofilename)
                        saveXML(xml=xml, filename=photoxmlfilename)
                        #thumb in zip
                        if photo == photosetprops['primary']:
                            download(url=photoprops['url_sq'], filename='thumb.jpg')
                            download(url=photoprops['url_m'], filename='../%s' % (photofilename))
                        tags += getPhotoTags(xml=xml)
                        photosinset.append(photo)
                else:
                    #download all the photos without a set
                    allphotos = getAllPhotosFromUser(flickr=flickr, user_id=userid)
                    photoswithoutaset = list(set(allphotos.keys()) - set(photosinset))
                    photoswithoutaset.sort()
                    print(len(photoswithoutaset), "files without a set")
                    for photo, photoprops in allphotos.items():
                        if photo in photoswithoutaset:
                            xml = getPhotoInfoXML(flickr=flickr, photo_id=photo)
                            photofilename = '%s-%s.%s' % (plain(getPhotoTitle(xml=xml)), getPhotoId(xml=xml), getPhotoOriginalFormat(xml=xml))
                            photoxmlfilename = '%s-%s.xml' % (plain(getPhotoTitle(xml=xml)), getPhotoId(xml=xml))
                            download(url=photoprops['url_o'], filename=photofilename)
                            saveXML(xml=xml, filename=photoxmlfilename)
                            tags += getPhotoTags(xml=xml)
                
                #zip
                subprocess.call('zip' + ' -r ../%s *' % (photosetzipfilename), shell=True)
                os.chdir('..')
                print('Changed directory to', os.getcwd())
        
        xml = getUserInfoXML(flickr=flickr, user_id=userid)
        saveXML(xml=xml, filename='userinfo.xml')
        
        #upload to IA
        itemtitle = "" # use itemid by default
        itemdate = datetime.datetime.now().strftime("%Y-%m-%d")
        itemoriginalurl = 'https://www.flickr.com/photos/%s/' % (userid)
        itemtags = generateTags(tags=tags)
        itemdesc = 'Images by Flickr user <a href="%s">%s</a>' % (itemoriginalurl, userid)
        userpathalias = getUserPathalias(flickr=flickr, user_id=userid)
        if userpathalias:
            itemdesc += " / " + userpathalias
        userusername = getUserUsername(flickr=flickr, user_id=userid)
        if userusername:
            itemdesc += " / " + userusername
        userrealname = getUserRealname(flickr=flickr, user_id=userid)
        if userrealname:
            itemdesc += " / " + userrealname
        itemdesc += '.\n\nImages metadata in .xml files.\n\n<table style="border: 1px solid grey;">\n<tr><th>Set</th><th>Files</th><th>Thumb</th></tr>\n%s\n</table>' % ('\n'.join(rows))
        #print(itemdesc)
        md = {
            'mediatype': 'images', 
            'collection': 'opensource_media', 
        }
        md2 = {
            'creator': itemoriginalurl, 
            #'title': itemtitle, 
            'description': itemdesc, 
            'last-updated-date': itemdate, 
            #'licenseurl': itemlicenseurl, 
            'originalurl': itemoriginalurl, 
        }
        if len(itemtags) > 2:
            md2['subject'] = '; '.join(itemtags)
        with open('itemdesc.txt', 'w') as f:
            f.write(itemdesc)
        item = get_item(itemid)
        zips = glob.glob("*.zip")
        thumbs = glob.glob("*.jpg")
        files = zips + thumbs + ['userinfo.xml', 'itemdesc.txt']
        print("Uploading", files)
        item.upload(files=files, metadata=md, verbose=True, queue_derive=False)
        print("Adding metadata", md2)
        item.modify_metadata(md2)
        print('You can find it in https://archive.org/details/%s' % (itemid))
    
    os.chdir('..')
    print('Changed directory to', os.getcwd())

if __name__ == '__main__':
    main()
