# 29 June 2002
# Author; Martin OLIVIER
# Segment all raw images in the dataset into 500x500 px images

import os
import cv2
import math

folderName = 'testImages/'

directories = [x[0] for x in os.walk('../Data/LiDAR files')]#List all directories 
count = 0

textFile = open('testPaths.txt', 'r+')

for img in directories[1:]:
    count += 1
    imgName = "../Data/LiDAR files/" + img + "/" + img.split('/')[1]+"_SLRM_clip.tif"
    print("Loading ", imgName)
    img = cv2.imread(imgName, cv2.IMREAD_GRAYSCALE)
    for i in range(0, math.floor(img.shape[0]/500)):
        for j in range(0, math.floor(img.shape[1]/500)):
            imgArray = img[i*500:(i+1)*500,j*500:(j+1)*500]
            coords = '('+ str(i*500) + ',' + str((i+1)*500) + ',' + str(j*500) + ',' + str((j+1)*500) + ')'
            #print(coords, imgArray.shape)
            textFile.write(folderName + imgName[18:-4] + coords + '.jpg' + '\n')
            cv2.imwrite(folderName + imgName[18:-4] + coords + '.jpg', imgArray) 

