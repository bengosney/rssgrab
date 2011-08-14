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

import urllib
import os
import ConfigParser
from xml.dom.minidom import *

# read all the settings from the ini file
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

rsslist = Config.get("Main", "rsslist")
savepath = Config.get("Main", "savepath")

flist = file(rsslist)                       # load the rss feed list

for rssline in flist:                       # step through the list
    rssline = rssline.rstrip().split(',')   # slip the name and the url
    
    if not os.path.exists(savepath + rssline[0]):      # make the sub directory
        # if it doesn't exist
        os.makedirs(savepath + rssline[0])
    
    print "Checking " + rssline[0]

    dom = parse(urllib.urlopen(rssline[1])) # download the rssfeed

    listoffile = ""                         # reset list of files
    
    dlcount = 0    # reset download count for this podcast

    for node in dom.getElementsByTagName('item'):                                 # step through the rss feed
        pTitle = node.getElementsByTagName('title').item(0).childNodes.item(0).nodeValue    # get title, in a really nasty looking way

        pUrl = node.getElementsByTagName('enclosure').item(0).getAttribute('url')   # get the url

        pName = pTitle + os.path.splitext(pUrl)[1]    # Make file name

        fullpath = savepath + rssline[0] + "/" + pName   # make the full path for easy of reading
        
        listoffile = listoffile + "," + pName    # build a string of the file names to check deleting old podcasts
        
        if not os.path.exists(fullpath): # make sure we don't already have the file
            print "Downloading " + pName
            
            podcast = urllib.urlopen(pUrl)        # get the video file
            
            fout = file(fullpath,'w')           # open the output file
            fout.write(podcast.read())          # write the file
            fout.close()
    
            print "Downloaded"      

        # Limit the downloaded files
        dlcount = dlcount + 1    # incrament the downloaded count
        print "Downloaded: " + str(dlcount) + " of " + str(rssline[2])    # Print the count
        if dlcount == int(rssline[2]):    # Break if you've reached the download the limit
            break


    print "Cleaning up old podcasts"
    
    for root, dir, files in os.walk(savepath + rssline[0] + "/"):   # walk the podcast directory
        for tmp in files:
            if (listoffile.find(tmp) < 0):                          # check to see if we want the podcast or not
                print "removing " + tmp
                os.remove(savepath + rssline[0] + "/" + tmp)        # delete file if we don't want it
                                                   
    print rssline[0] + " is upto date" # close up and "stuff"
        
flist.close()
print "All Downloaded"
