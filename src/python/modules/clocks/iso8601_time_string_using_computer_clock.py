import datetime
import sys

def iso8601_time_string_using_computer_clock():
   iso8601_time_string = \
      datetime.datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
   return iso8601_time_string



if __name__ == '__main__':
   import clocks

   iso8601_time_string = clocks.iso8601_time_string_using_computer_clock()
   msg = iso8601_time_string
   msg += '\n'
   sys.stdout.write(msg)
