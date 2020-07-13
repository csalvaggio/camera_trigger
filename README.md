# CAMERA TRIGGER

## INTRODUCTION
This repository contains the ``/home/pi`` folder for the Raspberry Pi appliance developed to trigger a DSLR at specific computer or GPS clock times using either a USB connection with GPhoto2 or the custom designed PCB created for use with a shutter release cable.

## HARDWARE REQUIRED
* [Raspberry Pi Zero W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
* [BerryGPS-IMU V3](https://ozzmaker.com/product/berrygps-imu/)
* [PiSugar](https://www.pisugar.com)

## DEPENDENCIES
* argparse
* clocks (located in and installed as part of this repository)
* gphoto2
* gps3
* RPi.GPIO

## INSTALLATION
* Install the **Raspberry Pi OS Full** operating system on an SD card using one of the recommended methods
    * [Raspberry Pi Imager for Windows](https://downloads.raspberrypi.org/imager/imager.exe)
    * [Raspberry Pi Imager for macOS](https://downloads.raspberrypi.org/imager/imager.dmg)
    * [Raspberry Pi Imager for Ubuntu](https://downloads.raspberrypi.org/imager/imager_amd64.deb)

* Boot your Raspberry Pi

* Configure your Raspberry Pi so that it may connect to your local area network and access the Internet

* Update and upgrade your Raspberry Pi

        sudo apt-get update
        sudo apt-get upgrade

* Install the following packages

        sudo apt-get install vim
        sudo apt-get install dcraw
        sudo apt-get install udhcpd
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

* In the ``/home/pi`` directory, clone this repository

        git clone https://github.com/csalvaggio/camera_trigger.git

* Configure the BerryGPS-IMU V3 by following the [BerryGPS Setup Guide for Raspberry Pi](https://ozzmaker.com/berrygps-setup-guide-raspberry-pi/) and make sure that ``gpsd`` starts automatically at boot time

        sudo systemctl stop gpsd.socket
        sudo systemctl disable gpsd.socket
        sudo systemctl enable gpsd.socket
        sudo systemctl start gpsd.socket

* Install [gps3](https://pypi.org/project/gps3/)

        sudo pip2 install gps3
        sudo pip3 install gps3

* Configure maintenance cron jobs by typing ``crontab -e`` and inserting the following at the end of the crontab file

        * * * * * pkill -f gvfs-gphoto2-volume-monitor
        * * * * * pkill -f gvfsd-gphoto2

* With a DSLR connected to the Raspberry Pi via a USB cable, check where gphoto2 is saving images on the camera

        gphoto2 --get-config capturetarget
           Label: Capture Target                                                          
           Readonly: 0
           Type: RADIO
           Current: Internal RAM    <--------
           Choice: 0 Internal RAM
           Choice: 1 Memory card
           END
If gphoto2 indicates that it is currently saving to the ``Internal RAM`` as above, then configure gphoto2 so that captured images are saved to the SD card on the camera

        gphoto2 --set-config capturetarget=1
        gphoto2 --get-config capturetarget
           Label: Capture Target                                                          
           Readonly: 0
           Type: RADIO
           Current: Memory card     <---------
           Choice: 0 Internal RAM
           Choice: 1 Memory card
           END

## CREATE DUPLICATE CAMERA TRIGGER
To create an additional camera trigger, [create a byte-for-byte copy of the SD card](https://appcodelabs.com/how-to-backup-clone-a-raspberry-pi-sd-card-on-macos-the-easy-way) created above.  While this is technically all that needs done, it is recommended that the computer's name is changed so that any ad hoc wireless network that is created will have a different name and will not interfere with other triggers in close proximity.

Once the card is duplicated, change the hostname using a macOS computer equipped with [Paragon Software's extFS](https://www.paragon-software.com/home/extfs-mac/) application.  Insert the Raspberry Pi's SD card in the Mac.  You will notice that two partitions are mounted; ``boot`` and ``rootfs``.  The ``rootfs`` partition is the Raspberry Pi's main filesystem.  The hostname (*e.g.* ``cameratriggermaster``) needs to be changed in two places on that filesystem; in ``/etc/hostname``

    cameratriggermaster

and in ``/etc/hosts``

    127.0.0.1	localhost
    ::1		localhost ip6-localhost ip6-loopback
    ff02::1		ip6-allnodes
    ff02::2		ip6-allrouters

    127.0.1.1	cameratriggermaster

This can be done manually using your favorite editor (*e.g.* vi, nano, emacs, or Xcode) or by executing the following script that should be named ``change_rpi_hostname.sh``

    #!/bin/bash

    OLD_HOST=$1
    NEW_HOST=$2

    DISK="/dev/"
    DISK+=`diskutil list | grep rootfs | awk -v N=6 '{print substr($N,0,5)}'`

    if [ $DISK = "/dev/" ]
    then
       echo "'rootfs' partition not found, be sure RPi SD card is inserted"
       exit
    fi

    if [ -z $OLD_HOST ] || [ -z $NEW_HOST ]
    then
       echo "Usage: $0 <old hostname> <new hostname>"
       exit
    else
       echo "Updating hostname from '$OLD_HOST' to '$NEW_HOST' on $DISK"

       echo ""
       echo "***** /etc/hostname (ORIGINAL)"
       cat  /Volumes/rootfs/etc/hostname
       sed -i -e "s/$OLD_HOST/$NEW_HOST/g" /Volumes/rootfs/etc/hostname
       echo ""
       echo "***** /etc/hostname (UPDATED)"
       cat  /Volumes/rootfs/etc/hostname

       echo ""
       echo "***** /etc/hosts (ORIGINAL)"
       cat  /Volumes/rootfs/etc/hosts
       sed -i -e "s/$OLD_HOST/$NEW_HOST/g" /Volumes/rootfs/etc/hosts
       echo ""
       echo "***** /etc/hosts (UPDATED)"
       cat  /Volumes/rootfs/etc/hosts

       echo ""
       echo "Unmounting $DISK"
       diskutil umountDisk $DISK
    fi

by executed as

    ./change_rpi_hostname.sh cameratriggermaster cameratrigger0

where ``cameratriggermaster`` is the original hostname and ``cameratrigger0`` is the desired hostname for the duplicate.

## USAGE
At this point, the system is ready to use as a camera triggering system using either a shutter release cable (assuming the custom camera trigger board is attached) or a USB cable (using GPhoto2).

To use the shutter release cable

    # python3 trigger_camera_with_shutter_release.py --help
    usage: trigger_camera_with_shutter_release.py [-h] [-v] [-c {computer,gps}]
                                              [-hp HALF_PRESS_TIME]
                                              [-fp FULL_PRESS_TIME]
                                              trigger_time

    Trigger camera at specific clock-time instances

    positional arguments:
      trigger_time          clock-time [seconds] at which to trigger (e.g. 10 for
                            every 10-second mark past the minute, 60 for the top
                            of every minute, 3600 for the top of every hour)

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose [default is False]
      -c {computer,gps}, --clock-to-use {computer,gps}
                            clock to use (valid options are "computer" or "gps")
                            [default is "computer"]
      -hp HALF_PRESS_TIME, --half-press-time HALF_PRESS_TIME
                            half-press time [s] [default is 0.0]
      -fp FULL_PRESS_TIME, --full-press-time FULL_PRESS_TIME
                            full-press time [s] [default is 1.0]

To use the USB cable

    # python3 trigger_camera_with_usb.py --help
    usage: trigger_camera_with_usb.py [-h] [-v] [-c {computer,gps}] [-d DIRECTORY]
                                      trigger_time

    Trigger camera at specific clock-time instances

    positional arguments:
      trigger_time          clock-time [seconds] at which to trigger (e.g. 10 for
                            every 10-second mark past the minute, 60 for the top
                            of every minute, 3600 for the top of every hour)

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         verbose [default is False]
      -c {computer,gps}, --clock-to-use {computer,gps}
                            clock to use (valid options are "computer" or "gps")
                            [default is "computer"]
      -d DIRECTORY, --directory DIRECTORY
                            directory to save images to [default is None]

While logged on to the Raspberry Pi, to switch on ad hoc network at next reboot

    switch_to_adhoc

To allow the Raspberry Pi to rejoin LAN at next reboot

    switch_to_lan
