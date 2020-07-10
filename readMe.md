This is the directory containing the data for the LiDAR object detection project
#Directories:
Data:
	Contains the spatial data e.g. the annotations that are used to create the dataset
yolo:
	Contains the config files for the yolo 
memoire:
	Contains the final report


# Automated LiDAR detection using YOLO

## Directories

## How to use
### Dataset Creation
Using the CSV databases containing the images in which the objects are located, construct the dataset using the createCroppedImgs.py

    python createCroppedImgs.py

The name and size of the image can be modified in the code. By default, the dataset is named lidarDetect, with image sized 500x500 pixels. 

### Darknet Compilation
Compile the latest darknet YOLOv4 included in the dataset. By default, this version does not include CV2 integration. Arch User Repositories offers an already compiled YOLOv4 that does include CV2. 
### Training
To train YOLO, you can use the already provided yolo/data/obj.name and yolo/data/obj.data which provide names for the objects along with some configuration needed for training. 

Place the train.txt and test.txt files which are located in the dataset which you have created in the data folder. 

To train, use the following command:
		`./darknet detector train data/obj.data cfg/YOUR_CFG_FILE.cfg yolov4.conv.137 -map`

A good number of epoch would be about 3*Number of Classes. Here, every model was trained for 10K epochs.
### Inference on one image
To run an inference on a single image:
`./darknet detector test data/obj.data cfg/YOUR_CFG_FILE.cfg backup/YOUR_CFG_FILE_best.weights data/test.jpg`

### Full dataset inference
To run an inference on all of the tif files, we must first construct a test dataset comprised of cropped 500x500 pixels images. 
Use the following command to do so:
`python cutDataset.py`
This will create a `testImages/` directory and put all of the cropped images inside, along with creating a text file named `testPaths.txt` containing the path to those images.

Use the following command to infer on the test images
`./darknet detector test yolo/data/obj.data yolo/cfg/yolov4-custom-GIOU-CV2.cfg yolo/backup/11June2020/yolov4-custom-GIOU-CV2_best.weights -dont_show -ext_output < testPaths.txt > results.txt`

### GIS Integration
Finally, we can use the coordinates of the detected object for use in a GIS. 
Run the following command:
`python detectionToCSV.py`
This will take the result.txt files and create 3 CSV database for each detect objects. Each row of this database contains the polygon coordinates in WKT, the confidence of detection and the class.

#Various notes:
	The reference on the SIG is flipped on the y axis compared to the image (top down -> down top)
	The dataset is not completely clean: for example there are multiple instances of barrows being covered twice or more. This WILL cause issues down the line. Need to clean this, but hard to compare between CSV and GIS, also hard to automatise because of natural occlusion issues...  
