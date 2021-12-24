# RaspiCar

<!-- <img src="./img/car3.jpg" alt="drawing" height="400" width="600"/> -->
![RaspiCar](./img/car3.jpg)

## Intro

Guide for building a small-scale prototype of an autonomous vehicle with a Raspberry Pi, OpenCV, Tensorflow and Keras.

## Contents
1. [Project Objectives](#project-objectives)
2. [Prerequsite](#prerequisite)
3. [Assembly](#assembly)
4. [Setup](#setup)
5. [Model Training](#model-training)

### Project Objectives

1. Prerequisite
2. Assembly
3. Setup
4. Lane Detection
5. Traffic Sign Detection


### Prerequisite

#### Hardware

1. Tamiya TT02 Chassi
2. Raspberry Pi 4
3. Camera (optional with Wide-Angle-Lense)
4. Adafruit PCA 9865
5. DC/DC Converter
6. 3D printed parts

#### Skills

1. Basic Python programming skills
2. Basic Linux operating system (cli)

### Assembly

1. Mechanical Components:
  - Chassi
  - 3D Print CAD Model
2. Electrical Components:
  - Raspi
  - Cam
  - PCA with servo and ecu (i2c)
  - DC/DC Converter

Connect Electric Circuit:
![Electric Circuit](./img/Electric_Circuit.jpg)
![RaspberryPi Pins](./img/RaspiPins.jpg)


### Setup

Software Dependencies:

[Raspbian Os 64-Bit](https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-05-28/)
- Python 3.7
- Pillow 5.4.1
- Numpy 1.19.5
- Keras 2.6.0
- Tensorflow 2.6.0
- TFLite-Runtime 2.5.0
- OpenCVLite (Lightweight OpenCV Package with all needed Functions for the RaspiCar)
- Adafruit-PCA9685 1.0.1

All steps for installation is written in the installation Readme

### Model Training
If your interested in the Training Process of the Neural Networks you find the code
in the [model training](https://github.com/Fuchsi94/model-training) repository.

#### Lane Detection

[lane detection](https://github.com/Fuchsi94/model-training/tree/master/Lane-Detection)

train_model/lane_detection

#### Traffic Sign Detection

[traffic sign detection](https://github.com/Fuchsi94/model-training/tree/master/Traffic-Sign-Detection)
train_model/object_detection
