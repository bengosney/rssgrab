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
from xml.dom.minidom import parse

# read all the settings from the ini file
Config = ConfigParser.ConfigParser()
Config.read("config.ini")    # might want to make this a literal path if your running from a crontab

rsslist = Config.get("Main", "rsslist")
savepath = Config.get("Main", "savepath")

flist = file(rsslist)                       # load the rss feed list

for rssline in flist:                       # step through the list
    rssline = rssline.rstrip().split(',')   # slip the name and the url
    
    if not os.path.exists(savepath + rssline[0]):      # make the sub directory if it doesn't exist
        os.makedirs(savepath + rssline[0])
    
    print "Checking " + rssline[0]

    dom = parse(urllib.urlopen(rssline[1]))    # download the rss list
    
    listoffile = ""                                 # reset list of files
    
    for node in dom.getElementsByTagName('enclosure'):                                 # step through the rss feed
        fn = node.getAttribute('url')
        fullpath = savepath + rssline[0] + "/" + os.path.basename(fn)   # make the full path for easy of reading
        
        listoffile = listoffile + "," + os.path.basename(fn)    # build a string of the file names to check deleting old podcasts
        
        if not os.path.exists(fullpath): # make sure we don't already have the file
            print "Downloading " + fn
            
            podcast = urllib.urlopen(fn)        # get the video file
            
            fout = file(fullpath,'w')           # open the output file
            fout.write(podcast.read())          # write the file
            fout.close()
    
            print "Downloaded"      
    print "Cleaning up old podcasts"
    
    for root, dir, files in os.walk(savepath + rssline[0] + "/"):   # walk the podcast directory
        for tmp in files:
            if (listoffile.find(tmp) < 0):                          # make sure the podcast is still in the feed
                print "removing " + tmp
                os.remove(savepath + rssline[0] + "/" + tmp)        #delete file
                                                   
    print rssline[0] + " is upto date" # close up and "stuff"
        
flist.close()
print "All Downloaded"