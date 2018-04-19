# !/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
from itertools import count
# temperature recordings
import os
import glob

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

BASE_DIRECTORY_LOCATION = '/sys/bus/w1/devices/'
DEVICE_FOLDER_LOCATION = glob.glob(BASE_DIRECTORY_LOCATION + '28*')[0]
DEVICE_FILE_LOCATION = DEVICE_FOLDER_LOCATION + '/w1_slave'


def read_raw_temperature_from_the_sensor():
    f = open(DEVICE_FILE_LOCATION, 'r')
    lines = f.readlines()
    f.close()
    return lines


def get_celsius_temperature():
    lines = read_raw_temperature_from_the_sensor()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_raw_temperature_from_the_sensor()
    position = lines[1].find('t=')
    if position != -1:
        temp_string = lines[1][position + 2:]
        in_celsius = float(temp_string) / 1000.0
        return in_celsius


def publish_mqtt(payload):
    """
    Send an MQTT mesage to javaScript client
    """
    topic = 'temperature:recording'
    try:
        publish.single(topic, payload, hostname='127.0.0.1', port=1883, retain=False, qos=0)
    except Exception as err:
        print("Couldn't publish :" + str(err))
        pass


count = 0
try:
    while True:
        print(get_celsius_temperature())
        publish_mqtt(get_celsius_temperature())
        count += 1
        time.sleep(1)
except Exception as err:
    print('Error: ', err)
finally:
    print('')
    print('Cleaning up')
