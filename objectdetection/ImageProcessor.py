import cv2
from matplotlib import pyplot as plt
from matplotlib import cm
from pytesseract import image_to_string
import numpy as np
import json


class ImageProcessor:
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

    def extract_contours(self):
        """For use in init, Apply canny edge detection and get all the contours that are found"""
        canny = cv2.Canny(self.cv2_image_blurred, 10, 50)  # apply canny to roi
        # Find contours
        self.all_contours = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    def filter_contours(self):
        """For use within init, filter contours in order to only get the corner vertices for shape detection
            also filters the image itself if it is detected as an object"""

        # First, determine max and min areas for thresholding
        self.max_area = self.cv2_image.shape[0] * self.cv2_image.shape[1] * 0.9
        self.min_area = 100

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
            building = self.extract_vertex_coordinates(contour, building)

            # Extract the region of interest (ROI) from the original image
            roi, roi_grayscale = self.extract_roi(x, y, w, h)

            print("Total edges: " + str(len(contour)))

            building["Height"] = self.extract_number(roi_grayscale, contour, [x,y,w,h])
            building["Color"] = self.extract_color(roi, contour,[x,y,w,h])
            print("The color for this region is: " + building["Color"])
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
            building[f"XofV{count}"] = int(vertex[0][0])
            building[f"YofV{count}"] = int(vertex[0][1])
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

    def extract_number(self, roi_grayscale, contour, bounding_box):
        """Extracts the number from the region of interest and returns it
        Parameters:
            roi_grayscale: Region of interest in grayscale
            contour: The list of vertices of the corners, used for removing the edges
        Returns:
            text_number: The number that is found"""

        def preprocess_image(img_temp):
            """Apply preprocessing techniques to improve OCR accuracy."""
            # Apply Gaussian Blur to reduce noise
            blurred = cv2.GaussianBlur(img_temp, (5, 5), 0)

            # Apply adaptive thresholding for better contrast
            adaptive_thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            return adaptive_thresh

        # Preprocess the ROI
        processed_img = preprocess_image(roi_grayscale)
        processed_img = self.remove_edges(processed_img, contour,bounding_box)

        # Try different versions (original, thresholded, inverted)
        versions = [
            processed_img
        ]
        cv2.imshow("processed_img", processed_img)
        cv2.waitKey(0)

        text_number = None

        for img in versions:
            text = image_to_string(img, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789').strip()

            if text:
                print(f"Detected number: {text}")
                text_number = text
                break  # Stop once we successfully detect a number

        if text_number is None:
            print("Couldn't find number.")

        return text_number

    def extract_color(self, roi, contour, bounding_box):
        """
        Extracts the dominant color of the building within the ROI.

        Args:
            roi: The region of interest (ROI) image.
            contour: The contour of the building.
            bounding_box: [x, y, w, h] of the bounding box.

        Returns:
            A string representing the dominant color (e.g., "red", "blue", "gray").
        """

        if roi is None or roi.size == 0:
            return "#000000"  # Return black if ROI is empty

        resized_roi = cv2.resize(roi, (100, 100))

        # Calculate the average color
        average_color_bgr = np.mean(resized_roi, axis=(0, 1))

        # Convert BGR to RGB
        average_color_rgb = average_color_bgr[::-1]

        # Convert RGB to hex
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(average_color_rgb[0]), int(average_color_rgb[1]),
                                                 int(average_color_rgb[2]))

        return hex_color

    def show_final(self):
        """Creates the environment
        of the picture and shows it"""
        cv2.drawContours(self.cv2_image, self.filtered_contours, -1, (0, 255, 0), 3)
        plt.subplot(1, 1, 1)
        plt.imshow(self.cv2_image, cmap=cm.bone)
        plt.show()

    def remove_edges(self, roi_grayscale, corners, bounding_box, edge_thickness=10):
        """
        Removes edges from an object in an ROI by using the object's corner coordinates.

        Parameters:
            roi_grayscale: The extracted region of interest (grayscale).
            corners: List of (X, Y) corner coordinates from the original image.
            bounding_box: (x, y, w, h) - Bounding box of the ROI in the original image.

        Returns:
            roi_no_edges: The ROI with edges removed.
        """
        # Extract bounding box details
        x, y, w, h = bounding_box

        # Convert corner coordinates to ROI-relative coordinates
        relative_corners = np.array(corners) - np.array([x, y])

        # Create a white mask
        mask = np.ones_like(roi_grayscale, dtype=np.uint8) * 255

        # Ensure the relative_corners are properly reshaped for OpenCV
        pts = relative_corners.reshape((-1, 1, 2)).astype(np.int32)

        # Fill the shape with white, then draw the edges in black
        cv2.fillPoly(mask, [pts], 255)  # Fill with white
        cv2.polylines(mask, [pts], isClosed=True, color=0, thickness=edge_thickness)  # Draw edges in black


        # Apply the mask to remove edges while keeping the inside intact
        roi_no_edges = cv2.bitwise_and(255-roi_grayscale, mask)
        filtered_roi = cv2.medianBlur(roi_no_edges,3)
        filtered_inv = 255-filtered_roi
        # Create a kernel for dilation (adjust the size and shape as needed)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # Example 3x3 rectangular kernel

        # Dilate the binary image
        dilated_img = cv2.dilate(filtered_inv, kernel, iterations=1)
        eroded_img = cv2.erode(dilated_img, kernel, iterations=1)


        return eroded_img

    def export_json(self):
        with open('result.json', 'w') as fp:
            json.dump(self.buildings, fp)
