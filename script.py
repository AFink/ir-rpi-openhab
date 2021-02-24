import sys, traceback
import os
import requests
from random import randrange
from datetime import datetime, timedelta
from threading import Timer
import threading
import schedule
import time
import RPi.GPIO as GPIO

url_power = 'http://open.hab/rest/items/Gang_Power'
url_color = 'http://open.hab/rest/items/Gang_Color'
PIN=23

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN,GPIO.IN)

color = "null"
state = "false"

def switchLight(key):
    global color, brightness, state, url_power, url_color
    if key == "OFF":
        r = requests.post(url_power, 'OFF')
        state = "false"
    else: 
        now = datetime.now()
        if now.hour > 7 and now.hour < 19:
            brightness = 100
        else:
            brightness = 15
        r=requests.post(url_color, "{},100,{}".format(color, brightness))
        state = "true"

def generateColor():
    global color
    color = randrange(360)

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

generateColor()
schedule.every().day.at("0:00").do(generateColor)

timer = ResumableTimer(30, switchLight, ("OFF",))

try:
    while True:
        schedule.run_pending()
        i=GPIO.input(PIN)
        if i==0:
            time.sleep(0.5)
        if i==1:
            if state == "false":
                switchLight('ON')
                timer.start()
            timer.reset()
            time.sleep(0.1)
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)