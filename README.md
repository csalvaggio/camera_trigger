# CAMERA TRIGGER

## INTRODUCTION
This repository contains the ``/home/pi`` folder for the Raspberry Pi appliance developed to trigger a DSLR at specific computer or GPS clock times using either a USB connection with GPhoto2 or the custom designed PCB created for use with a shutter release cable.

## HARDWARE REQUIRED
* [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
* [BerryGPS-IMU V3](https://ozzmaker.com/product/berrygps-imu/)
* [PiSugar](https://www.pisugar.com)

## INSTALLATION
* Install the **Raspberry Pi OS Full** operating system on an SD card using one of the recommended methods:
    * [Raspberry Pi Imager for Windows](https://downloads.raspberrypi.org/imager/imager.exe)
    * [Raspberry Pi Imager for macOS](https://downloads.raspberrypi.org/imager/imager.dmg)
    * [Raspberry Pi Imager for Ubuntu](https://downloads.raspberrypi.org/imager/imager_amd64.deb)
* Boot your Raspberry Pi
* Configure the BerryGPS-IMU V3 by following the [BerryGPS Setup Guide for Raspberry Pi](https://ozzmaker.com/berrygps-setup-guide-raspberry-pi/)
* Install [gps3](https://pypi.org/project/gps3/)

        sudo pip install gps3

* Install the following packages

        sudo apt-get install dcraw
        sudo apt-get install gpsd \
                             gpsd-clients
        sudo apt-get install gphoto2 \
                             libgphoto2-6 \
                             libgphoto2-dev \
                             libgphoto2-dev-doc \
                             libgphoto2-l10n \
                             libgphoto2-port12 \
                             python-gphoto2-doc \
                             python-gphoto2cffi \
                             python-piggyphoto \
                             python3-gphoto2 \
                             python3-gphoto2cffi
        sudo apt-get install vim
        
* Configure the following cron jobs - type ``crontab -e`` and insert the following

        * * * * * pkill -f gvfs-gphoto2-volume-monitor
        * * * * * pkill -f gvfsd-gphoto2

* With a DSLR connected to the Raspberry Pi via a USB cable
Check where gphoto2 is saving images on the camera ...

        gphoto2 --get-config capturetarget
           Label: Capture Target                                                          
           Readonly: 0
           Type: RADIO
           Current: Internal RAM    <--------
           Choice: 0 Internal RAM
           Choice: 1 Memory card
           END
Configure images to be saved to the SD card on the camera ...

        gphoto2 --set-config capturetarget=1
        gphoto2 --get-config capturetarget
           Label: Capture Target                                                          
           Readonly: 0
           Type: RADIO
           Current: Memory card     <---------
           Choice: 0 Internal RAM
           Choice: 1 Memory card
           END

* In the ``/home/pi`` directory, clone this repository

        git clone git@github.com:csalvaggio/camera_trigger.git
