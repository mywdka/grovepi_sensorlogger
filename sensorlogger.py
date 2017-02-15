#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import grove_128_64_oled as oled
import pynmea2 as nmea
import serial
import sys
from stat import *
from time import sleep

from sensors.sound import Sound

NETWORK_IFACE = 'eth0'
GPS_PATH = '/dev/ttyACM0'
GPS_CONNECTED = True
GPS_DISCONNECTED = False


OLED_LINE_SENSOR_TYPE = 0
OLED_LINE_GPS_LAT = 1
OLED_LINE_GPS_LON = 2
OLED_LINE_SENSOR_DATA = 3
OLED_LINE_SENSOR_DATA_AVG = 4
OLED_LINE_SPACER = 5
OLED_LINE_IP = 6
OLED_LINE_TIME = 7

external_ip = ""

gps_current_state = False
gps_port = None
nmea_stream = None

last_latlon = [None, None, None]


def check_ip(iface):
    cmd = "ifconfig %s | grep inet |awk '{print $2}' | sed -e s/.*://" % (iface)
    return os.popen(cmd, "r").read().strip()

def check_for_gps(path):
    if os.path.exists(path) and S_ISCHR(os.stat(path).st_mode):
        return True
    return False

def oled_write_line(line, msg, clear=True):
    oled.setTextXY(0, line)
    if clear:
        for i in range(16):
            oled.putChar(' ')
    oled.setTextXY(0, line)
    oled.putString(msg[0:16])

oled.init()          #initialze SEEED OLED display
oled.clearDisplay()          #clear the screen and set start position to top left corner
#oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setInverseDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setPageMode()           #Set addressing mode to Page Mode

oled_write_line(OLED_LINE_SENSOR_TYPE, "Sensor: Sound")
oled_write_line(OLED_LINE_GPS_LAT, "GPS Disconnected")
oled_write_line(OLED_LINE_SPACER, "----------------")

sensor = Sound(0, 0.5)
sensor.start()

try:
    while True:

        ip = check_ip(NETWORK_IFACE)
        if ip != external_ip:
            oled_write_line(OLED_LINE_IP, ip)
            external_ip = ip

        gps_new_state = check_for_gps(GPS_PATH)
        if gps_new_state != gps_current_state:
            if gps_new_state == GPS_CONNECTED:
                gps_port = serial.Serial(GPS_PATH, 9600, timeout=1)
                gps_port.flushInput()
                nmea_stream = nmea.NMEAStreamReader(gps_port, errors='raise')
            else:
                if gps_port != None:
                    nmea_stream = None
                    gps_port.flushInput()
                    gps_port.close()

            oled_write_line(OLED_LINE_GPS_LAT, "GPS %s" % ("Connected" if gps_new_state == GPS_CONNECTED else "Disconnected"))
            oled_write_line(OLED_LINE_GPS_LON, "")
            gps_current_state = gps_new_state

        if gps_current_state == GPS_CONNECTED and gps_port != None:
            try:
                for msg in nmea_stream.next():
                    if msg.sentence_type == 'GGA':
                        tstamp = msg.timestamp.strftime("%H:%M:%S UTC")
                        oled_write_line(OLED_LINE_TIME, tstamp, False)

                        if not msg.is_valid:
                            oled_write_line(OLED_LINE_GPS_LON, "Waiting for fix")
                        else:
                            lat = "%s %s%s" % (msg.lat[0:2], msg.lat[2:], msg.lat_dir)
                            lon = "%s %s%s" % (msg.lon[0:3], msg.lon[3:], msg.lon_dir)
                            oled_write_line(OLED_LINE_GPS_LAT, "lat %s" % (lat))
                            oled_write_line(OLED_LINE_GPS_LON, "lat %s" % (lat))
                            last_latlon = [msg.timestamp, lat, lon]
                            print last_latlon

            except nmea.ParseError as e:
                print e
            except UnicodeDecodeError as e:
                print e
            except Exception as e:
                print e
        else:
            time.sleep(1)

        oled_write_line(OLED_LINE_SENSOR_DATA,     "value: %.4d" % (sensor.value), False)
        oled_write_line(OLED_LINE_SENSOR_DATA_AVG, "Avg:   %.4d" % (sensor.avg_value), False)

except KeyboardInterrupt:
    print "Quiting"
    if gps_port != None:
        nmea_stream = None
        gps_port.flushInput()
        gps_port.close()
    sensor.stop = True
    sensor.join()
    sys.exit()
