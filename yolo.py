# -*- coding: utf-8 -*-
"""
Created on Sun May  8 13:04:34 2022

@author: ASUS
"""
import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
# from pygame import mixer
import pygame
import time
import vlc


GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

cap = cv.VideoCapture(0)
whT = 320
confThreshold =0.5
nmsThreshold= 0.2

#### LOAD MODEL
## Coco Names
classesFile = "coco.txt"
classNames = []
with open(classesFile, 'rt') as f:
    classNames = f.read().rstrip('nq').split(',')
print(classNames)
## Model Files
modelConfiguration = "yolov3-tiny.cfg"
modelWeights = "yolov3-tiny.weights"
net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
def alert():
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('beep-07.wav') 
    p.set_media(m)
    p.play() 
    p.pause() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
def alert_person():
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('person.wav') 
    p.set_media(m)
    p.play() 
    p.pause() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
def alert_car():
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('car1_1.mp3') 
    p.set_media(m)
    p.play() 
    p.pause() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
def alert_buss():
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('busedt.mp3') 
    p.set_media(m)
    p.play() 
    p.pause() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
def alert_cat():
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('cat1_1.mp3') 
    p.set_media(m)
    p.play() 
    p.pause() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
def alert_cell():
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('cellphone.m4a') 
    p.set_media(m)
    p.play() 
    p.pause() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
def findObjects(outputs,img):
    hT, wT, cT = img.shape
    bbox = []
    classIds = []
    confs = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w,h = int(det[2]*wT) , int(det[3]*hT)
                x,y = int((det[0]*wT)-w/2) , int((det[1]*hT)-h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))
                print(classIds)
                if classIds==[0]:
                    alert_person()
                if classIds==[2]:
                    alert_car()
                if classIds==[4]:
                    alert_buss()
                if classIds==[15]:
                    alert_cat()
                if classIds==[67]:
                    alert_cell()


                
    indices = cv.dnn.NMSBoxes(bbox, confs, confThreshold, nmsThreshold)

    for i in indices:
        
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # print(x,y,w,h)
        cv.rectangle(img, (x, y), (x+w,y+h), (255, 0 , 255), 2)
        try:
            cv.putText(img,f'{classNames[classIds[i]].upper()} {int(confs[i]*100)}%',
                              (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        except:
            print('no')
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
def beep_freq():
  # Measure the distance
  dist = distance()
  # If the distance is bigger than 50cm, we will not beep at all
  if dist > 50:
    return -1
  # If the distance is between 50 and 30 cm, we will beep once a second
  elif dist <= 50 and dist >=30:
    return 1
  # If the distance is between 30 and 20 cm, we will beep every twice a second
  elif dist < 30 and dist >= 20:
    return 0.5
  # If the distance is between 20 and 10 cm, we will beep four times a second
  elif dist < 20 and dist >= 10:
    return 0.25
  # If the distance is smaller than 10 cm, we will beep constantly
  else:
    return 0
while True:
    success, img = cap.read()
    blob = cv.dnn.blobFromImage(img, 1 / 255, (whT, whT), [0, 0, 0], 1, crop=False)
    net.setInput(blob)
    layersNames = net.getLayerNames()
    outputNames = [(layersNames[i - 1]) for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)
    findObjects(outputs,img)
    dist = distance()
    print ("Measured Distance = %.1f cm" % dist)
    freq = beep_freq()
    # No beeping
    if freq == -1:
        print('no signal')
        time.sleep(0.25)
        # Constant beeping
    elif freq == 0:
        alert()
        time.sleep(0.25)
        # Beeping on certain frequency
    else:
        alert()
        time.sleep(0.2) # Beep is 0.2 seconds long
        print('3')
        time.sleep(freq) # Pause between beeps = beeping frequency
    cv.imshow('Image', img)
    cv.waitKey(1)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    
    # Release handle to the webcam
cap.release()
cv.destroyAllWindows()