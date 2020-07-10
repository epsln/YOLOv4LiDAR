#AUTHOR: Martin OLIVIER
#Date  : 13 May 2020
#This is a simple script aimed at creating the bounding box of the annotated objects on the full size images
#Problem: the location of the cropped image is not known, nor is the location of the bbox on the fullsize tif
#Solution: Extract the location of the polygons from the .shp files . Those locations are relative to the GIS file
#so we need to first find in which images they are, then transform then into image relative coordinates
#Outputs a csv file containing both the original position of the objects and their image

import os
import cv2
import numpy as np
import csv
import subprocess 

csvName = "kilnsCSV" #Modify this to use the correct CSV 
directories = [x[0] for x in os.walk('../Data/LiDAR files')]#List all directories 

coordsArray = [] #Array of tuple containing (xMin, xMax, yMin, yMax, imgName) for all the full size images 
for img in directories[1:]:
    imgName = img + "/" + img.split('/')[1]+"_SLRM_clip.tif"

    #Get information on the position of the image using gdalinfo
    process = subprocess.Popen(['gdalinfo', imgName], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out= process.communicate()[0]
    #Extract from the STDOUT
    xMin= float(str(out).split("Upper Left")[1].split(" ")[4].strip(','))
    yMax= float(str(out).split("Upper Left")[1].split(" ")[6].strip(')'))
    xMax= float(str(out).split("Lower Right")[1].split(" ")[3].strip(','))
    yMin= float(str(out).split("Lower Right")[1].split(" ")[5].strip(')'))
    print(xMin, xMax, yMin, yMax)
    coordsArray.append((xMin, xMax, yMin, yMax, imgName))

def findImg(coordsObj):
    print(coordsObj)
    for coord in coordsArray:
        (xMin, xMax, yMin, yMax) = coord[:-1]
        if  xMin <= coordsObj[0] <=  xMax and  xMin <= coordsObj[1] <=  xMax and  yMin <= coordsObj[2] <=  yMax and yMin <= coordsObj[3] <=  yMax:
            return coord[4] 
            

writeCSV = open(csvName+'_img.csv', mode='w', newline='')#open new file for writing
writer = csv.writer(writeCSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)#Prepare writer

with open(csvName + '.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    header = next(reader)
    header.append('TIF IMAGE')#Add a column to the csv
    writer.writerow(header)  
    for row in reader:#Extract the coordinates from the (not too well constructed) CSV
       xMin = float(row[0].split(",")[0].strip('POLYGON ((').split(' ')[0])
       yMax = float(row[0].split(",")[0].strip('POLYGON ((').split(' ')[1])
       xMax = float(row[0].split(",")[2].split(' ')[0])
       yMin = float(row[0].split(",")[2].split(' ')[1])
       row[0] = row[0][0:]#delete some unwanted parts
       row.append(findImg((xMin, xMax, yMin, yMax)))
       writer.writerow(row)  
    
