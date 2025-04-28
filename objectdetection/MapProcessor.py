import cv2
from matplotlib import pyplot as plt
from matplotlib import cm
from pytesseract import image_to_string
import pytesseract
import numpy as np
import json


class MapProcessor:
    def __init__(self, image_path: str):
        """
        Loads the image for later processing operations

        Parameters:
         image_path (str): The name of the image that will be processed
        """

        # Variables that will be initialized later in other functions
        self.filtered_contours = None
        self.min_area = None
        self.max_area = None
        self.all_contours = None
        self.cv2_image_blurred = None
        self.cv2_image_gray = None

        self.img_path = image_path
        self.cv2_image = cv2.imread(image_path)
        self.preprocess_image()
        # cv2.imshow("Thresholded Image", self.threshold_image)
        # cv2.imshow("Blurred Image", self.blur_image)
        # cv2.imshow("Median Image", self.median_image)
        # cv2.imshow("Otsu Image", self.otsu_threshold)
        # cv2.imshow("Inpainted Mask", self.inpainted_mask)
        # cv2.imshow("Bilateral Filtered Inpainted Mask", self.bilateral_inpainted_mask)
        cv2.imshow("Closed Bilateral Filtered Inpainted Mask", self.closed_bilateral_inpainted_mask)
#        cv2.imshow("Median Closed Bilateral Filtered Inpainted Mask", self.median_closed_bilateral_inpainted_mask)


        self.extract_contours()
        self.filter_contours()
        self.buildings = {"Buildings": []}

    def preprocess_image(self):
        """
        For use within the init, create a grayscale version of the image and creates another version that
        has gaussian blur applied
        """
        self.cv2_image_gray = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2GRAY)  # convert image into grayscale
        self.cv2_image_blurred = cv2.GaussianBlur(self.cv2_image_gray, (5, 5), 1)  # apply blur to image
        # self.threshold_image = cv2.adaptiveThreshold(self.cv2_image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,2)
        self.threshold_image = cv2.adaptiveThreshold(self.cv2_image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,11,2)
        self.median_image = cv2.medianBlur(self.threshold_image, 3)

        ret, self.otsu_threshold = cv2.threshold(self.cv2_image_gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        self.inpainted_mask = cv2.inpaint(self.threshold_image,self.otsu_threshold, 3, cv2.INPAINT_NS)
        self.bilateral_inpainted_mask = cv2.bilateralFilter(self.inpainted_mask, 9, 125, 125)

        # kernel_opening = np.ones((2,2),np.uint8)
        # self.opened_bilateral_inpainted_mask =  cv2.morphologyEx(self.bilateral_inpainted_mask, cv2.MORPH_CLOSE, kernel_opening)
        kernel = np.ones((3, 3), np.uint8)
        self.closed_bilateral_inpainted_mask = cv2.morphologyEx(self.bilateral_inpainted_mask, cv2.MORPH_CLOSE, kernel)
        self.median_closed_bilateral_inpainted_mask = cv2.medianBlur(self.closed_bilateral_inpainted_mask,5)
    def extract_contours(self):
        """For use in init, Apply canny edge detection and get all the contours that are found"""
        canny = cv2.Canny(self.median_closed_bilateral_inpainted_mask, 100, 200, True)  # apply canny to roi
        # Find contours
        self.all_contours = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    def filter_contours(self):
        """For use within init, filter contours in order to only get the corner vertices for shape detection
            also filters the image itself if it is detected as an object"""

        # First, determine max and min areas for thresholding
        self.max_area = self.cv2_image.shape[0] * self.cv2_image.shape[1] * 0.9
        self.min_area = 10

        # Second, create a filtered list
        self.filtered_contours = []
        for contour in self.all_contours:
            area = cv2.contourArea(contour)
            if self.min_area < area < self.max_area:
                epsilon = 0.04 * cv2.arcLength(contour, True)  # Adjust epsilon as needed. Lower=more detail
                approx = cv2.approxPolyDP(contour, epsilon, True)
                self.filtered_contours.append(approx)

    def extract_building_details(self):
        """Call this function to process the image and prepare the json data"""
        # for enumerating the building Ids
        current_id = 1

        for contour in self.filtered_contours:
            # Create temporary dict that will be added to the list
            building = {"Id": current_id}

            # Increment it
            current_id += 1

            # Get the bounding rectangle around the contour
            x, y, w, h = cv2.boundingRect(contour)
            #building["Shape"] = self.extract_shape(contour)

            building = self.extract_vertex_coordinates(contour, building)


            # Extract the region of interest (ROI) from the original image
            #roi, roi_grayscale = self.extract_roi(x, y, w, h)

            # print("Total edges: " + str(len(contour)))
            #
            # building["Height"] = self.extract_number(roi_grayscale, contour, [x,y,w,h])
            # building["Color"] = self.extract_color(roi, contour,[x,y,w,h])
            # print("The color for this region is: " + building["Color"])
            # Append the building data to the list
            self.buildings["Buildings"].append(building)

            # # Show the extracted ROI (optional)
            # cv2.imshow('ROI', 255 - thresh)
            # cv2.waitKey(0)


    def extract_vertex_coordinates(self, contour: list, building: dict):
        """For use withing the extract_building_details, gets the coordinates of the vertices in a group of vertices
        Parameters:
            contour (list): The group of vertices
            building (dict): The dict that will be appended
        Returns:
            building (dict): The new building dictionary
            """
        for count, vertex in enumerate(contour):
            building[f"V{count}"] = (int(vertex[0][0]), int(vertex[0][1]))
        return building

    def extract_roi(self, x, y, w, h):
        """For use within the extract_building_details, gets the image withing a bounding box
        Parameters:
            x: x coordinate
            y: y coordinate
            w: width of the bounding box
            h: height of the bounding box
        Returns:
            roi: Region of interest
            roi_grayscale: Region of interest in grayscale"""
        # roi = img[y+10:y + h-10, x+10:x + w-10]
        roi = self.cv2_image[y:y + h, x:x + w]
        #cv2.imshow("ex", roi)
        roi_grayscale = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        return roi, roi_grayscale

    def show_final(self):
        """Creates the environment
        of the picture and shows it"""
        cv2.drawContours(self.cv2_image, self.filtered_contours, -1, (0, 255, 0), 3)
        plt.subplot(1, 1, 1)
        plt.imshow(self.cv2_image, cmap=cm.bone)
        plt.show()


    def export_json(self):
        with open('result.json', 'w') as fp:
            json.dump(self.buildings, fp)