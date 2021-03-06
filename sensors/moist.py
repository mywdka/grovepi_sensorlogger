# NOTE: # Wait 2 minutes for the sensor to heat-up

import time
import grovepi
from threading import Thread

class Sensor(Thread):
    def __init__ (self, pin):
        Thread.__init__(self)
        self.name = "Moisture sensor"
        self.shortname = "Moist"
        self.pin = pin
        self.value = 0
        self.interpretation = ''
        self.stop = False

        grovepi.pinMode(pin, "INPUT")

    def get_log_header(self, delimiter):
        return "%s%c%s" % ("value", delimiter, "interpretation")

    def get_log_string(self, delimiter):
        return "%.2f%c%s" % (self.value, delimiter, self.interpretation)

    def get_str1(self):
        return "raw:  %.2f" % (self.value)

    def get_str2(self):
        return self.interpretation

    def run(self):
        while not self.stop:
            try:
                self.value = grovepi.analogRead(self.pin)
                if self.value > 700:
                    self.interpretation = "in water"
                elif self.value > 300:
                    self.interpretation = "humid soil"
                elif self.value > 20:
                    self.interpretation = "dry soil"
                else:
                    self.interpretation = "open air"
            except IOError as e:
                print ("Moist sensor exception: %s" % (e))
            time.sleep(.5)
