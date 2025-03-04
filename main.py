import cv2
from matplotlib import pyplot as plt
from matplotlib import cm
from pytesseract import image_to_string
import numpy as np
import json


# Opening image
img = cv2.imread("img_1.png")

# OpenCV opens images as BRG
# but we want it as RGB and
# we also need a grayscale
# version
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert roi into gray
Blur=cv2.GaussianBlur(gray,(5,5),1) #apply blur to roi
Canny=cv2.Canny(Blur,10,50) #apply canny to roi



#Find my contours
contours =cv2.findContours(Canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]

#If the image itself is found as an object it needs to be removed from the contours

#First, determine max and min areas for thresholding
max_area = img.shape[0] * img.shape[1] * 0.9
min_area = 100

#Second, create a filtered list
filtered_contours = []
for contour in contours:
    area = cv2.contourArea(contour)
    if min_area < area < max_area:
        epsilon = 0.04 * cv2.arcLength(contour, True) #Adjust epsilon as needed. Lower=more detail
        approx = cv2.approxPolyDP(contour, epsilon, True)
        filtered_contours.append(approx)

#Create a dictionary which will later be converted to json and sent to other subsystems
buildings = {"Buildings": []}

#for enumerating the building Ids
current_id = 1

for contour in filtered_contours:
    #Create dict that will be added to the list
    building = {}

    #Assign Id and increment it
    building["Id"] = current_id
    current_id += 1

    # Get the bounding rectangle around the contour
    x, y, w, h = cv2.boundingRect(contour)

    #The midway point between the corners indicate the coordinates of the center
    for count, vertex in enumerate(contour):
        building[f"XofV{count}"] = int(vertex[0][0])
        building[f"YofV{count}"] = int(vertex[0][1])

    # Extract the region of interest (ROI) from the original image
    #The roi is cropped to remove the bounding lines from the image, might implement a more robust algorithm for this later
    #roi = img[y+10:y + h-10, x+10:x + w-10]
    roi = img[y:y + h, x:x + w]
    cv2.imshow("ex", roi)
    roi_grayscale = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    #threshold for easier number detection
    _, thresh = cv2.threshold(roi_grayscale, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Perform OCR
    text = image_to_string(thresh, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789') # psm 7 for a single line of text
    inv_text = image_to_string(255-thresh, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')
    text_gray = image_to_string(roi_grayscale, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789') # psm 7 for a single line of text
    inv_text_gray = image_to_string(255-roi_grayscale, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')

    text_number = -1

    if text.strip():
        print(f"Detected number: {text.strip()}")
        text_number = text.strip()
    elif inv_text.strip():
        print(f"Detected number: {inv_text.strip()}")
        text_number = inv_text.strip()
    elif text_gray.strip():
        print(f"Detected number: {text_gray.strip()}")
        text_number = text_gray.strip()
    elif inv_text_gray.strip():
        print(f"Detected number: {inv_text_gray.strip()}")
        text_number = inv_text_gray.strip()
    else:
        print("Couldn't find number.")

    print("Total edges: " + str(len(contour)))

    building["Height"] = text_number
    #Append the building data to the list
    buildings["Buildings"].append(building)

    # Show the extracted ROI (optional)
    cv2.imshow('ROI', 255-thresh)
    cv2.waitKey(0)

# Creates the environment
# of the picture and shows it
cv2.drawContours(img, filtered_contours, -1, (0,255,0), 3)
plt.subplot(1, 1, 1)
plt.imshow(img, cmap=cm.bone)
plt.show()

with open('result.json', 'w') as fp:
    json.dump(buildings, fp)