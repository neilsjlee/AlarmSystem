# https://peppe8o.com/use-active-buzzer-with-raspberry-pi-and-python/
# sudo apt install rpi.gpio

import sys
import RPi.GPIO as GPIO
import time

# Set trigger PIN according with your cabling
signalPIN = 14

# Set PIN to output
GPIO.setmode(GPIO.BCM)
GPIO.setup(signalPIN,GPIO.OUT)

# this row makes buzzer work for 1 second, then
# cleanup will free PINS and exit will terminate code execution

GPIO.output(signalPIN,1)
time.sleep(5)

GPIO.cleanup()
sys.exit()
