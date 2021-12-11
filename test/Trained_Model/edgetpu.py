import os
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate
from PIL import Image
from PIL import ImageDraw

# Creates tflite interpreter
interpreter = Interpreter('detect_quant_edgetpu.tflite', experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
# This exact code can be used to run inference on the edgetpu by simply creating 
# the instantialize the interpreter with libedgetpu delegates:
# interpreter = Interpreter(args.model, experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
interpreter.allocate_tensors()
interpreter.invoke() # warmup
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
width = input_details[0]['shape'][2]
height = input_details[0]['shape'][1]

floating_model = (input_details[0]['dtype'] == np.float32)

def run_inference(interpreter, image):
  interpreter.set_tensor(input_details[0]['index'], image)
  interpreter.invoke()
  boxes = interpreter.get_tensor(output_details[1]['index'])[0]
  classes = interpreter.get_tensor(output_details[3]['index'])[0]
  scores = interpreter.get_tensor(output_details[0]['index'])[0]
  # num_detections = interpreter.get_tensor(output_details[3]['index'])[0]
  return boxes, classes, scores

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame1 = cap.read()
    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    frame_np = np.asarray(frame_resized, dtype=np.int8)
    input_data = np.expand_dims(frame_np, axis=0)

    # Run inference
    boxes, classes, scores = run_inference(interpreter, input_data)
    print('boxes', boxes, 'classes', classes, 'scores', scores)
    
    if cv2.waitKey(1) or 0xFF ==ord('q'):
        cap.release()
        cv2.destroyAllWindows()