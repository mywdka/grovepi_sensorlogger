import time
import grovepi
from threading import Thread

class Sensor(Thread):
    def __init__ (self, pin, avg_fraction=0.8):
        Thread.__init__(self)
        self.name = "Grove sound sensor"
        self.shortname = "Sound"
        self.pin = pin
        self.avg_fraction = avg_fraction
        self.value = 0
        self.avg_value = 0
        self.stop = False

        grovepi.pinMode(pin, "INPUT")

    def get_log_header(self, delimiter):
        return "raw%caverage" % (delimiter)

    def get_log_string(self, delimiter):
        return "%.2f%c%.2f" % (self.value, delimiter, self.avg_value)

    def get_str1(self):
        return "val: %.2f" % (self.value)

    def get_str2(self):
        return "avg: %.2f" % (self.avg_value)

    def avg(self, current, new, fraction):
        return (current * (1.0-fraction)) + (new * fraction)

    def run(self):
        while not self.stop:
            try:
                self.value = grovepi.analogRead(self.pin)
                self.avg_value = self.avg(self.avg_value, self.value, self.avg_fraction)
            except IOError as e:
                print ("Sound sensor exception: %s" % (e))
            time.sleep(0.01)
