# Lane Detection using Edge Detection and Hough Transform

## Overview
This project implements a lane detection algorithm using classical computer vision techniques. The goal is to simulate how autonomous vehicles detect lane markings from road images.

The system processes 10 road scene images and detects the left and right lane boundaries. The detected lane lines are then overlaid onto the original images, and the lane center is optionally marked.

The algorithm uses:

- Canny Edge Detection
- Hough Line Transform
- Region of Interest (ROI) masking
- Color filtering for white lane markings
- Morphological operations to strengthen lane features

All images are processed using **a single Python program**, as required by the assignment.

---

## Repository Structure

lane-detection/
│
├── images/
│ ├── frame1.jpg
│ ├── frame2.jpg
│ ├── ...
│ └── frame10.jpg
│
├── output/
│ ├── output_frame1.jpg
│ ├── output_frame2.jpg
│ ├── ...
│ └── output_frame10.jpg
│
├── lane_detection_model.py
└── README.md

---


### Folder Description

**images/**
- Contains the 10 input road scene images.

**output/**
- Contains the processed images with detected lane lines.

**lane_detection_model.py**
- Main Python script that processes all images and produces the output results.

---

## Methodology

The lane detection pipeline consists of several steps:

### 1. White Lane Extraction
The algorithm first isolates white lane markings using HSV color filtering.

This step helps remove unnecessary background information such as vegetation, sky, and road texture.

### 2. Morphological Processing
A vertical morphological closing operation is applied to connect fragmented lane segments.

This improves the continuity of lane markings before edge detection.

### 3. Gaussian Blur
Gaussian blur is used to reduce noise and smooth the image before detecting edges.

### 4. Canny Edge Detection
Edges are detected using the Canny Edge Detector.

This highlights the boundaries of lane markings.

### 5. Edge Dilation
A small dilation operation strengthens weak edges and connects fragmented lane segments, improving line detection consistency.

### 6. Region of Interest (ROI)
A polygon mask is applied to focus only on the lower portion of the image where lanes are expected to appear.

This reduces false detections from irrelevant regions.

### 7. Hough Line Transform
The Hough Transform detects line segments corresponding to lane markings.

Detected lines are separated into left and right lanes based on their slope.

### 8. Lane Stabilization
Multiple detected line segments are averaged to generate a single stable lane line for each side.

### 9. Lane Center Estimation (Optional)
The midpoint between the two detected lanes is calculated and marked with a green circle.

---

## Parameter Tuning

The parameters were experimentally tuned to achieve robust detection across all 10 input images.

### Canny Edge Detection

- CANNY_LOW = 30
- CANNY_HIGH = 100
These values balance sensitivity and noise suppression.

---

### Hough Transform

- HOUGH_RHO = 1
- HOUGH_THETA = π / 180
- HOUGH_THRESHOLD = 25
- HOUGH_MIN_LINE_LENGTH = 75
- HOUGH_MAX_LINE_GAP = 150

Key considerations:

- **Minimum Line Length (75)** prevents short dashed center lines from being misclassified as lane boundaries.
- **Hough Threshold (25)** allows detection of weaker lane segments.

---

### Slope Filtering
To remove near-horizontal artifacts, a slope threshold was applied.

**abs(slope) < 0.29 → rejected**
- The value **0.29** was selected after experimentation to maintain correct detection across all frames while avoiding noise and incorrect line detections.

---

## Results

The final algorithm successfully detects:

- Left lane boundary
- Right lane boundary
- Lane center (optional)

All 10 images are processed using the same pipeline without image-specific adjustments.

---

## How to Run

### Requirements

Install dependencies:

pip install opencv-python numpy

---

### Run the Program

From the project directory:

python lane_detection_model.py


The program will:

1. Load all images from the **images/** folder
2. Process each image using the lane detection pipeline
3. Save the results to the **output/** folder

---

## Output

Each output image shows:

- Detected left lane (red)
- Detected right lane (red)
- Estimated lane center (green circle)

---

## Author

Nguyen Tien Dung

This project was completed as part of an assignment on computer vision and lane detection using classical image processing techniques.
