import time
import grovepi
from threading import Thread

class Sensor(Thread):
    def __init__ (self, pin, avg_fraction=0.8):
        Thread.__init__(self)
        self.name = "Grove UV sensor"
        self.shortname = "UV"
        self.pin = pin
        self.intensity = 0
        self.uv_index = 0
        self.stop = False

        grovepi.pinMode(pin, "INPUT")

    def get_log_header(self, delimiter):
        return "intensity (mW/m^2)%cUV index" % (delimiter)

    def get_log_string(self, delimiter):
        return "%.2f%c%.2f" % (self.intensity, delimiter, self.uv_index)

    def get_str1(self):
        return "illum: %.2f" % (self.intensity)

    def get_str2(self):
        return "uvidx: %.2f" % (self.uv_index)

    def run(self):
        while not self.stop:
            try:
                val = 0;
                for i in range(100):
                    sensorValue = grovepi.analogRead(self.pin)
                    val = sensorValue + val
                    time.sleep(0.002)

                avgVal = val / 100.0
                Vsig = avgVal * 0.0049
                self.intensity = Vsig * 307
                self.uv_index = self.intensity / 200
            except IOError as e:
                print ("Sound sensor exception: %s" % (e))

            time.sleep(0.02);
