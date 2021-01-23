'''
Python Web Scraper for letterboxd
'''
import sys
import math
import requests
from bs4 import BeautifulSoup

def film_link_func(base_link, pages):
	link_list = []
	for page in range(1, pages+1):
		URL = base_link+str(page)
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


#Check for year paramater

if len(sys.argv) > 2:
	year = sys.argv[2]
else:
	year = '2020'

#Base URL for your diary
mainlink= 'https://letterboxd.com/'+sys.argv[1]+'/films/diary/for/'+year+'/page/'
URL = 'https://letterboxd.com/'+sys.argv[1]+'/films/diary/for/'+year
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

# Get the total Number of entries

results = str(soup.find('h2', class_='ui-block-heading'))

start = results.find('logged ') + 7

end = results.find('entries') - 1

entries = int(results[start:end])

# Calculate the number of pages
pages = math.ceil(entries/50)

#Test print statment to check entries and page number logic
print(str(entries) + ' entires spread over '+ str(pages) +' page(s)')

film_pages = film_link_func(mainlink, pages)

print(film_pages)

image_links = image_link_func(film_pages)

print(*image_links, sep = "\n")