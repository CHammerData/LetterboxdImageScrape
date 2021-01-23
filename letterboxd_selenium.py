'''
Python Web Scraper for letterboxd
'''
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
import math
import requests
from bs4 import BeautifulSoup
import time

#Check for year paramater

if len(sys.argv) > 2:
	year = sys.argv[2]
else:
	year = '2020'

#Base URL for your diary
crawler = webdriver.Chrome()

URL = 'https://letterboxd.com/'+sys.argv[1]+'/films/diary/for/'+year
crawler.get(URL)
crawler.execute_script("window.scrollTo(0,document.body.scrollHeight)")
time.sleep(5)
soup = BeautifulSoup(crawler.page_source, "lxml")

crawler.close()

# Get the total Number of entries

results = str(soup.find('h2', class_='ui-block-heading'))

start = results.find('logged ') + 7

end = results.find('entries') - 1

entries = int(results[start:end])

# Calculate the number of pages
pages = math.ceil(entries/50)

#Test print statment to check entries and page number logic
#print(str(entries) + ' entires spread over '+ str(pages) +' page(s)')

#print(str(soup.find('td', class_='td-film-details').find('div').get('data-film-link')))

for imagelink in soup.find_all('td', class_='td-film-details'):
	print(imagelink.find('div').get('data-poster-url'))

crawler.quit()