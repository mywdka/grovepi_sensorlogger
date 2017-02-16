import time
import math
import grovepi
from threading import Thread

class Sensor(Thread):
    # temp_humidity_sensor_type
    # Grove Base Kit comes with the blue sensor.
    blue = 0    # The Blue colored sensor.
    white = 1   # The White colored sensor.

    def __init__ (self, pin):
        Thread.__init__(self)
        self.name = "Grove humidity and temperature sensor"
        self.shortname = "hdt"
        self.pin = pin
        self.humidity = 0
        self.temp = 0
        self.stop = False

    def get_log_header(self, delimiter):
        return "temperature (C)%shumidity (%%)" % (delimiter)

    def get_log_string(self, delimiter):
        return "%.02f%c%.02f" % (self.temp, delimiter, self.humidity)

    def get_str1(self):
        return "temp: %.02fC" % (self.temp)

    def get_str2(self):
        return "hum : %.02f%%" % (self.humidity)

    def run(self):
        while not self.stop:
            try:
                [temp, humidity] = grovepi.dht(self.pin, self.blue)  
                if math.isnan(temp) == False and math.isnan(humidity) == False:
                    #print("temp = %.02f C humidity =%.02f%%" % (temp, humidity))
                    self.temp = temp
                    self.humidity = humidity
            except IOError as e:
                print ("Sound sensor exception: %s" % (e))

