# https://www.tensorflow.org/api_docs/python/tf/lite/Interpreter

import re
import cv2
from tflite_runtime.interpreter import Interpreter
import numpy as np
import time
import math
from tflite_runtime.interpreter import load_delegate
#import tensorflow as tf

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

def load_labels(path='labelmap.txt'):

    """Loads the labels file. Supports files with or without index numbers."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        labels = {}
        for row_number, content in enumerate(lines, start=1):
            labels[row_number] = content.strip()
            
    return labels

def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = np.expand_dims((image-255)/255, axis=0)


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor
  
  
def initialize_model():
    labels = load_labels()
    #interpreter = Interpreter('detect.tflite')
    interpreter = Interpreter('detect_quant_edgetpu.tflite', experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print("Model Loaded Successfully.")

    interpreter.allocate_tensors()
    a, input_height, input_width, b = interpreter.get_input_details()[0]['shape']
    print("Model initialized with height, width: ", input_height, "x", input_width)
    return input_height, input_width, interpreter

def get_image(frame):
    img = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (input_height, input_width))
    return img

def detect_objects(interpreter, image, threshold):
    """Returns a list of detection results, each a dictionary of object info."""
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    # Get all output details
    output1 = interpreter.get_output_details()[0]['index']
    output2 = interpreter.get_output_details()[1]['index']
    output3 = interpreter.get_output_details()[2]['index']
    output4 = interpreter.get_output_details()[3]['index']

    boxes = np.squeeze(interpreter.get_tensor(output2))
    classes = np.squeeze(interpreter.get_tensor(output4))
    scores = np.squeeze(interpreter.get_tensor(output1))
    num_classes = np.squeeze(interpreter.get_tensor(output3))
    
#    print("output1: ", output1)
#    print("output2: ", output2)
#    print("output3: ", output3)
#    print("output4: ", output4)
    
    print("boxes: ", boxes)
    print("classes: ", classes)
    print("scores: ", scores)
    print("num classes: ", num_classes)
    
    results = []
    result = {
       'bounding_box': boxes[0],
        'class_id': classes[0],
        'score': scores[0]
       }
    results.append(result)
    return results

 
def main():
    input_height, input_width, interpreter = initialize_model()
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        img = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (320,320))
        res = detect_objects(interpreter, img, 0.8)
        
       # print(res)

        for result in res:
            ymin, xmin, ymax, xmax = result['bounding_box']
            xmin = int(max(1,xmin * CAMERA_WIDTH))
            xmax = int(min(CAMERA_WIDTH, xmax * CAMERA_WIDTH))
            ymin = int(max(1, ymin * CAMERA_HEIGHT))
            ymax = int(min(CAMERA_HEIGHT, ymax * CAMERA_HEIGHT))
            
            cv2.rectangle(frame,(xmin, ymin),(xmax, ymax),(0,255,0),3)
            #cv2.putText(frame,labels[int(result['class_id'])],(xmin, min(ymax, CAMERA_HEIGHT-20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),2,cv2.LINE_AA) 

        cv2.imshow('Pi Feed', frame)

        if cv2.waitKey(10) & 0xFF ==ord('q'):
            cap.release()
            cv2.destroyAllWindows()            

if __name__ == "__main__":
    main()