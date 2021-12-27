"""
Python Web Scraper for letterboxd
"""
import sys
import getpass
import math
import requests
from bs4 import BeautifulSoup
import os
import shutil
from PIL import Image as ImageLib

'''

Functions

'''

# setting up local folder structure for storing of images. Will be gotten rid of in future versions in favor of only holding 1 image at a time and appending to final images
def system_setup():
    # getting username for file locations
    username = getpass.getuser()

    # creating path for image staging and final images
    if sys.platform == 'darwin':
        staging_location = '/Users/' + username + '/Desktop/TempImageHolder'
        final_location = '/Users/' + username + '/Desktop/FinalImages'
    elif sys.platform == 'win32':
        staging_location = 'C:\\Users\\' + username + '\\Desktop\\TempImageHolder'
        final_location = 'C:\\Users\\' + username + '\\Desktop\\FinalImages'

    # checking if the directory already exists and clearing it if it does
    if os.path.exists(staging_location):
        shutil.rmtree(staging_location)
    os.mkdir(staging_location)
    if os.path.exists(final_location):
        shutil.rmtree(final_location)
    os.mkdir(final_location)

    return staging_location, final_location


# given the url of a letterboxd diary returns the number of pages the entries will be spread over
def page_count(diary_url):
    web_page = requests.get(diary_url)

    soup = BeautifulSoup(web_page.content, 'html.parser')

    # Get the total Number of entries
    results = str(soup.find('h2', class_='ui-block-heading'))
    start = results.find('logged ') + 7
    end = results.find('entries') - 1
    diary_entries = int(results[start:end])

    # Calculate the number of pages
    diary_pages = math.ceil(diary_entries / 50)

    return diary_pages, diary_entries


def film_link_func(base_link, pages):
    link_list = []
    for page in range(1, pages + 1):
        URL = base_link + '/page/' + str(page)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        for link in soup.find_all('td'):
            if link.has_attr('data-film-link'):
                link_list.append(link.get('data-film-link'))
        print("done with page " + str(page))
    return link_list


def image_link_func(image_links):
    link_array = []
    for link in image_links:
        image_address = 'https://letterboxd.com' + link
        page = requests.get(image_address)
        soup = BeautifulSoup(page.content, 'html.parser')
        poster = soup.find('div', class_='film-poster')
        image_link = poster.find('img', itemprop='image').get('src')
        link_array.append(image_link)

    return link_array


def get_image_func(links, location):
    for x, link in enumerate(links, 1):
        r = requests.get(link)
        open(os.path.join(location, str(x) + '.jpg'), 'wb').write(r.content)


def make_images(image_count, image_dir, final_image_dir):
    image_total = len(os.listdir(image_dir))

    poster_size = []
    assigned = 0
    for x in range(image_count - 1):
        temp = math.ceil(math.sqrt((image_total - assigned) / (image_count - x))) ** 2
        assigned += temp
        poster_size.append(temp)

    poster_size.append(image_total - assigned)

    used = 0
    for x in range(image_count):
        image = image_build(image_dir, used, poster_size[x])
        image.save(os.path.join(final_image_dir, str(x) + '.jpg'))
        used += poster_size[x]

    return poster_size


def image_build(file_path, used, images):
    image_start = used + 1

    im = ImageLib.open(os.path.join(file_path, os.listdir(file_path)[0]))

    width = im.size[0]
    height = im.size[1]
    if images + math.ceil(math.sqrt(images)) < math.ceil(math.sqrt(images))**2:
        fill_height = height * (math.ceil(math.sqrt(images)) - 1)
    else:
        fill_height = height * math.ceil(math.sqrt(images))
    # Make Black Filler Image
    fill_image = ImageLib.new('RGB', (width * math.ceil(math.sqrt(images)), fill_height), (0, 0, 0))

    fill_image.save(os.path.join(file_path, 'fill.jpg'))

    for pic in range(0, images):
        x = (pic % math.ceil(math.sqrt(images))) * width
        y = (math.floor(pic / math.ceil(math.sqrt(images)))) * height
        main = ImageLib.open(os.path.join(file_path, 'fill.jpg'))
        main.paste(ImageLib.open(os.path.join(file_path, str(image_start + pic) + '.jpg')), (x, y))
        main.save(os.path.join(file_path, 'fill.jpg'))

    main = ImageLib.open(os.path.join(file_path, 'fill.jpg'))
    return main.resize((width * 4, int(height * 4 * (fill_height / (height * math.ceil(math.sqrt(images)))))))


'''

Running code for the script

'''

# Check for year parameter
if len(sys.argv) > 2:
    year = sys.argv[2]
else:
    year = '2021'

# Base URL for your diary
url = 'https://letterboxd.com/' + sys.argv[1] + '/films/diary/for/' + year

# get teh number of pages
pages, entries = page_count(url)

# Test print statement to check entries and page number logic
print(str(entries) + ' entries spread over ' + str(pages) + ' page(s)')

# get the film individual pages
film_pages = film_link_func(url, pages)
print('Film Page Links: DONE')

poster_links = image_link_func(film_pages)

# print(*image_links, sep = "\n")
print('Film Poster Links: DONE')

temp, final = system_setup()

get_image_func(poster_links, temp)

print('Film Poster Downloads: DONE')

images = make_images(4, temp, final)

print(images)
