'''
Portion of the Python Web Scraper for letterboxd. Used this file to develop single film image grab and saving
'''

import sys
import requests
from bs4 import BeautifulSoup
import os

def get_image_func(links):
	# Fetch username and desktop local
	username = os.getlogin()
	#Create temporary file for images
	location = 'C:\\Users\\'+username+'\\Desktop\\TempImageHolder'
	os.mkdir(location)
	x=1
	for link in links:
		r = requests.get(link)
		open(location'\\'+x+'.jpg', 'wb').write(r.content)
		x++