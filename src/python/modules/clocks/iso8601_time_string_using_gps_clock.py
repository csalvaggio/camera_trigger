import sys

from gps3 import gps3

def iso8601_time_string_using_gps_clock(timeout = 30):
   gps_socket = gps3.GPSDSocket()
   data_stream = gps3.DataStream()

   gps_socket.connect()
   gps_socket.watch()

   try:
      attempt = 0
      for new_data in gps_socket:
         if new_data:
            attempt += 1;
            if attempt > timeout:
               iso8601_time_string = None
               break

            data_stream.unpack(new_data)

            # Determine the fix type that the GPS currntly has
            #    0 - no mode value yet seen
            #    1 - no fix
            #    2 - 2D
            #    3 - 3D
            mode = data_stream.TPV['mode']
            if mode == 'n/a':
               continue
            if int(mode) < 2:
               iso8601_time_string = None
               break

            iso8601_time_string = data_stream.TPV['time']
            if iso8601_time_string == 'n/a':
               continue
            break

      gps_socket.close()

   except KeyboardInterrupt:
      gps_socket.close()
      msg = '\n'
      msg += '... Exiting\n'
      sys.stdout.write(msg)
      sys.exit()

   return iso8601_time_string


if __name__ == '__main__':
   import clocks

   iso8601_time_string = clocks.iso8601_time_string_using_gps_clock()
   if iso8601_time_string:
      msg = iso8601_time_string
      msg += '\n'
      sys.stdout.write(msg)
   else:
      msg = '\n'
      msg += '*** ERROR *** '
      msg += 'GPS time was not available, check if fix was obtained\n'
      msg += '\n'
      sys.stderr.write(msg)
      sys.exit()
