import cv2
import os
import time
import datetime
import Adafruit_PCA9685
import xbox
import csv

def steering_angle_to_pwm(steering_angle):
    pwm = (steering_angle +20) * 3.5 + 270
    return pwm

def max_steering(steering_angle):
    if steering_angle >= 20:
        steering_angle = max_steering_right
    elif sttering_angle <= -20:
        steering_angle = max_steering_left
    else:
        steering_angle = steering_angle
    
#Initialize controller
joy = xbox.Joystick()         
print("Connected")
time.sleep(0.5)

output_path = '/home/pi'

#make training folder
if os.path.isdir('{}/training_data/IMG'.format(output_path)):
    print('IMG folder already exists')
else:
    os.mkdir('{}/training_data'.format(output_path))
    os.mkdir('{}/training_data/IMG'.format(output_path))
    print('created IMG folder')
time.sleep(0.5)

reverse = 0
speed = 0

#create empty dictionary
driving_log = {}
print('created driving log')
time.sleep(0.5)
    
#initialize PCA9685
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)
print('loaded PCA')
time.sleep(0.5)

#config servo values
servo_middle = 340 # mitte
servo_max = 75 # maximaler ausschlag
print('set servo values')
time.sleep(0.5)

#init camera
WIDTH = 320
HEIGHT = 160
vid = cv2.VideoCapture(0)
#vid = cv2.VideoCapture(0, cv2.CAP_V4L2)
#vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
#vid.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
#vid.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
print('started Videostream')
run = True
time.sleep(0.5)



count = 0
while run:
    
    ret, frame = vid.read()
    if not ret:
        run = False       
    
    x_axis   = joy.leftX()        #X-axis of the left stick (values -1.0 to 1.0)
    (x,y)    = joy.leftStick()    #Returns tuple containing left X and Y axes (values -1.0 to 1.0)
    trigger  = joy.rightTrigger() #Right trigger position (values 0 to 1.0)
    brake = joy.leftTrigger()
            
    # set  speed
    throttle = round(((trigger * -1) + 1) / 4 * 100 + 350, 0)
    pwm.set_pwm(1, 0, int(throttle))
    
    #steering
    steering_angle = x * 20
    pwm_signal = steering_angle_to_pwm(steering_angle)
    #print(steering_angle)
    pwm.set_pwm(0, 0, int(pwm_signal))

    steering = x
    
    date = datetime.datetime.now()
    csvstr = datetime.datetime.strftime(date, '%Y_%m_%d_%H_%M_%S')
    driving_log['{}/training_data/IMG/center_{}_{}.jpg'.format(output_path, csvstr, count)] = steering , throttle, reverse, speed
    cv2.imwrite('{}/training_data/IMG/center_{}_{}.jpg'.format(output_path, csvstr, count), frame)
    print('{}_{}.jpg steering_angle {}'.format(csvstr, count, steering_angle))
    time.sleep(0.01) # 30FPS
    count += 1
    
    if joy.A():                   
        run = False

if os.path.isfile('{}/training_data/driving_log.csv'.format(output_path)):
    with open('{}/training_data/driving_log.csv'.format(output_path), 'a') as file:
        writer = csv.writer(file)        
    
        for key, value in driving_log.items():
            writer.writerow([key, value[0], value[1], value[2], value[3]])
        
else:
    with open('{}/training_data/driving_log.csv'.format(output_path), 'w') as file:
        writer = csv.writer(file)        
        
        for key, value in driving_log.items():
            writer.writerow([key, value[0], value[1], value[2], value[3]])
