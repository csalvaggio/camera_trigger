"""
   title::
      parse_nmea_sentences

   description::
      Parse NMEA sentences obtained from the gpsd socket using the gps3 module
         (https://pypi.org/project/gps3/)

      Be certain that the gpsd daemon is running.  To autostart at boot:
         sudo systemctl enable gpsd.socket
         sudo systemctl start gpsd.socket

      Available JSON objects produced are:
         (https://gpsd.gitlab.io/gpsd/gpsd_json.html)

      TPV - time-position-velocity report
      {
       'device': '/dev/serial0',
       'mode': 3,
       'time': '2020-07-07T14:23:17.000Z',
       'alt': 175.9,
       'climb': 0.0,
       'epc': 'n/a',
       'epd': 'n/a',
       'eps': 68.67,
       'ept': 0.005,
       'epv': 45.8,
       'epx': 40.3,
       'epy': 33.0,
       'tag': 'n/a',
       'lat': 43.099763,
       'lon': -77.438366167,
       'speed': 0.26,
       'track': 0.0
      }

      SKY - sky view of the GPS satellite positions
      {
       'gdop': 11.02,
       'hdop': 7.04,
       'pdop': 8.86
       'tdop': 6.35,
       'vdop': 5.38,
       'xdop': 6.83,
       'ydop': 2.09,
       'satellites':
          [{'PRN': 1, 'el': 17, 'az': 48, 'ss': 19, 'used': True},
           {'PRN': 2, 'el': 10, 'az': 230, 'ss': 0, 'used': False},
           {'PRN': 3, 'el': 35, 'az': 75, 'ss': 8, 'used': False},
           {'PRN': 6, 'el': 44, 'az': 224, 'ss': 0, 'used': False},
           {'PRN': 17, 'el': 72, 'az': 352, 'ss': 22, 'used': False},
           {'PRN': 19, 'el': 58, 'az': 300, 'ss': 0, 'used': False},
           {'PRN': 22, 'el': 24, 'az': 53, 'ss': 22, 'used': True},
              .
              .
              .
           {'PRN': 84, 'el': 15, 'az': 254, 'ss': 0, 'used': False}]
      }

      GST - pseudorange noise report
      {
       'device': '/dev/serial0',
       'time': '2020-07-09T12:45:38.000Z',
       'rms': 53.0,
       'major': 'n/a',
       'minor': 'n/a',
       'orient': 'n/a',
       'lat': 18.0,
       'lon': 53.0,
       'alt': 36.0,
      }

      ATT - vehicle-attitude report
      {
       'device': 'n/a',
       'time': 'n/a',
       'heading': 'n/a',
       'mag_st': 'n/a',
       'pitch': 'n/a',
       'pitch_st': 'n/a',
       'yaw': 'n/a',
       'yaw_st': 'n/a',
       'roll': 'n/a',
       'roll_st': 'n/a',
       'dip': 'n/a',
       'mag_len': 'n/a',
       'mag_x': 'n/a',
       'mag_y': 'n/a',
       'mag_z': 'n/a',
       'acc_len': 'n/a',
       'acc_x': 'n/a',
       'acc_y': 'n/a',
       'acc_z': 'n/a',
       'gyro_x': 'n/a',
       'gyro_y': 'n/a',
       'depth': 'n/a',
       'temperature': 'n/a'
      }

      PPS - message is emitted each time daemon sees a valid PPS (pulse
            per second) strobe from a device
      {
       'device': 'n/a',
       'real_sec': 'n/a',
       'real_nsec': 'n/a',
       'clock_sec': 'n/a',
       'clock_nsec': 'n/a',
       'precision': 'n/a'
      }

   author::
      Carl Salvaggio

   copyright::
      Copyright (C) 2020, Rochester Institute of Technology

   license::
      GPL

   version::
      1.0.0

   disclaimer::
      This source code is provided "as is" and without warranties as to 
      performance or merchantability. The author and/or distributors of 
      this source code may have made statements about this source code. 
      Any such statements do not constitute warranties and shall not be 
      relied on by the user in deciding whether to use this source code.
     
      This source code is provided without any express or implied warranties 
      whatsoever. Because of the diversity of conditions and hardware under 
      which this source code may be used, no warranty of fitness for a 
      particular purpose is offered. The user is advised to test the source 
      code thoroughly before relying on it. The user must assume the entire 
      risk of using the source code.
"""

from gps3 import gps3

import sys

gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()

gps_socket.connect()
gps_socket.watch()

try:
   for new_data in gps_socket:
      if new_data:
         data_stream.unpack(new_data)

         msg = 'Time:{0}'.format(data_stream.TPV['time'])

         msg += ' '
         latitude = data_stream.TPV['lat']
         if latitude == 'n/a':
            msg += 'Lat:{0}'.format(latitude)
         else:
            latitude = float(latitude)
            msg += 'Lat:{0:.9f}'.format(float(latitude))

         msg += ' '
         longitude = data_stream.TPV['lon']
         if longitude == 'n/a':
            msg += 'Lon:{0}'.format(longitude)
         else:
            longitude = float(longitude)
            msg += 'Lon:{0:.9f}'.format(float(longitude))

         msg += ' '
         msg += 'NMEA Mode:{0}'.format(data_stream.TPV['mode'])

         msg += ' '
         number_of_satellites = 0
         satellites = data_stream.SKY['satellites']
         for satellite in satellites:
            if type(satellite) == dict:
               if satellite['used']:
                  number_of_satellites += 1
         msg += 'Sats:{0:02d}'.format(number_of_satellites)

         print(msg)

except KeyboardInterrupt:
   msg = '\n'
   msg += '... Exiting'
   print(msg)
   sys.exit()
