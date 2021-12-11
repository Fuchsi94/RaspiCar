import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import logging
import math

class rule_based_lane_follow():
    
    def __init__(self):
        logging.info('starting lane navigation')
        self.curr_steering_angle = 0
        
    def navigate(self, frame):
        
        avg_lines, combo_image = detect_lane_image(frame)
        self.curr_steering_angle, self.image = steering_angle(combo_image, avg_lines, self.curr_steering_angle)

        
def detect_lane_image(image):
    canny_img = canny(image)
    cropped_img = region_of_interest(canny_img)
    line_segments = detect_line_segments(cropped_img)
    avg_lines = average_slope_intercept(image, line_segments)
    line_image = display_lines(image, avg_lines)
    combo_image = cv2.addWeighted(image, 0.8, line_image, 1, 1)
    return avg_lines, combo_image

        
def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny


def region_of_interest(image):
    height = image.shape[0]
    width = image.shape[1]
    polygons = np.array([
    [(0, 600),  (1200, 600),  (1200, 400), (800, 250), (400, 250), (0, 400)]
    ])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def detect_line_segments(cropped_image):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # degree in radian, i.e. 1 degree
    min_threshold = 1  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_image, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4)

    if line_segments is not None:
        for line_segment in line_segments:
            logging.debug('detected line_segment:')
            logging.debug("%s of length %s" % (line_segment, length_of_line_segment(line_segment[0])))

    return line_segments


def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    width = image.shape[1]
    # höhe der roi
    y2 = 250
    #rechte spur
    if slope > 0:
        y1 = slope * width + intercept
        x1 = width
        x2 = (y2 - intercept) / slope
    #linke spur
    if slope < 0:
        y1 = intercept
        x1 = 0
        x2 = (y2 - intercept) / slope
    
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    return np.array([x1, y1, x2, y2])


def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = np.squeeze(line)
        slope, intercept = np.polyfit((x1, x2), (y1, y2), 1)
        # prüfen ob die spur auf der linke oder rechten seite ist
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))
    
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    
    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)
    
    return np.array([left_line, right_line])


def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image


def length_of_line_segment(line):
    x1, y1, x2, y2 = line
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)



def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected, do nothing')
        return 0

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0]
        _, _, right_x2, _ = lane_lines[1]
        camera_mid_offset_percent = 0.03 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    print(angle_to_mid_deg)
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return angle_to_mid_deg


def stabilize_steering_angle(curr_steering_angle, new_steering_angle, num_of_lane_lines, max_angle_deviation_two_lines=5, max_angle_deviation_one_lane=1):
    """
    Using last steering angle to stabilize the steering angle
    This can be improved to use last N angles, etc
    if new angle is too different from current angle, only turn by max_angle_deviation degrees
    """
    if num_of_lane_lines == 2 :
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else :
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane
    
    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
                                        + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    logging.info('Proposed angle: %s, stabilized angle: %s' % (new_steering_angle, stabilized_steering_angle))
    return stabilized_steering_angle


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    # figure out the heading line from steering angle
    # heading line (x1,y1) is always center bottom of the screen
    # (x2, y2) requires a bit of trigonometry

    # Note: the steering angle of:
    # 0-89 degree: turn left
    # 90 degree: going straight
    # 91-180 degree: turn right
    if steering_angle is not 0:
        steering_angle_radian = steering_angle / 180.0 * math.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
        y2 = int(height / 2)
        
    else:
        x1 = int(width / 2)
        y1 = height
        x2 = int(width / 2)
        y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image


def steering_angle(combo_image, avg_lines, curr_steering_angle):
    new_steering_angle = compute_steering_angle(combo_image, avg_lines)
    curr_steering_angle = stabilize_steering_angle(curr_steering_angle, new_steering_angle, len(avg_lines))
    curr_heading_image = display_heading_line(combo_image, curr_steering_angle)
    return curr_steering_angle, curr_heading_image


if __name__ == '__main__':
    autopilot = rule_based_lane_follow()
    frame = cv2.imread('lane.jpg')
    frame = cv2.resize(frame, (1200, 800))
    autopilot.navigate(frame)
    print(autopilot.curr_steering_angle)
    cv2.imshow('frame', autopilot.image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()