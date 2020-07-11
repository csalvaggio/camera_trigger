import argparse
import clocks
import os.path
import socket
import sys
import time

import gphoto2 as gp

def trigger_camera(camera, root=None, verbose=False):
   """
   IMPORTANT NOTE:
   When using this capture method, the camera must be set to capture RAW or
   JPG only, NOT BOTH
   """
   camera_filepath = camera.capture(gp.GP_CAPTURE_IMAGE)
   if verbose:
      msg = '   '
      msg += 'Camera triggered\n'
      sys.stdout.write(msg)

   if root:
      camera_file = \
         camera.file_get(camera_filepath.folder,
                         camera_filepath.name,
                         gp.GP_FILE_TYPE_NORMAL)

      filename = root + os.path.splitext(camera_filepath.name)[1].lower()
      camera_file.save(filename)
      del camera_file
      if verbose:
         msg = '   '
         msg += 'Image written to {0}\n'.format(filename)
         sys.stdout.write(msg)

   del camera_filepath


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

directory = None
help_message = 'directory to save images to '
help_message += '[default is {0}]'.format(directory)
parser.add_argument('-d', '--directory',
                    dest='directory',
                    type=str,
                    default=directory,
                    help=help_message)

args = parser.parse_args()
trigger_time = args.trigger_time
verbose = args.verbose
clock_to_use = args.clock_to_use
directory = args.directory

# Check that the clock-time at which to trigger is greater than or equal
# to the minimum required
minimum_required = 5
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
   sys.stdout.write(msg)

# Check that the output directory exists and is writeable
directory_ok = False
if directory:
   exists = os.access(directory, os.F_OK)
   writeable = os.access(directory, os.W_OK | os.X_OK)
   if exists and writeable:
      directory_ok = True
   else:
      msg = '\n'
      msg += '*** ERROR *** '
      msg += 'Specified target directory does not exist or is not writeable\n'
      msg += '\n'
      sys.stderr.write(msg)
      sys.exit()

# Initialize camera for access over USB
camera = gp.Camera()

while True:
   try:
      camera.init()
   except gp.GPhoto2Error as exception:
      if exception.code == gp.GP_ERROR_MODEL_NOT_FOUND:
         msg = '*** ERROR *** '
         msg += 'Camera not found, please connect and switch on camera\n'
         sys.stderr.write(msg)
         try:
            time.sleep(2)
         except KeyboardInterrupt:
            msg = '\n'
            msg += 'Exiting ...\n'
            sys.stdout.write(msg)
            sys.exit()
         continue
      raise
   break

# Continuously trigger the camera at the user-specified clock-time instances
try:
   first_trigger = True
   while True:
      # Get the elapsed number of seconds since midnight
      if clock_to_use == 'computer':
         iso8601_time_string = clocks.iso8601_time_string_using_computer_clock()
         seconds_since_midnight = \
            clocks.convert_iso8601_time_string(iso8601_time_string, 's')
      else:
         first_clock_check = True
         while True:
            iso8601_time_string = clocks.iso8601_time_string_using_gps_clock()
            if iso8601_time_string:
               seconds_since_midnight = \
                  clocks.convert_iso8601_time_string(iso8601_time_string, 's')
               break
            else:
               if first_clock_check:
                  first_clock_check = False
                  msg = '\n'
                  sys.stderr.write(msg)
               msg = '*** ERROR *** '
               msg += 'GPS time was not available, continuing to try ...\n'
               sys.stderr.write(msg)
               time.sleep(0.5)
               continue

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
         if directory:
            basename = iso8601_time_string.replace(':', '-').replace('.', '-')
            basename += '_'
            basename += '{0}'.format(socket.gethostname())
            root = os.path.join(directory, basename)
         else:
            root = None
         trigger_camera(camera, root, verbose)

         # Delay execution until the next second
         time.sleep(1)

except KeyboardInterrupt:
   camera.exit()
   if verbose:
      msg = '\n'
      msg += '... Exiting'
      sys.stdout.write(msg)
   msg = ''
   sys.exit(msg)
