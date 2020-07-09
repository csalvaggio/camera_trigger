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

   return True


if __name__ == '__main__':
   verbose = True

   camera = gp.Camera()

   try:
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

      directory = '/tmp'
      for capture_idx in range(2):
         iso8601_time_string = clocks.iso8601_time_string_using_computer_clock()
         basename = iso8601_time_string.replace(':', '-').replace('.', '-')
         basename += '_'
         basename += '{0}'.format(socket.gethostname())
         root = os.path.join(directory, basename)

         trigger_camera(camera, root, verbose)

      camera.exit()

   except KeyboardInterrupt:
      camera.exit()
      msg = '\n'
      msg += 'Exiting ...\n'
      sys.stdout.write(msg)
      sys.exit()
