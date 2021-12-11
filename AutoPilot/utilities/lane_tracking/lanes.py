import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import logging
import math
import sys
import datetime

test_img_path = 'test2.jpg'

def resize(image, show_img):
    resized_img = cv2.resize(image, (640, 480), interpolation=cv2.INTER_CUBIC)
    if show_img:
        cv2.imshow('image', resized_img)
    return resized_img

def hsv(resized_img, show_img):
    hsv = cv2.cvtColor(resized_img, cv2.COLOR_BGR2HSV)
    if show_img:
        cv2.imshow('hsv', hsv)
    lower_blue = np.array([50, 120, 0])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    if show_img:
        cv2.imshow('blue mask', mask)
    return mask

def canny(hsv_img, show_img):
    blur = cv2.GaussianBlur(hsv_img, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)
    if show_img:
        cv2.imshow('canny', canny)
    return canny

def region_of_interest(canny_img, show_img):
    height, width = canny_img.shape
    polygons = np.array([
    [(0, height), (int(width*0.4), int(height*0.5)), (int(width*0.6), int(height*0.5)), (width, height)]
    ])
    mask = np.zeros_like(canny_img)
    cv2.fillPoly(mask, polygons, 255)
    cropped_img = cv2.bitwise_and(canny_img, mask)
    if show_img:
        cv2.imshow('cropped image', cropped_img)
    return cropped_img

def detect_line_segments(cropped_img):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # degree in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_img, rho, angle, min_threshold, np.array([]), minLineLength=8,
                                    maxLineGap=4)

    return line_segments

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        logging.info('No line_segment segments detected')
        return lane_lines

    height, width = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines

def make_points(frame, line):
    height, width = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
        We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected, do nothing')
        return -90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle

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
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

def detect_lane(input_image):
    image = cv2.imread(input_image)
    resized_img = resize(image, False)
    hsv_img = hsv(resized_img, False)
    canny_img = canny(hsv_img, False)
    cropped_img = region_of_interest(canny_img, False)
    
    line_segments = detect_line_segments(cropped_img)
    line_segments_img = display_lines(resized_img, line_segments)
    
    lane_lines = average_slope_intercept(cropped_img, line_segments)
    lane_lines_img = display_lines(resized_img, lane_lines)
 
    return lane_lines, lane_lines_img, resized_img  

lane_lines, lane_lines_img, img = detect_lane(test_img_path)
new_steering_angle = compute_steering_angle(img, lane_lines)
heading_img = display_heading_line(img, new_steering_angle)
cv2.imshow('heading img', heading_img)
cv2.waitKey(0)
