from math import degrees, radians
import Adafruit_PCA9685
import logging

MAX_LEFT_ANGLE = -20   # In unit degree
MAX_RIGHT_ANGLE = 20   # In unit degree

MAX_LEFT_RADIAN = radians(MAX_LEFT_ANGLE)   # In unit radian
MAX_RIGHT_RADIAN = radians(MAX_RIGHT_ANGLE) # In unit radian

MAX_LEFT_PULSE = 270
MAX_RIGHT_PULSE = 410
NEUTRAL_PULSE = 340

# NOTE: To produce a desired steering angle, the linear relationship
#       between steering angle (in degree) and pulse width is defined as follow:
ANGLE_TO_PWM = lambda x: int((x +20) * 3.5 + 200)

class Servo:
    """ Control the transverse (left and right) motion of the car """
    def __init__(self, pin):
        logging.info("initialize Servor")
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(60)
        self.pin = pin
        self.steer_angle = 0
        self.calibrate()
    
    def calibrate(self):
        #self.neutral()
        self.neutral()

    def left(self):
        """ Turn servo left"""
        self.pwm.set_pwm(self.pin, 0, MAX_LEFT_PULSE)
        self.steer_angle = MAX_LEFT_ANGLE
        logging.info(MAX_LEFT_ANGLE)

    def right(self):
        """ Turn servo right"""
        self.pwm.set_pwm(self.pin, 0, MAX_RIGHT_PULSE)
        self.steer_angle = MAX_RIGHT_ANGLE
        logging.info(MAX_RIGHT_ANGLE)

    def neutral(self):
        """ Reset servo to neutral position"""
        self.pwm.set_pwm(self.pin, 0, NEUTRAL_PULSE)
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
        
        self.pwm.set_pwm(self.pin, 0, pulse_width)
        self.steer_angle = steer_angle
        logging.info(pulse_width)

    
if __name__ == "__main__":
    servo = Servo(0)
    servo.turn(0)


    