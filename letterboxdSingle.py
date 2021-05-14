'''
Portion of the Python Web Scraper for letterboxd. Used this file to develop single film image grab and saving
'''

import sys
import os
from PIL import Image as image

def makeimages(image_count, image_dir, final_image_dir:
	image_total = len(os.listdir(image_dir))
	

imagestart = 1
images = 4
file_path = 'C:\\Users\\chris\\Desktop\\testfolder'
imagecount = len(os.listdir('C:\\Users\\chris\\Desktop\\testfolder'))

im = image.open(os.listdir(path)[0])
#Make Black Filler Image
black = image.new('RGB', im.size, (0,0,0))

black.save('C:\\Users\\chris\\Desktop\\testfolder\\black.jpg')

for pic in range(imagestart, imagestart-1