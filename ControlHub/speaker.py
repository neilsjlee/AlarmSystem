# https://peppe8o.com/use-active-buzzer-with-raspberry-pi-and-python/
# sudo apt install rpi.gpio

import RPi.GPIO as GPIO
import threading
import time
import datetime


class Speaker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.speaker_pin = 23
        self.speaker_off_button_pin = 24
        self.on_when_true = False
        self.print_time_measurement = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.speaker_pin, GPIO.OUT)
        GPIO.setup(self.speaker_off_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def buzzer_on(self):
        print("[SPEAKER] BUZZER FLAG TURNED ON")
        self.on_when_true = True

    def buzzer_off(self):
        print("[SPEAKER] BUZZER FLAG TURNED OFF")
        self.on_when_true = False

    def run(self):
        try:
            while(True):
                time1 = datetime.datetime.now()
                if self.on_when_true:
                    GPIO.output(self.speaker_pin, True)
                else:
                    GPIO.output(self.speaker_pin, False)
                button_state = GPIO.input(self.speaker_off_button_pin)
                if button_state == False:
                    self.print_time_measurement = True
                    print("[SPEAKER] BUZZER OFF BUTTON PRESSED")
                    self.on_when_true = False
                    time2 = datetime.datetime.now()
                    if self.print_time_measurement == True:
                        print("LAST LOOP -> BUTTON PRESS DETECTED: ", (time1 - time3))
                        print("BUTTON PRESS DETECTED -> SPEAKER OFF: ", (time2 - time1))
                        self.print_time_measurement = False
                time3 = datetime.datetime.now()
                time.sleep(0.01)
        except KeyboardInterrupt:
            GPIO.cleanup()

