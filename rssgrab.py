#!/usr/bin/env python

# Copyright Ben Gosney 2010
# bengosney@googlemail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import os
import ConfigParser
from xml.dom.minidom import *

# read all the settings from the ini file
Config = ConfigParser.ConfigParser()
# make sure the config path is correct
ConfigPath = os.path.dirname(os.path.abspath(__file__)) + "/config.ini"
Config.read(ConfigPath)

rsslist = Config.get("Main", "rsslist")
savepath = Config.get("Main", "savepath")

flist = file(rsslist)                       # load the rss feed list

for rssline in flist:                       # step through the list
    # allow for comments in the rss list
    if rssline[0] == '#':
        continue

    rssline = rssline.rstrip().split(',')   # split the name and the url

    if not os.path.exists(savepath + rssline[0]):      # make the sub directory
        os.makedirs(savepath + rssline[0])    # if it doesn't exist

    print "Checking " + rssline[0]

    try:
        dom = parse(urllib2.urlopen(rssline[1]))  # download the rssfeed
    except:
        continue

    listoffile = ""                         # reset list of files

    dlcount = 0    # reset download count for this podcast

    # step through the rss feed
    for node in dom.getElementsByTagName('item'):
        tmpNode = node.getElementsByTagName('title').item(0).childNodes.item(0)
        # get title, in a really nasty looking way
        pTitle = tmpNode.nodeValue
        tmpNode = node.getElementsByTagName('link').item(0).childNodes.item(0)
        pUrl = tmpNode.nodeValue  # get the url

        if node.getElementsByTagName('enclosure').length > 0:
            tmpNode = node.getElementsByTagName('enclosure').item(0)
            pUrl = tmpNode.getAttribute('url')
            pSize = tmpNode.getAttribute('length')
        else:
            fileHeaders = urllib2.urlopen(pUrl).headers  # get the file headers

            # see if the server has given us a file size
            if "Content-Length" in fileHeaders:
                pSize = int(fileHeaders.headers["Content-Length"])
            else:
                # if there's no size, set it to a negative number to make sure
                # we download the file in a min
                pSize = -1

        # Make file name
        pName = pTitle + os.path.splitext(pUrl)[1]
        # make the full path for easy of reading
        fullpath = savepath + rssline[0] + "/" + pName

        # build a string of the file names to check deleting old podcasts
        listoffile = listoffile + "," + pName

        # Try to get the file size
        try:
            # if it can't find the file it throws an exception
            fSize = os.path.getsize(fullpath)
        except:    # catch the exception...
            fSize = 0    # set the size to zero

        print pName

        # if the file doesn't excist or is too small, go get it!
        if int(fSize) < int(pSize):
            print "Downloading " + pName

            podcast = urllib2.urlopen(pUrl)        # get the video file
            CHUNK_SIZE = 16 * 1024

            try:
                with open(fullpath, 'w') as fout:
                    while True:
                        chunk = podcast.read(CHUNK_SIZE)
                        if not chunk: break
                        fout.write(chunk)
                        
                print "Downloaded"
            except:
                print "failed to download and save"

        # limit the downloaded files
        dlcount = dlcount + 1    # incrament the downloaded count
        # Break if you've reached the download the limit
        if dlcount == int(rssline[2]):
            break

    print "Cleaning up old podcasts"

    # walk the podcast directory
    for root, dir, files in os.walk(savepath + rssline[0] + "/"):
        for tmp in files:
            # check to see if we want the podcast or not
            if (listoffile.find(tmp) < 0):
                print "removing " + tmp
                # delete file if we don't want it
                os.remove(savepath + rssline[0] + "/" + tmp)

    print rssline[0] + " is upto date"  # close up and "stuff"

flist.close()
print "All Downloaded"
