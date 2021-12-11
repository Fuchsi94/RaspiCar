import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

MAX_LEFT_PULSE = 270
MAX_RIGHT_PULSE = 410
NEUTRAL_PULSE = 340

pwm.set_pwm(0, 0, 410)