import cv2
import logging
import numpy as np
from time import time, sleep
from control.car import Car
from sensor.cv2_videostream import VideoStream
from navigation.model import loadTrainedModel, preprocessing
from utilities.xbox import Joystick

def stabilize_steering_angle(curr_steering_angle, new_steering_angle, max_angle_deviation=8):
    """
    Using last steering angle to stabilize the steering angle
    This can be improved to use last N angles, etc
    if new angle is too different from current angle, only turn by max_angle_deviation degrees
    """
    
    angle_deviation = new_steering_angle - curr_steering_angle
    print("angle deviation", angle_deviation)
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    print("stabilized", stabilized_steering_angle)
    print("new steering angle", new_steering_angle)
        
    return stabilized_steering_angle

def run(car, videostream, model):
    videostream.start()
    go = True
    car.move(361)
    steering_angle = 0
    while go:
        # Grab frame from video stream
        frame = videostream.read()
        img = preprocessing(np.asarray(frame))
        img = np.array([img])
        pred_steering_angle = float(model.predict(img)) * 20
        print("predicted", pred_steering_angle)
        steering_angle = stabilize_steering_angle(steering_angle, pred_steering_angle)
        print("steering", steering_angle)
        #steering_angle = pred_steering_angle
        car.turn(steering_angle)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            go = False
           
    car.stop()
    car.neutral()
    videostream.stop()
    cv2.destroyAllWindows()

def main():
    logging.info("starting up RaspiCar")
    # define PIN Number on PCA9865
    SERVO_PIN = 0
    MOTOR_PIN = 1
    MODEL_PATH = "./navigation/model.h5"
    logging.info("Setting up hardware API")
    car = Car(motor_pin=MOTOR_PIN, servo_pin=SERVO_PIN)
    videostream = VideoStream(resolution=(320, 160),framerate=30)
    model = loadTrainedModel(MODEL_PATH)
    run(car, videostream, model)


    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()


# add pip3 install Adafruit-PCA9685 to setting_up.sh


