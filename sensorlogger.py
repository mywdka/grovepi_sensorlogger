#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import grove_128_64_oled as oled
import pynmea2 as nmea
import serial
import sys
from stat import *
from time import sleep

SENSOR = 'sound'
if sys.argv[1] != '':
    SENSOR = sys.argv[1].strip().lower()

if SENSOR == 'sound':
    from sensors.sound import Sensor
    sensor = Sensor(0, 0.5)
elif SENSOR == 'dht':
    from sensors.dht import Sensor
    sensor = Sensor(4)
elif SENSOR == 'uv':
    from sensors.uv import Sensor
    sensor = Sensor(0)
elif SENSOR == 'dust':
    from sensors.dust import Sensor
    sensor = Sensor()
elif SENSOR == 'gas':
    from sensors.gas import Sensor
    sensor = Sensor(0)
elif SENSOR == 'air':
    from sensors.air import Sensor
    sensor = Sensor(0)
elif SENSOR == 'moist':
    from sensors.moist import Sensor
    sensor = Sensor(0)
elif SENSOR == 'simple_light':
    from sensors.simple_light import Sensor
    sensor = Sensor(0)





NETWORK_IFACE = 'eth0'
GPS_PATH = '/dev/ttyACM0'
GPS_CONNECTED = True
GPS_DISCONNECTED = False


OLED_LINE_SENSOR_TYPE = 0
OLED_LINE_GPS_LAT = 1
OLED_LINE_GPS_LON = 2
OLED_LINE_SENSOR_DATA1 = 3
OLED_LINE_SENSOR_DATA2 = 4
OLED_LINE_SPACER = 5
OLED_LINE_IP = 6
OLED_LINE_TIME = 7

LOG_PATH = '/boot/log.csv'
CSV_DELIMITER = '|'
LOG_HEADER = 'timestamp (UTC){delim}latitude{delim}longitude{delim}signal quality{delim}sensor type{delim}{sensor_hdr}\n'
LOG_FORMAT = '{time}{delim}{lat}{delim}{lon}{delim}{valid}{delim}{sensor}{delim}{value_str}\n'


external_ip = ''

gps_current_state = False
gps_port = None
nmea_stream = None

last_latlon = {'tstamp': '', 'lat':'51.9187771N', 'lon':'4.4863584E'}


def check_ip(iface):
    cmd = "ifconfig %s | grep inet |awk '{print $2}' | sed -e s/.*://" % (iface)
    return os.popen(cmd, "r").read().strip()

def check_for_gps(path):
    if os.path.exists(path) and S_ISCHR(os.stat(path).st_mode):
        return True
    return False

def oled_write_line(line, msg):
    oled.setTextXY(0, line)
    oled.putString('{0: <{1}}'.format(msg[0:16], 16))

def write_to_log(path, msg):
    with open(path, "a") as log:
        log.write(msg)
	log.flush()
	os.fsync(log.fileno())

def format_log_msg(delim='|', gps_time="", gps_lat="", gps_lon="", gps_quality=0, sensor_name="", value_str=""):
    return LOG_FORMAT.format(delim=delim, time=gps_time, lat=gps_lat, lon=gps_lon, valid=gps_quality, 
                             sensor=sensor_name, value_str=value_str)

oled.init()          #initialze SEEED OLED display
oled.clearDisplay()          #clear the screen and set start position to top left corner
#oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setInverseDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setPageMode()           #Set addressing mode to Page Mode

sensor.start()

write_to_log(LOG_PATH, LOG_HEADER.format(delim=CSV_DELIMITER, sensor_hdr=sensor.get_log_header(CSV_DELIMITER)))

oled_write_line(OLED_LINE_SENSOR_TYPE, "Sensor: %s" % (sensor.shortname))
oled_write_line(OLED_LINE_GPS_LAT, "GPS Disconnected")
oled_write_line(OLED_LINE_SPACER, "----------------")



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
                        tstamp = msg.timestamp.strftime("%H:%M:%S")
                        oled_write_line(OLED_LINE_TIME, tstamp)
                        last_latlon['tstamp'] = tstamp

                        if not msg.is_valid:
                            oled_write_line(OLED_LINE_GPS_LAT, "GPS Connected   ")
                            oled_write_line(OLED_LINE_GPS_LON, "Waiting for fix")
                        else:
                            lat = "%f" % (msg.latitude)
                            lon = "%f" % (msg.longitude)
                            oled_write_line(OLED_LINE_GPS_LAT, "lat %.7f" % (lat))
                            oled_write_line(OLED_LINE_GPS_LON, "lon %.7f" % (lon))
                            last_latlon['lat'] = lat
                            last_latlon['lon'] = lon

                        logmsg = format_log_msg(delim       = CSV_DELIMITER,
                                                gps_time    = last_latlon['tstamp'],
                                                gps_lat     = last_latlon['lat'],
                                                gps_lon     = last_latlon['lon'],
                                                gps_quality = msg.gps_qual,
                                                sensor_name = sensor.name,
                                                value_str   = sensor.get_log_string(CSV_DELIMITER))
                        print logmsg
                        write_to_log(LOG_PATH, logmsg)

            except nmea.ParseError as e:
                print e
            except UnicodeDecodeError as e:
                print e
            except Exception as e:
                print e
        else:
            sleep(0.01)

        oled_write_line(OLED_LINE_SENSOR_DATA1, sensor.get_str1())
        oled_write_line(OLED_LINE_SENSOR_DATA2, sensor.get_str2())

except KeyboardInterrupt:
    print "Quiting"
    if gps_port != None:
        nmea_stream = None
        gps_port.flushInput()
        gps_port.close()
    sensor.stop = True
    sensor.join()
    sys.exit()
