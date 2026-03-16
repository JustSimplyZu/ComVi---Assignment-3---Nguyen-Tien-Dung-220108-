import cv2
import numpy as np
import os

# =========================
# PARAMETERS
# =========================

CANNY_LOW = 30
CANNY_HIGH = 100

HOUGH_RHO = 1
HOUGH_THETA = np.pi / 180
HOUGH_THRESHOLD = 25
HOUGH_MIN_LINE_LENGTH = 75
HOUGH_MAX_LINE_GAP = 150

DRAW_CENTER = True


# =========================
# WHITE COLOR MASK
# =========================

def white_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 160])
    upper_white = np.array([180, 80, 255])

    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Stronger vertical closing to connect broken lane pieces
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 20))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask




# =========================
# ROI
# =========================

def region_of_interest(img):
    height, width = img.shape
    mask = np.zeros_like(img)

    polygon = np.array([[
        (0, int(height * 0.55)),
        (width, int(height * 0.55)),
        (width, height),
        (0, height)
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    return cv2.bitwise_and(img, mask)


# =========================
# SEPARATE LEFT & RIGHT
# =========================

def separate_lines(lines, width):
    left = []
    right = []

    for line in lines:
        x1, y1, x2, y2 = line[0]

        if x2 == x1:
            continue

        slope = (y2 - y1) / (x2 - x1)

        # Remove near-horizontal lines
        if abs(slope) < 0.20:
            continue

        # LEFT lane: negative slope
        if slope < 0:
            left.append((x1, y1, x2, y2))

        # RIGHT lane: positive slope
        elif slope > 0:
            right.append((x1, y1, x2, y2))

    return left, right



def stable_lane(lines, height, side):
    if len(lines) == 0:
        return None

    filtered = []

    for x1, y1, x2, y2 in lines:
        if x2 - x1 == 0:
            continue

        slope = (y2 - y1) / (x2 - x1)

        # Reject almost horizontal lines
        if abs(slope) < 0.29:
            continue

        # Enforce slope direction
        if side == "left" and slope > 0:
            continue
        if side == "right" and slope < 0:
            continue

        filtered.append((slope, x1, y1,  x2, y2))

    if len(filtered) == 0:
        return None

    # Average slope and intercept for stability
    slopes = []
    intercepts = []

    for slope, x1, y1, x2, y2 in filtered:
        intercept = y1 - slope * x1
        slopes.append(slope)
        intercepts.append(intercept)

    slope_avg = np.mean(slopes)
    intercept_avg = np.mean(intercepts)

    y_bottom = height
    y_top = int(height * 0.4)

    x_bottom = int((y_bottom - intercept_avg) / slope_avg)
    x_top = int((y_top - intercept_avg) / slope_avg)

    return [x_bottom, y_bottom, x_top, y_top]


# =========================
# DRAW
# =========================

def draw_lines(img, left_line, right_line):
    line_img = np.zeros_like(img)

    if left_line is not None:
        cv2.line(line_img,
                 (left_line[0], left_line[1]),
                 (left_line[2], left_line[3]),
                 (0, 0, 255), 10)

    if right_line is not None:
        cv2.line(line_img,
                 (right_line[0], right_line[1]),
                 (right_line[2], right_line[3]),
                 (0, 0, 255), 10)

    return cv2.addWeighted(img, 0.8, line_img, 1, 1)


def draw_center(img, left_line, right_line):
    if left_line is None or right_line is None:
        return img

    bottom_y = left_line[1]
    center_x = int((left_line[0] + right_line[0]) / 2)

    cv2.circle(img, (center_x, bottom_y), 10, (0, 255, 0), -1)
    return img


# =========================
# PIPELINE
# =========================

def process_image(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Failed to load {image_path}")
        return

    height, width = img.shape[:2]

    # 1. Extract white lanes
    mask = white_mask(img)

    # 2. Blur
    blur = cv2.GaussianBlur(mask, (5, 5), 0)

    edges = cv2.Canny(blur, CANNY_LOW, CANNY_HIGH)

    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    cropped = region_of_interest(edges)

    # 5. Hough
    lines = cv2.HoughLinesP(
        cropped,
        HOUGH_RHO,
        HOUGH_THETA,
        HOUGH_THRESHOLD,
        minLineLength=HOUGH_MIN_LINE_LENGTH,
        maxLineGap=HOUGH_MAX_LINE_GAP
    )

    if lines is None:
        cv2.imwrite(output_path, img)
        return

    left_lines, right_lines = separate_lines(lines, width)

    left_line = stable_lane(left_lines, height, "left")
    right_line = stable_lane(right_lines, height, "right")
    


    result = draw_lines(img, left_line, right_line)

    if DRAW_CENTER:
        result = draw_center(result, left_line, right_line)

    cv2.imwrite(output_path, result)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, "images")
    output_folder = os.path.join(script_dir, "output")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(1, 11):
        filename = f"frame{i}.jpg"
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"output_{filename}")

        print(f"Processing {filename}")
        process_image(input_path, output_path)

    print("All images processed successfully.")


if __name__ == "__main__":
    main()
