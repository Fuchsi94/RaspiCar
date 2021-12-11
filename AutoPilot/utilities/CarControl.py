import Adafruit_PCA9685
import xbox
import time
import socket
from lib_oled96 import ssd1306
from smbus import SMBus

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

i2cbus = SMBus(1)
oled = ssd1306(i2cbus)
draw = oled.canvas
oled.cls()
oled.display()

# Configure min and max servo pulse lengths
servo_min = 290  # Min pulse length out of 4096 links
servo_max = 410  # Max pulse length out of 4096 rechts
servo_middle = 350 # mitte

throttle_min = 150  # Min pulse length out of 4096 links
throttle_max = 600  # Max pulse length out of 4096 rechts
throttle_mid = 150 + 600 // 2

joy = xbox.Joystick()         #Initialize joystick
print("Connected")

steering = False
throttle = False

while steering == True:
    pwm.set_pwm(0, 0, servo_min)
    print('move servo to min')
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_middle)
    print('move servo to middle')
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_max)
    print('move servo to max')
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_middle)
    print('move servo to middle')
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_min)
    print('move servo to min')
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_max)
    print('move servo to max')
    time.sleep(1)
    
    
while not joy.Back(): 
    
    if joy.A():                   #Test state of the A button (1=pressed, 0=not pressed)
        print('X button pressed')
    
    if joy.B():                   #Test state of the A button (1=pressed, 0=not pressed)
        print('Circle button pressed')
        
    if joy.X():                   #Test state of the A button (1=pressed, 0=not pressed)
        print('Square button pressed')
        
    if joy.Y():                   #Test state of the A button (1=pressed, 0=not pressed)
        print('Triangle button pressed')
        
    # Left analog stick
    #show("  Left X/Y:", fmtFloat(joy.leftX()), "/", fmtFloat(joy.leftY()))
    # Right trigger
    #show("  RightTrg:", fmtFloat(joy.rightTrigger()))
    
    x_axis   = joy.leftX()        #X-axis of the left stick (values -1.0 to 1.0)
    (x,y)    = joy.leftStick()    #Returns tuple containing left X and Y axes (values -1.0 to 1.0)
    trigger  = joy.rightTrigger() #Right trigger position (values 0 to 1.0)
    brake = joy.leftTrigger()
    
    
    
    throttle = round(((trigger * -1) + 1) / 4 * 100 + 350, 0)
    pwm.set_pwm(1, 0, int(throttle))
    
    steering_angle = round((x * 100 + 100) /2 + 300, 0)
    pwm.set_pwm(0, 0, int(steering_angle))
    print('move servo to ' + str(steering_angle), 'throttle ' + str(throttle))
 
joy.close()                   #Cleanup before exit
    
