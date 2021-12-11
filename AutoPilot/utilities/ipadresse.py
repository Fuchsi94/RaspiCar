import time
import socket
from lib_oled96 import ssd1306
from smbus import SMBus
import Adafruit_PCA9685
import xbox

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

i2cbus = SMBus(1)
oled = ssd1306(i2cbus)
draw = oled.canvas
oled.cls()

joy = xbox.Joystick()         #Initialize joystick
print("Connected")
draw.text((30, 16),"Controller", fill=1)
draw.text((30, 30),"Connected", fill=1)
oled.display()
time.sleep(2)
oled.cls()


def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

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
    
    draw.rectangle((70, 16, 120, 40), 0, 0);
    draw.text((10, 0), "IP: ", fill=1)
    draw.text((30, 0), get_ip_address(), fill=1)
    draw.text((10, 16), "steering: ", fill=1)
    draw.text((70, 16), str(round(x, 1)), fill=1)
    draw.text((10, 30), "throttle: ", fill=1)
    draw.text((70, 30), str(round(trigger, 1)), fill=1)
    oled.display()
 
joy.close()                   #Cleanup before exit


    
