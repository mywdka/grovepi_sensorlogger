import time
import grovepi
from threading import Thread

class Sound(Thread):
    def __init__ (self, pin, avg_fraction=0.8):
        Thread.__init__(self)
        self.pin = pin
        self.avg_fraction = avg_fraction
        self.value = 0
        self.avg_value = 0
        self.stop = False

        grovepi.pinMode(pin, "INPUT")

    def avg(self, current, new, fraction):
        return (current * (1.0-fraction)) + (new * fraction)

    def run(self):
        while not self.stop:
            try:
                self.value = grovepi.analogRead(self.pin)
                self.avg_value = self.avg(self.avg_value, self.value, self.avg_fraction)
                print self.value, self.avg_value
            except IOError as e:
                print ("Sound sensor exception: %s" % (e))
            time.sleep(0.01)
