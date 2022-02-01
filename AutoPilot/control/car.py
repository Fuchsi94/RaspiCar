from math import degrees
import Adafruit_PCA9685
import logging
from time import sleep

MAX_LEFT_ANGLE = -20   # In unit degree
MAX_RIGHT_ANGLE = 20   # In unit degree

MAX_LEFT_PULSE = 270
MAX_RIGHT_PULSE = 410
NEUTRAL_PULSE = 340

MAX_PULSE = 355
MIN_PULSE = 364
STOP_PULSE = 365
logging.info("stop: {}, min: {}, max {}".format(MAX_PULSE, MIN_PULSE, STOP_PULSE))

# NOTE: To produce a desired steering angle, the linear relationship
#       between steering angle (in degree) and pulse width is defined as follow:
ANGLE_TO_PWM = lambda x: int((x +20) * 3.5 + 270)

class Car:
    def __init__(self, motor_pin, servo_pin, initPulseWidth=360):
        logging.info("starting RaspiCar")
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(60)
        self.motor_pin = motor_pin
        self.servo_pin = servo_pin
        self.steer_angle = 0
        self.pulseWidth = initPulseWidth
        
    def moveForward(self):
        """ Move forward """
        logging.info("setting pwm to {}".format(self.pulseWidth))
        self.pwm.set_pwm(self.motor_pin, 0, self.pulseWidth)

    def stop(self):
        """ Stop the car """
        logging.info("stopping car")
        self.pwm.set_pwm(self.motor_pin, 0, 365)
        
    def move(self, speed):
        """Move forward with specific speed"""
        logging.info("setting pwm to {}".format(speed))
        self.pwm.set_pwm(self.motor_pin, 0, speed)
        
    def calibrate(self):
        self.neutral()

    def left(self):
        """ Turn servo left"""
        self.pwm.set_pwm(self.servo_pin, 0, MAX_LEFT_PULSE)
        self.steer_angle = MAX_LEFT_ANGLE
        logging.info(MAX_LEFT_ANGLE)

    def right(self):
        """ Turn servo right"""
        self.pwm.set_pwm(self.servo_pin, 0, MAX_RIGHT_PULSE)
        self.steer_angle = MAX_RIGHT_ANGLE
        logging.info(MAX_RIGHT_ANGLE)

    def neutral(self):
        """ Reset servo to neutral position"""
        self.pwm.set_pwm(self.servo_pin, 0, NEUTRAL_PULSE)
        self.steer_angle = 0
        logging.info(NEUTRAL_PULSE)

    def turn(self, steer_angle):

        if steer_angle == 0:
            pulse_width = NEUTRAL_PULSE
        # If left turn
        elif steer_angle < 0:
            # Calculate the desire PWM to induce the steering angle
            pulse_width = ANGLE_TO_PWM(steer_angle)
            # Restraint the pulse width within the safety range [1200, 1780]
            pulse_width = max(MAX_LEFT_PULSE, pulse_width)
        else:
            # Calculate the desire PWM to induce the steering angle
            pulse_width = ANGLE_TO_PWM(steer_angle)
            # Restraint the pulse width within the safety range [1200, 1780]
            pulse_width = pulse_width = min(MAX_RIGHT_PULSE, pulse_width)
        
        self.pwm.set_pwm(self.servo_pin, 0, pulse_width)
        self.steer_angle = steer_angle
        logging.info(pulse_width)
        