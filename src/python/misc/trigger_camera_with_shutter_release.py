import argparse
import clocks
import RPi.GPIO
import sys
import time

def trigger_camera(half_press_time, full_press_time, verbose=False):
   mode = RPi.GPIO.BCM
   half_press_pin = 24
   full_press_pin = 23

   # Set up half- and full-press pins
   RPi.GPIO.setmode(mode)
   RPi.GPIO.setup(half_press_pin, RPi.GPIO.OUT)
   RPi.GPIO.setup(full_press_pin, RPi.GPIO.OUT)

   # Half press the shutter-release button (focus and exposure mode)
   if half_press_time > 0:
      if verbose:
         msg = '   '
         msg += 'Shutter half-pressed\n'
         sys.stdout.write(msg)
      RPi.GPIO.output(half_press_pin, True)
      time.sleep(half_press_time) 

   # Full press the shutter-release button (trigger)
   if full_press_time > 0:
      if verbose:
         msg = '   '
         msg += 'Shutter full-pressed\n'
         sys.stdout.write(msg)
      RPi.GPIO.output(full_press_pin, True)
      time.sleep(full_press_time) 

   # Release both the half- and full-press buttons
   if verbose:
      msg = '   '
      msg += 'Shutter released\n'
      sys.stdout.write(msg)
   RPi.GPIO.output(half_press_pin, False)
   RPi.GPIO.output(full_press_pin, False)

   return True


gpio_in_use = False

# Parse the command-line arguments
description = 'Trigger camera at specific clock-time instances'
parser = argparse.ArgumentParser(description=description)

help_message = 'clock-time [seconds] at which to trigger (e.g. '
help_message += '10 for every 10-second mark past the minute, '
help_message += '60 for the top of every minute, '
help_message += '3600 for the top of every hour)'
parser.add_argument('trigger_time',
                    type=int,
                    help=help_message)

help_message = 'verbose '
help_message += '[default is False]'
parser.add_argument('-v', '--verbose',
                    dest='verbose',
                    action='store_true',
                    default=False,
                    help=help_message)

help_message = 'clock to use (valid options are "computer" or "gps") '
help_message += '[default is "computer"]'
parser.add_argument('-c', '--clock-to-use',
                    dest='clock_to_use',
                    type=str,
                    choices=['computer', 'gps'],
                    default='computer',
                    help=help_message)

half_press_time = 0.0
help_message = 'half-press time [s] '
help_message += '[default is {0}]'.format(half_press_time)
parser.add_argument('-hp', '--half-press-time',
                    dest='half_press_time',
                    type=float,
                    default=half_press_time,
                    help=help_message)

full_press_time = 1.0
help_message = 'full-press time [s] '
help_message += '[default is {0}]'.format(full_press_time)
parser.add_argument('-fp', '--full-press-time',
                    dest='full_press_time',
                    type=float,
                    default=full_press_time,
                    help=help_message)

args = parser.parse_args()
trigger_time = args.trigger_time
verbose = args.verbose
clock_to_use = args.clock_to_use
half_press_time = args.half_press_time
full_press_time = args.full_press_time

# Check that the clock-time at which to trigger is greater than or equal
# to the minimum required for the specified half- and full-press times
# (round the minimum required time up to the next 5-second value)
minimum_required = int(((half_press_time + full_press_time + 1) // 5 + 1) * 5)
if trigger_time < minimum_required:
   msg = '\n'
   msg += '*** ERROR *** '
   msg += 'Clock-time at which to trigger must be >= '
   msg += '{0} [s]\n'.format(minimum_required)
   msg += '\n'
   sys.stderr.write(msg)
   sys.exit()

# Report the operating conditions
if verbose:
   msg = '\n'
   msg += 'Triggering camera every {0} [s] using '.format(trigger_time)
   msg += '{0} clock ...\n'.format(clock_to_use.upper())
   msg += 'Half-press time: {0} [s]\n'.format(half_press_time)
   msg += 'Full-press time: {0} [s]\n'.format(full_press_time)
   sys.stdout.write(msg)

# Continuously trigger the camera at the user-specified clock-time instances
first_trigger = True
while True:
   try:
      # Get the elapsed number of seconds since midnight
      if clock_to_use == 'computer':
         iso8601_time_string = clocks.iso8601_time_string_using_computer_clock()
         seconds_since_midnight = \
            clocks.convert_iso8601_time_string(iso8601_time_string, 's')
      else:
         iso8601_time_string = clocks.iso8601_time_string_using_gps_clock()
         if iso8601_time_string:
            seconds_since_midnight = \
               clocks.convert_iso8601_time_string(iso8601_time_string, 's')
         else:
            msg = '\n'
            msg += '*** ERROR *** '
            msg += 'GPS time was not available, check if fix was obtained\n'
            msg += '\n'
            sys.stderr.write(msg)
            sys.exit()

      # If the clock-time to trigger has arrived, start the triggering process
      if seconds_since_midnight % trigger_time == 0:

         # Skip the first trigger instance
         if first_trigger:
            first_trigger = False
            time.sleep(trigger_time)
            msg = '\n'
            sys.stdout.write(msg)
            continue

         # Report the trigger time
         if verbose:
            seconds = seconds_since_midnight
            hour = seconds // 3600
            seconds = seconds_since_midnight - hour * 3600
            minute = seconds // 60
            seconds = seconds - minute * 60 
            msg = 'Triggering process started at '
            msg += '{0:02d}:'.format(hour)
            msg += '{0:02d}:'.format(minute)
            msg += '{0:02d}\n'.format(seconds)
            sys.stdout.write(msg)

         # Trigger the camera
         trigger_camera(half_press_time, full_press_time, verbose)
         gpio_in_use = True

         # Delay execution until the next second
         time.sleep(1)

   except KeyboardInterrupt:
      if verbose:
         if gpio_in_use:
            msg = '\n'
            msg += '... Cleaning up GPIO resources'
            sys.stdout.write(msg)
            RPi.GPIO.cleanup()
         msg = '\n'
         msg += '... Exiting'
         sys.stdout.write(msg)
      msg = ''
      sys.exit(msg)
