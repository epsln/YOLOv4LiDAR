#Author: Martin OLIVIER
#Date : 08 July 2020
#Creates a database of detections for use in GIS 

import csv
import re 
import subprocess 

resultFile = open("result.txt", 'r')

barrows = open('barrowsDetect.csv', mode='w', newline='')#open new file for writing
kilns   = open('kilnsDetect.csv', mode='w', newline='')
cfields = open('cFieldsDetect.csv', mode='w', newline='')

barrows.write("WKT,confidence,detection\n")
kilns.write("WKT,confidence,detection\n")
cfields.write("WKT,confidence,detection\n")

def map(variable1, min1, max1, min2, max2):
    return min2+(max2-min2)*((variable1-min1)/(max1-min1))

def getGlobalCoords(coordsImg, fullImgName, coordsObj):
    coordsInImg = (coordsImg[0]+coordsObj[0], coordsImg[1]+coordsObj[1] ,coordsImg[0]+coordsObj[2], coordsImg[1]+coordsObj[3])
    print(coordsObj, coordsImg, coordsInImg)

    process = subprocess.Popen(['gdalinfo', "../LiDAR files/"+fullImgName.split('_')[0]+'/'+ fullImgName + '.tif'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)#Get the location using gdalinfo
    out = process.communicate()[0]
    #Extract from the STDOUT
    xMinImg = float(str(out).split("Upper Left")[1].split(" ")[4].strip(','))
    xMaxImg = float(str(out).split("Lower Right")[1].split(" ")[3].strip(','))
    yMaxImg = float(str(out).split("Upper Left")[1].split(" ")[6].strip(')'))
    yMinImg = float(str(out).split("Lower Right")[1].split(" ")[5].strip(')'))
    print(fullImgName, xMinImg, xMaxImg, yMinImg, yMaxImg)
    out = [0,0,0,0]
    out[0] = map(coordsInImg[0], 0, 10290, xMinImg, xMaxImg)
    out[1] = map(coordsInImg[1], 13140, 0, yMinImg, yMaxImg)
    out[2] = map(coordsInImg[2], 0, 10290, xMinImg, xMaxImg)
    out[3] = map(coordsInImg[3], 13140, 0, yMinImg, yMaxImg)
    print(out)
    return out 

i = 0
lengthFile = 0
for line in resultFile:
    lengthFile += 1
resultFile.seek(0)
for line in resultFile:
    #print("[", i, "/", lengthFile, "]")
    if "Enter" in line:
        imageName = line.split(' ')[3][:-1]
        xImg = int(line.split('(')[1].split(',')[0])
        yImg = int(line.split('(')[1].split(',')[2])
        coordsImg = (yImg, xImg)
        fullImgName = line.split('/')[1].split('(')[0]
    elif "width" in line:
        coords = re.findall(r'\d+', line)
        confidence = int(coords[0])
        left_x  = int(coords[1])
        top_y   = int(coords[2])
        width   = int(coords[3])
        height  = int(coords[4])
        right_x = left_x + width
        bott_y  = top_y + height
        coordsObj = (left_x, top_y, right_x, bott_y)
        if "barrows" in line:
            classObj = 'barrow'
            csvFile = barrows; 
        if "celtic" in line:
            classObj = 'celtic_field'
            csvFile = cfields; 
        if "kiln" in line:
            classObj = 'charcoal_kiln'
            csvFile = kilns; 
        if height > 10 and width > 10 and height/width < 5:
            coords = getGlobalCoords(coordsImg, fullImgName, coordsObj)
            if confidence > 50:
                print('gud')
            row = '"POLYGON (('+ str(coords[0]) + ' ' + str(coords[1]) + ','\
                               + str(coords[2]) + ' ' + str(coords[1]) + ','\
                               + str(coords[2]) + ' ' + str(coords[3]) + ','\
                               + str(coords[0]) + ' ' + str(coords[3]) + ','\
                               + str(coords[0]) + ' ' + str(coords[1]) + '))",'\
                               + str(confidence) + ','\
                               + classObj + "\n"
            csvFile.write(row)
    i+=1
