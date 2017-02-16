import time
import grovepi
from threading import Thread

class Sensor(Thread):
    def __init__ (self, pin, avg_fraction=0.8):
        Thread.__init__(self)
        self.name = "Grove gas MQ9 sensor (CO, Coal, Liquified)"
        self.shortname = "Gas"
        self.pin = pin
        self.value = 0
        self.density = 0
        self.stop = False

        grovepi.pinMode(pin, "INPUT")

    def get_log_header(self, delimiter):
        return "density"

    def get_log_string(self, delimiter):
        return "%.2f" % (self.density)

    def get_str1(self):
        return "raw:  %.2f" % (self.value)

    def get_str2(self):
        return "dens: %.2f" % (self.density)

    def run(self):
        while not self.stop:
            try:
                self.value = grovepi.analogRead(self.pin)
                self.density = (float)(self.value / 1024.0)
                time.sleep(.5)
            except IOError as e:
                print ("gas sensor exception: %s" % (e))
            time.sleep(0.01)
