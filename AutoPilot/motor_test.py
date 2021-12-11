import cv2
import logging
import numpy as np
from time import time, sleep
from control.car import Car
from sensor.cv2_videostream import VideoStream
from navigation.model import loadTrainedModel, preprocessing
from utilities.xbox import Joystick

SERVO_PIN = 0
MOTOR_PIN = 1
MODEL_PATH = "./navigation/model.h5"

logging.basicConfig(level=logging.INFO)
videostream = VideoStream(resolution=(320, 160),framerate=30)
model = loadTrainedModel(MODEL_PATH)
car = Car(motor_pin=MOTOR_PIN, servo_pin=SERVO_PIN)

#video = cv2.VideoCapture(0)

videostream.start()
car.move(355)
count = 0
go = True
while go:
    # Grab frame from video stream
    frame = videostream.read()
    img = preprocessing(np.asarray(frame))
    img = np.array([img])
    steering_angle = float(model.predict(img)) * 10
    car.turn(steering_angle)
    print(steering_angle)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        go = False
           
car.stop()
car.neutral()
videostream.stop()
cv2.destroyAllWindows()
