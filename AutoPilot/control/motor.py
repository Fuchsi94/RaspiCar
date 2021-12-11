import Adafruit_PCA9685
import logging
from time import sleep

MAX_PULSE = 355
MIN_PULSE = 364
STOP_PULSE = 365
logging.info("stop: {}, min: {}, max {}".format(MAX_PULSE, MIN_PULSE, STOP_PULSE))

class Motor:
    """ Control the longitudinal (forward) motion of the car"""
    def __init__(self, pin, initPulseWidth=364):
        logging.info("initialize Motor")
        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40)
        self.pwm.set_pwm_freq(60)
        self.pin = pin
        self.pulseWidth = initPulseWidth

    def moveForward(self):
        """ Move forward """
        logging.info("setting pwm to {}".format(self.pulseWidth))
        self.pwm.set_pwm(self.pin, 0, self.pulseWidth)

    def stop(self):
        """ Stop the car """
        logging.info("stopping car")
        self.pwm.set_pwm(self.pin, 0, 365)
        
    def move(self, speed):
        """Move forward with specific speed"""
        logging.info("setting pwm to {}".format(speed))
        self.pwm.set_pwm(self.pin, 0, speed)
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    motor = Motor(pin=1)
    motor.stop()