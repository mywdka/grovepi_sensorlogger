#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import grove_128_64_oled as oled
import pynmea2 as nmea
import serial
import sys
from stat import *
from threading import Timer
from time import sleep

GPS_PATH = '/dev/ttyACM0'
gps_available = False
gps_port = None
nmea_stream = None

def check_ip():
    external_ip = os.popen("ifconfig eth0|grep inet|awk '{print $2}' | sed -e s/.*://", "r").read().strip()
    oled.setTextXY(0, 0)
    for i in range(16):
        oled.putChar(' ')
    oled.setTextXY(0, 0)
    oled.putString(" %s" % (external_ip if external_ip != '' else "no IP"))
    t = Timer(10, check_ip)
    t.start()

def check_for_gps():
    global gps_available
    global gps_port
    global GPS_PATH
    global nmea_stream


    if not os.path.exists(GPS_PATH):
        gps_available = False
        if gps_port:
            try:
                gps_port.close()
            except:
                pass
            gps_port = None
        oled.setTextXY(0, 1)
        oled.putString("Turn GPS on    ")
    else:
        mode = os.stat(GPS_PATH)
        if S_ISCHR(mode.st_mode):
            if not gps_available:
                gps_available = True
                gps_port = serial.Serial(GPS_PATH, 9600)
                gps_port.flushInput()
                nmea_stream = nmea.NMEAStreamReader(gps_port, errors='raise')
                oled.putString("Wait for fix...")
    t = Timer(5, check_for_gps)
    t.start()

oled.init()          #initialze SEEED OLED display
oled.clearDisplay()          #clear the screen and set start position to top left corner
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setPageMode()           #Set addressing mode to Page Mode

check_ip()
check_for_gps()

try:
    while True:
        if gps_available and gps_port != None:
            try:
                for msg in nmea_stream.next():
                    #print str(msg)
                    if msg.sentence_type == 'GGA':
                        t = msg.timestamp.strftime("%H:%M:%S")
                        print t, msg.is_valid
                        if not msg.is_valid:
                            oled.setTextXY(0, 1)
                            oled.putString("Wait for fix...")
                        else:
                            lat = "%s %s%s" % (msg.lat[0:2], msg.lat[2:], msg.lat_dir)
                            lon = "%s %s%s" % (msg.lon[0:3], msg.lon[3:], msg.lon_dir)
                            alt = "%d" % (msg.altitude)
                            oled.setTextXY(0, 1)
                            oled.putString("lat %s" % (lat))
                            oled.setTextXY(0, 2)
                            oled.putString("lon %s" % (lon))
                            print lat, lon, alt
                        oled.setTextXY(0, 7)
                        oled.putString(t)
            except nmea.ParseError as e:
                print e
            except UnicodeDecodeError as e:
                print e
        else:
            sleep(1)
except KeyboardInterrupt:
    print "Quiting"
    if gps_port != None:
        gps_port.close()
    sys.exit()
