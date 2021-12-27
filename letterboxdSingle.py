"""
Portion of the Python Web Scraper for letterboxd. Used this file to develop single film image grab and saving
"""

import sys
import os
import math
from PIL import Image

image_start = 1
images = 100
file_path = '/Users/overlordHAMMER/Desktop/TempImageHolder'
imagecount = len(os.listdir('/Users/overlordHAMMER/Desktop/TempImageHolder'))

im = Image.open(os.path.join(file_path, os.listdir(file_path)[0]))

width = im.size[0]
height = im.size[1]
# Make Black Filler Image
black = Image.new('RGB', (width * math.ceil(math.sqrt(images)), height * math.ceil(math.sqrt(images))), (0, 0, 0))

black.save(os.path.join(file_path, 'black.jpg'))

for pic in range(0, images):
    x = (pic % math.ceil(math.sqrt(images))) * width
    y = (math.floor(pic / math.sqrt(math.ceil(images)))) * height
    main = Image.open(os.path.join(file_path, 'black.jpg'))
    main.paste(Image.open(os.path.join(file_path, str(image_start + pic) + '.jpg')), (x, y))
    main.save(os.path.join(file_path, 'black.jpg'))

main = Image.open(os.path.join(file_path, 'black.jpg'))
new = main.resize((width * 4, height * 4))
new.save(os.path.join(file_path, 'black.jpg'))
