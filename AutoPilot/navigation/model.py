import h5py
import cv2
import tensorflow
import logging
from keras.models import load_model
from keras import __version__ as keras_version
KERAS_VERSION = keras_version


def loadTrainedModel(filename='model.h5'):

    # check that model Keras version is same as local Keras version
    model_file = h5py.File(filename, mode='r')
    model_version = model_file.attrs.get('keras_version')
    keras_version = str(KERAS_VERSION).encode('utf8')

    if model_version != keras_version:
        logging.warning('You are using Keras version {} but the model was built using {}'.format(keras_version, model_version))
        
    logging.info("succesfully loaded {}".format(filename))
    return load_model(filename)


def preprocessing(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,  (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model = loadTrainedModel()
    #image = preprocessing()