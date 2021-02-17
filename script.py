import sys, traceback
import os

import RPi.GPIO as GPIO
import requests
import time
import threading
import random

PIN=23
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN,GPIO.IN)

state = "false"

class ResumableTimer:
    def __init__(self, timeout, callback, args):
        self.timeout = timeout
        self.args = args
        self.callback = callback
        self.timer = threading.Timer(timeout, callback, args)

    def start(self):
        if (not self.timer.is_alive):
            self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.callback, self.args)
        self.timer.start()

def callUrl(key):
    global state
    r=requests.post('http://open.hab/rest/items/Gang_Power', key)
    if key == "OFF":
        state = "false"
    #print(key == "OFF")
    #print(key)

timer = ResumableTimer(20, callUrl, ("OFF",))

try:
    while True:
        i=GPIO.input(PIN)
        if i==0:
            #print("nothing detected")
            time.sleep(0.5)
        if i==1:
            #print("something detected") 
            if state == "false":
                callUrl('ON')
                state = "true"
                timer.start()
            timer.reset()
            time.sleep(0.1)
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)