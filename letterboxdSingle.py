'''
Portion of the Python Web Scraper for letterboxd. Used this file to develop single film image grab and saving
'''

import sys
import requests
from bs4 import BeautifulSoup


#Base URL for your diary
def image_link_func(links):
	image_links = []
	for link in links:
		URL = 'https://letterboxd.com' + link
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		poster = soup.find('div', class_= 'film-poster')
		image_link = poster.find('img', itemprop="image").get('src')
		image_links.append(image_link)