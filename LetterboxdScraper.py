'''
Python Web Scraper for letterboxd
'''
import sys
import getpass
import math
import requests
from bs4 import BeautifulSoup
import os
import shutil
from PIL import Image as image

'''

Functions

'''

def system_setup():
	#getting username for file locations
	username = getpass.getuser()

	#creating path for image staging and final images
	if sys.platform == 'darwin':
		staginglocation = '/Users/'+username+'/Desktop/TempImageHolder'
		finallocation = '/Users/'+username+'/Desktop/FinalImages'
	elif sys.platform == 'win32':
		staginglocation = 'C:\\Users\\'+username+'\\Desktop\\TempImageHolder'
		finallocation = 'C:\\Users\\'+username+'\\Desktop\\FinalImages'
	
	#checking if the directory already exsists and clearing it if it does
	if os.path.exists(staginglocation):
		shutil.rmtree(staginglocation)
	os.mkdir(staginglocation)
	if os.path.exists(finallocation):
		shutil.rmtree(finallocation)
	os.mkdir(finallocation)

	return staginglocation, finallocation

#given the url of a letterboxd diary returns the number of pages the entries will be spread over
def page_count(url):
	page = requests.get(url)

	soup = BeautifulSoup(page.content, 'html.parser')

	# Get the total Number of entries
	results = str(soup.find('h2', class_='ui-block-heading'))
	start = results.find('logged ') + 7
	end = results.find('entries') - 1
	entries = int(results[start:end])

	# Calculate the number of pages
	pages = math.ceil(entries/50)

	return pages, entries


def film_link_func(base_link, pages):
	link_list = []
	for page in range(1, pages+1):
		URL = base_link+'/page/'+str(page)
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		for link in soup.find_all('td'):
			if link.has_attr('data-film-link'):
				link_list.append(link.get('data-film-link'))
		print("done with page "+str(page))
	return link_list

def image_link_func(links):
	image_links = []
	for link in links:
		URL = 'https://letterboxd.com' + link
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		poster = soup.find('div', class_= 'film-poster')
		image_link = poster.find('img', itemprop="image").get('src')
		image_links.append(image_link)

	return image_links

def get_image_func(links, location):
	
	for x, link in enumerate(links,1):
		r = requests.get(link)
		open(os.path.join(location, str(x)+'.jpg'), 'wb').write(r.content)

def makeimages(image_count, image_dir, final_image_dir):
	image_total = len(os.listdir(image_dir))

	#Make Black Filler Image
	im = image.open(os.path.join(image_dir,os.listdir(image_dir)[0]))
	black = image.new('RGB', im.size, (0,0,0))
	black.save(os.path.join(image_dir, 'black.jpg'))

	return image_total


'''

Running code for the script

'''

#Check for year paramater
if len(sys.argv) > 2:
	year = sys.argv[2]
else:
	year = '2021'

#Base URL for your diary
url = 'https://letterboxd.com/'+sys.argv[1]+'/films/diary/for/'+year

#get teh number of pages
pages, entries = page_count(url)

#Test print statment to check entries and page number logic
print(str(entries) + ' entires spread over '+ str(pages) +' page(s)')

#get the film individual pages
film_pages = film_link_func(url, pages)
print('Film Page Links: DONE')

image_links = image_link_func(film_pages)

#print(*image_links, sep = "\n")
print('Film Poster Links: DONE')

temp, final = system_setup()

get_image_func(image_links, temp)

print('Film Poster Downloads: DONE')

images = makeimages(4, temp, final)

print(images)