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


class rssGrab :
	def grabVideo(self) :
		# read all the settings from the ini file
		Config = ConfigParser.ConfigParser()
		ConfigPath = os.path.dirname(os.path.abspath(__file__)) + "/config.ini"    # make sure the config path is correct
		Config.read(ConfigPath)

		rsslist = Config.get("Main", "rsslist")
		savepath = Config.get("Main", "savepath")

		flist = file(rsslist)                       # load the rss feed list

		for rssline in flist:                       # step through the list
		    if rssline[0] == '#':                   # allow for comments in the rss list
			continue

		    rssline = rssline.rstrip().split(',')   # split the name and the url
		    
		    if not os.path.exists(savepath + rssline[0]):      # make the sub directory
			os.makedirs(savepath + rssline[0])    # if it doesn't exist
		    
		    print "Checking " + rssline[0]

		    try:
			dom = parse(urllib2.urlopen(rssline[1])) # download the rssfeed
		    except:
			continue

		    listoffile = ""                         # reset list of files
		    
		    dlcount = 0    # reset download count for this podcast

		    for node in dom.getElementsByTagName('item'):                                 # step through the rss feed
			pTitle = node.getElementsByTagName('title').item(0).childNodes.item(0).nodeValue    # get title, in a really nasty looking way
			pUrl = node.getElementsByTagName('enclosure').item(0).getAttribute('url')   # get the url
			pSize = node.getElementsByTagName('enclosure').item(0).getAttribute('length')   # get the size for later
		

			pName = pTitle + os.path.splitext(pUrl)[1]    # Make file name
			fullpath = savepath + rssline[0] + "/" + pName   # make the full path for easy of reading
		
			listoffile = listoffile + "," + pName    # build a string of the file names to check deleting old podcasts

			# Try to get the file size
			try:
			    fSize = os.path.getsize(fullpath)    # if it can't find the file it throws an exception
			except:    # catch the exception...
			    fSize = 0    # set the size to zero

			print pName
		
			if int(fSize) != int(pSize):    # if the file doesn't excist or is the wrong size, go get it!
			    print "Downloading " + pName
			    
			    podcast = urllib2.urlopen(pUrl)        # get the video file
			    
			    try:
				fout = file(fullpath,'w')           # open the output file
				# read and write "line" by "line"
				for chunk in podcast:
				    fout.write(chunk)
				fout.close()
			    except:
				print "failed to download and save"
			      
			    print "Downloaded"      

			# limit the downloaded files
			dlcount = dlcount + 1    # incrament the downloaded count
			#print "Downloaded: " + str(dlcount) + " of " + str(rssline[2])    # Print the count
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


if __name__ == "__main__":
	rss = rssGrab()
	rss.grabVideo()
