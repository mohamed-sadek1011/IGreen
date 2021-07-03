from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User
from sensors import *
import time
import cv2
import serial
from time import sleep

ser = serial.Serial("/dev/ttyS0",9600)

work = Blueprint('work', __name__)



def gen():
    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    thres = 0.45 # Threshold to detect object
    #cap.set(3,1280)
    #cap.set(4,720)
   # cap.set(10,70)

    classNames= []
    classFile = 'coco.names'
    with open(classFile,'rt') as f:
        classNames = f.read().rstrip('n').split('n')

    configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightsPath = 'frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightsPath,configPath)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    #Read until video is completed
    while(cap.isOpened()):
        #Capture frame-by-frame
        ret, img = cap.read()
        img = cv2.flip(img,1)
        classIds, confs, bbox = net.detect(img,confThreshold=thres)
       # print(classIds,bbox)
        if len(classIds) != 0:
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                cv2.rectangle(img,box,color=(0,255,0),thickness=2)
               
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        else: 
            break

@work.route('/sensors', methods = ['GET' , 'POST'])
@login_required
def sensors():
    global Temperature
    global Humidity
    global Soil_Moisture
    global Lighting

    ser.write(b'request_sensors')
    Lighting =(ser.readline().decode('utf-8'))
    sleep(0.25)
    Soil_Moisture=(ser.readline().decode('utf-8'))
    sleep(0.25) 
   
    return render_template("sensors.html",user=current_user, Lighting = Lighting, Humidity = Humidity, Soil_Moisture = Soil_Moisture, Temperature = Temperature)

@work.route('/arm', methods = ['GET' , 'POST'])
@login_required
def move():
    if request.method == 'POST':
        if request.form['action'] == 'Open':
            ser.write(b'g')
            sleep(0.01)
            ser.write(b'280')
            sleep(0.1)
            return ('', 204)
        elif request.form['action'] == 'Close':
            ser.write(b'g')
            sleep(0.01)
            ser.write(b'0')
            sleep(0.1)
            return ('', 204)
        elif request.form['action'] == 'Move':
            BaseAngle = str(request.form.get('Base_Angle'))
            LsAngle = str(request.form.get('LS_Angle'))
            UsAngle = str(request.form.get('US_Angle'))
            ser.write(b'base')
            sleep(0.01)
            ser.write(bytes(BaseAngle,'utf-8'))
            sleep(0.1)
            ser.write(b'ls')
            sleep(0.01)
            ser.write(bytes(LsAngle,'utf-8'))
            sleep(0.1)
            ser.write(b'us')
            sleep(0.01)
            ser.write(bytes(UsAngle,'utf-8'))
            sleep(0.1)
            return ('', 204)
    elif request.method == 'GET':
        return render_template("mechanical_arm.html", user=current_user)
    

@work.route('/arm/video-feed')
def video_feed():
     return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
