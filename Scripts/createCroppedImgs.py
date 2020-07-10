#Author: Martin OLIVIER
#Date:  14 May 2020
#Creates cropped images containing on every object in the CSVs  along with the correct annotation in YOLO format
#We need to find every object that can be seen in the image and create correct annotations !

import csv
import numpy as np 
from PIL import Image
import cv2 
import tqdm 
import subprocess 

DSNAME = "annotations/"
CSVarray = [ "SpatialData/celticCSV_img.csv","SpatialData/kilnsCSV_img.csv", "SpatialData/barrowsCSV_img.csv"]
RES = 250 #Resolution of the image/2: 500 will create a 1000x1000 pxl image
JITTER = 100 #Move the image randomly withing these bounds (pixels)

seenArray = [] #Array containing objects that have already been annotated in an image

#Object types:
#Kilns = 0
#Celtic Fields = 1
#Barrows = 2

def findObjects(coords, imgName, imgCoords, debug):
    #Given coordinates, this function will find all the object present in the cropped image
    #And return them as a an array 
    #The array contains the coordinates of each objects + their type 
    objectArray = []
    xMinImg, xMaxImg, yMinImg, yMaxImg = imgCoords

    for csvName in CSVarray:#Read all the csv 
        #Set type
        if 'kilns' in csvName:
            objType = 0
        elif 'celtic' in csvName:
            objType = 1 
        elif 'barrows' in csvName:
            objType = 2 
    
        if debug == 1:
            print(csvName)
        #open and read csv 
        csvfile = open(csvName, newline='')
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(reader)#Skip the header !
        
        for row in reader:
            if row[3] == imgName:
               #Transform the coordinates from a GIS reference to an image reference
               #Note: The basis is flipped ! The origin is at the top left, instead of bottom left
               xMin = float(row[0].split(",")[0].strip('POLYGON ((').split(' ')[0])
               xMin = int(map(xMin, xMinImg, xMaxImg, 0, 10290))
               xMax = float(row[0].split(",")[2].split(' ')[0])
               xMax = int(map(xMax, xMinImg, xMaxImg, 0, 10290))

               yMin = float(row[0].split(",")[2].split(' ')[1])
               yMin = int(map(yMin, yMinImg, yMaxImg, 13140, 0))
               yMax = float(row[0].split(",")[0].strip('POLYGON ((').split(' ')[1])
               yMax = int(map(yMax, yMinImg, yMaxImg, 13140, 0))
               if debug == 1:
                   print("OBJ: ", xMin, xMax, yMin, yMax)
                   print("IMG: ", xMinImg, xMaxImg, yMinImg, yMaxImg)
               #Check if the bbox is inside the cropped image, and append to the output array if it is the case
               if coords[0] <= xMin <= coords[1] and  coords[0] <= xMax <= coords[1] and coords[2] <= yMin <= coords[3] and  coords[2] <= yMax <= coords[3]:
                   seenArray.append(row)
                   objectArray.append((xMin, xMax, yMin, yMax, objType))
    return objectArray 
    
def map(variable1, min1, max1, min2, max2):
    return min2+(max2-min2)*((variable1-min1)/(max1-min1))

def placeImg(coords, imgName):
    #Chose wether the image will go in test or train (80/20 split)
    if np.random.uniform(0,1) > 0.2:
        txt = open(DSNAME + "train.txt", "a+")
    else:
        txt = open(DSNAME + "test.txt", "a+")

    img = cv2.imread(imgName)
    imgArray = np.array(img)
    #Get information on the position of the image
    process = subprocess.Popen(['gdalinfo', imgName], stdout=subprocess.PIPE, stderr=subprocess.PIPE)#Get the location using gdalinfo
    out= process.communicate()[0]
    #Extract from the STDOUT
    xMinImg = float(str(out).split("Upper Left")[1].split(" ")[4].strip(','))
    xMaxImg = float(str(out).split("Lower Right")[1].split(" ")[3].strip(','))
    yMaxImg = float(str(out).split("Upper Left")[1].split(" ")[6].strip(')'))
    yMinImg = float(str(out).split("Lower Right")[1].split(" ")[5].strip(')'))

    imgCoords = (xMinImg, xMaxImg, yMinImg, yMaxImg)
    #Get the center coordinates of the box, and perform some jitter, then map w.r.t the image
    centerX = (coords[0] + coords[1])/2.0 + np.random.uniform(-JITTER, JITTER)
    centerX = int(map(centerX, xMinImg, xMaxImg, 0, 10290))
    centerY = (coords[2] + coords[3])/2.0 + np.random.uniform(-JITTER, JITTER)
    centerY = int(map(centerY, yMinImg, yMaxImg, 13140, 0))

    #print(centerX, centerY)
    #print(centerX-RES, centerY-RES)
    #print(centerX+RES, centerY+RES)
    #We need to check if the newly obtained box is inside the image. If it isnt we move the center so that every vertex sits inside
    if centerX-RES < 0:
        centerX += abs(centerX - RES)
    if centerY-RES < 0:
        centerY += abs(centerY - RES)
    if centerX+RES > 10290:
        centerX -= abs(centerX + RES - 10290) 
    if centerY+RES > 13140:
        centerY -= abs(centerY + RES - 13140 ) 

    #Get all the objects visibile in the image in a list
    objsImg = findObjects((centerX-RES, centerX+RES, centerY-RES, centerY+RES), imgName, imgCoords, 0)

    if len(objsImg) == 0:
        print('ERROR: no object found in the image !')
        objsImg = findObjects((centerX-RES, centerX+RES, centerY-RES, centerY+RES), imgName, imgCoords, 1)
        print(row)
    imgName = imgName.split("/")[2] #Remove the directory from the filename
    #Create a new filename that contains the position of the cropped image
    imgName = imgName[:5]+"_(" + str(centerX) + "," + str(centerY) + ").jpg"

    txtFile = open(DSNAME + imgName[:-4]+".txt", "a+") #Create and open a txt file with the same name as the image 

    #For all the visible object in the list, get their coordinates and transform them into YOLO format
    for obj in objsImg:
        centerXObj = (obj[0] + obj[1])/2.0 
        centerXObj = map(centerXObj, centerX-RES, centerX+RES, 0, 1)#Coordinates in yolo are in (0, 1]
        centerYObj = (obj[2] + obj[3])/2.0
        centerYObj = map(centerYObj, centerY-RES, centerY+RES, 0, 1)
        
        width  = (centerXObj - map(obj[0], centerX-RES, centerX+RES, 0, 1)) * 2.0
        height = (centerYObj - map(obj[3], centerY-RES, centerY+RES, 0, 1)) * 2.0
        #print(str(obj[4])+ ", " + str(centerXObj) + ", " + str(centerYObj) + ", " +str(width)+ ", "+ str(height))
        txtFile.write(str(obj[4])+ " " + str(centerXObj) + " " + str(centerYObj) + " " +str(width)+ " "+ str(height) + "\n")

    img = img[centerY-RES:centerY+RES, centerX-RES:centerX+RES] #Crop the image 

    txt.write("data/" + DSNAME + imgName+"\n") #Write the name of the image on the file containing the list of train/test image 
    cv2.imwrite(DSNAME + imgName, img) #Write to a new image

        
for csvName in CSVarray:#Read all the csv 
    with open(csvName, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        row_count = sum(1 for row in reader)-1  #Number of objects = number of rows - header
        csvfile.seek(0) #return to begining
        next(reader)#Skip the header !
        pbar = tqdm.tqdm(total=row_count) #Get ourselves a nice progressbar
        for row in reader:
           #if row in seenArray: #If we have already seen the object, goto next object
           #    continue 
           pbar.update(1)
           xMin = float(row[0].split(",")[0].strip('POLYGON ((').split(' ')[0])
           yMax = float(row[0].split(",")[0].strip('POLYGON ((').split(' ')[1])
           xMax = float(row[0].split(",")[2].split(' ')[0])
           yMin = float(row[0].split(",")[2].split(' ')[1])
           placeImg((xMin, xMax, yMin, yMax), row[3])
