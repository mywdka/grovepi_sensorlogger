# USAGE
#
# Connect the dust sensor to Port 8 on the GrovePi. The dust sensor only works on that port
# The dust sensor takes 30 seconds to update the new values
#
# the fist byte is 1 for a new value and 0 for old values
# second byte is the concentration in pcs/0.01cf

import time
import grovepi
from threading import Thread

class Sensor(Thread):
    def __init__ (self):
        Thread.__init__(self)
        self.name = "Grove dust sensor"
        self.shortname = "dust"
        self.new_value = 0
        self.value = 0
        self.stop = False

        grovepi.dust_sensor_en()

    def get_log_header(self, delimiter):
        return "new value%cvalue (pcs/0.01cf)" % (delimiter)

    def get_log_string(self, delimiter):
        return "%d%c%.2f" % (self.new_value, delimiter, self.value)

    def get_str1(self):
        return "new val: %d" % (self.new_value)

    def get_str2(self):
        return "value  : %.2f" % (self.value)

    def run(self):
        while not self.stop:
            try:
                [new_val,lowpulseoccupancy] = grovepi.dustSensorRead()
                self.new_value = new_val
                self.value = lowpulseoccupancy
		time.sleep(5) 

            except IOError as e:
                print ("dust sensor exception: %s" % (e))
            
        grovepi.dust_sensor_dis()
