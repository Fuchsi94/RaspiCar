from laneNavigation_test import rule_based_lane_follow
import cv2
import Adafruit_PCA9685
import logging
import time

#logging.basicConfig(level=logging.INFO)

autopilot = rule_based_lane_follow()
#initialize PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)
logging.info('loaded PCA')
time.sleep(0.5)
servo_middle = 340 # mitte

def steering_angle_to_pwm(steering_angle):
    pwm = (steering_angle +20) * 3.5 + 270
    return pwm

def max_steering(steering_angle):
    if steering_angle >= 20:
        steering_angle = max_steering_right
    elif steering_angle <= -20:
        steering_angle = max_steering_left
    else:
        steering_angle = steering_angle
    return steering_angle

cam = cv2.VideoCapture(0)
while cam:
    ret, frame = cam.read()
    if ret:
        frame = cv2.resize(frame, (1200, 800))
        autopilot.navigate(frame)
        steering_angle = autopilot.curr_steering_angle
        print(autopilot.curr_steering_angle)
        steering_angle = max_steering(steering_angle)
        pwm = steering_angle_to_pwm(steering_angle)
        cv2.imshow('frame', autopilot.image)
        print(pwm)
        
    else:
        loggin.warning('Somethings wrong with the camera')
        break
    
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
cam.release()

#pwm.set_pwm(0, 0, 340)