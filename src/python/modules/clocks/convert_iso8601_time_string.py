import sys

def convert_iso8601_time_string(time_string, units='s'):
   """
   title::
      convert_iso8601_time_string

   description::
      Convert provided ISO 8601 date/time string (e.g. 2005-06-08T10:34:48.283Z)
      to the specified units

   attributes::
      time_string
         A string containing and ISO 8601 timestamp
      units
         A string describing the units to convert to
            's': convert to truncated integer second
            's+': convert to rounded up (ceil) integer second
            's-': convert to rounded down (floor) integer second
            'S': convert to floating point seconds

   returns::
      A scalar containing the converted units

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

   Y = int(time_string[0:4])
   M = int(time_string[5:7])
   D = int(time_string[8:10])
   h = int(time_string[11:13])
   m = int(time_string[14:16])
   s = int(time_string[17:19])
   S = int(time_string[20:23])

   if units == 's' or units =='s-':
      converted = h * 3600
      converted += m * 60
      converted += s

   elif units =='s+':
      converted = h * 3600
      converted += m * 60
      converted += s
      converted += 1

   elif units == 'S':
      converted = h * 3600
      converted += m * 60
      converted += s
      converted += S / 1000

   else:
      msg = '\n'
      msg += '*** ERROR *** '
      msg += 'Invalid units provided for ISO 8601 time string conversion\n'
      msg += '\n'
      sys.stderr.write(msg)
      sys.exit()

   return converted



if __name__ == '__main__':
   import clocks

   iso8601_time_string = clocks.iso8601_time_string_using_computer_clock()
   msg = iso8601_time_string
   msg += '\n'
   sys.stdout.write(msg)

   seconds_since_midnight = \
      convert_iso8601_time_string(iso8601_time_string, 's')
   msg = 'Seconds since midnight (UTC): '
   msg += '{0}'.format(seconds_since_midnight)
   msg += '\n'
   sys.stdout.write(msg)
