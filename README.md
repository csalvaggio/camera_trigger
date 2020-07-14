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

* Perform headless configuration (on your setup machine)

    * Wireless networking

        Define a wpa_supplicant.conf file for your particular wireless network. Put this file in the /boot partition, and when the Pi first boots, it will copy that file into the correct location in the Linux root file system and use those settings to start up wireless networking.

         *wpa_supplicant.conf*

            ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
            update_config=1
            country=US

            network={
            	ssid="<insert your SSID here>"
            	psk="<insert your network's WPA passphrase here>"
            	key_mgmt=WPA-PSK
            }

    * Enable SSH

        For headless setup, SSH can be enabled by placing an empty file named ``ssh``, without any extension, onto the /boot partition of the SD card. When the Pi boots, it looks for the ``ssh`` file. If it is found, SSH is enabled and the file is deleted.

* Change the hostname as described [here](#duplicating-camera-trigger)

* If it is still mounted, eject your SD card making sure you eject all partitions (under macOS you may use the ``diskutil`` command, *e.g.* ``diskutil umountDisk /dev/disk2`` where ``/dev/disk2`` is the name for the mounted volume)

* Insert your card and boot your Raspberry Pi for the first time

* Change the password for the ``pi`` account after this first boot [recommended]

* Set time zone to UTC

        sudo raspi-config

    **Localisation Options > Change Time Zone > None of the above > UTC**

* Enable VNC

        sudo raspi-config

    **Interfacing Options > VNC > Yes**

* Update and upgrade your Raspberry Pi

        sudo apt-get update
        sudo apt-get upgrade
        sudo apt-get autoremove

* Configure the BerryGPS-IMU V3 - The manufacturer's instructions may be found in the article [BerryGPS Setup Guide for Raspberry Pi](https://ozzmaker.com/berrygps-setup-guide-raspberry-pi/) and are summarized below 

  * The serial console needs to be disabled and the the serial port enabled

            sudo raspi-config

        **Interfacing Options > Serial > No > Yes** and **Yes** to reboot

  * Test that the GPS is operating properly (serial)
 
            cat /dev/serial0

  * Install ``gpsd``. ``gpsd`` is a daemon that receives data from a GPS receiver, and provides the data back to multiple applications through a socket.

            sudo apt-get install gpsd-clients gpsd

  * Edit the ``gpsd`` configuration file so that the daemon uses the correct serial device

            sudo vi /etc/default/gpsd

        Look for ``DEVICES=""`` and change it to ``DEVICES="/dev/serial0"``

  * Make sure that ``gpsd`` starts automatically at boot time

            sudo systemctl stop gpsd.socket
            sudo systemctl disable gpsd.socket
            sudo systemctl enable gpsd.socket
            sudo systemctl start gpsd.socket

            sudo reboot

  * Test that the GPS is operating properly (socket)

            gpspipe -r

* Install [gps3](https://pypi.org/project/gps3/)

        sudo pip2 install gps3
        sudo pip3 install gps3

* Configure and test ``gphoto2``

  * Install the following packages
  
            sudo apt-get install gphoto2 libgphoto2-6 libgphoto2-dev libgphoto2-dev-doc libgphoto2-l10n libgphoto2-port12 python-gphoto2-doc python-gphoto2cffi python-piggyphoto python3-gphoto2 python3-gphoto2cffi

  * With a DSLR connected to the Raspberry Pi via a USB cable, check where ``gphoto2`` is saving images on the camera

            gphoto2 --get-config capturetarget
               Label: Capture Target
               Readonly: 0
               Type: RADIO
               Current: Internal RAM    <--------
               Choice: 0 Internal RAM
               Choice: 1 Memory card
               END

     If ``gphoto2`` indicates that it is currently saving to the ``Internal RAM`` as above, then configure ``gphoto2`` so that captured images are saved to the SD card on the camera

            gphoto2 --set-config capturetarget=1
            gphoto2 --get-config capturetarget
               Label: Capture Target
               Readonly: 0
               Type: RADIO
               Current: Memory card     <---------
               Choice: 0 Internal RAM
               Choice: 1 Memory card
               END

* Install these remaining packages

        sudo apt-get install vim
        sudo apt-get install dcraw
        sudo apt-get install udhcpd

* Clean up the ``/home/pi`` directory

        rm -fr Bookshelf Desktop Documents Downloads Music Pictures Public Templates Videos

* In the ``/home/pi`` directory, checkout this repository

        cd /home/pi
        git init
        git remote add origin https://github.com/csalvaggio/camera_trigger.git
        git fetch
        git checkout -f master

* Log out and log back in

* Configure maintenance cron jobs by typing ``crontab -e`` and inserting the following at the end of the crontab file

        * * * * * pkill -f gvfs-gphoto2-volume-monitor
        * * * * * pkill -f gvfsd-gphoto2

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

## MAINTENANCE
### DUPLICATING CAMERA TRIGGER
To create an additional camera trigger, [create a byte-for-byte copy of the SD card](https://appcodelabs.com/how-to-backup-clone-a-raspberry-pi-sd-card-on-macos-the-easy-way) created above.  While this is technically all that needs done, it is recommended that the computer's name is changed so that any ad hoc wireless network that is created will have a different name and will not interfere with other triggers in close proximity.

Once the card is duplicated, change the hostname using a macOS computer equipped with [Paragon Software's extFS](https://www.paragon-software.com/home/extfs-mac/) application.  Insert the Raspberry Pi's SD card in the Mac.  You will notice that two partitions are mounted; ``boot`` and ``rootfs``.  The ``rootfs`` partition is the Raspberry Pi's main filesystem.  The hostname (*e.g.* ``cameratriggermaster``) needs to be changed in two places on that filesystem

*/etc/hostname*

    cameratriggermaster

and in

*/etc/hosts*

    127.0.0.1	localhost
    ::1			localhost ip6-localhost ip6-loopback
    ff02::1		ip6-allnodes
    ff02::2		ip6-allrouters

    127.0.1.1	cameratriggermaster

This can be done manually using your favorite editor (*e.g.* vi, nano, emacs, or Xcode) or by executing the following script

*change\_rpi\_hostname.sh*

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

executed as

    ./change_rpi_hostname.sh cameratriggermaster cameratrigger0

where ``cameratriggermaster`` is the original hostname and ``cameratrigger0`` is the desired hostname for the duplicate.

### SWITCHING NETWORK TYPE
#### LAN -> AD HOC
##### On Raspberry Pi
While logged on to the Raspberry Pi, to switch to an ad hoc network at next reboot

    switch_to_adhoc

##### Off Raspberry Pi
The ad hoc network can be switched on for the next boot by executing the following script

*switch\_to\_adhoc.sh*

    #!/bin/bash

    #
    # Install script for RPiAdHocWifi (from macOS)
    #

    LOCAL_MNT="/Volumes/rootfs"
    SCRIPT_DIR=$LOCAL_MNT/home/pi/src/scripts/RPiAdHocWiFi

    # Check if Raspberry Pi card is inserted and mounted
    if [ ! -e $LOCAL_MNT ]
    then
       echo "'rootfs' partition not found, be sure RPi SD card is inserted"
       exit
    fi

    touch $LOCAL_MNT/var/lib/misc/udhcpd.leases

    # Make backups of existing files
    if [ -e $LOCAL_MNT/etc/rc.local ]
    then
        cp $LOCAL_MNT/etc/rc.local $LOCAL_MNT/etc/rc.local.adhoc_bak
    fi

    if [ -e $LOCAL_MNT/etc/udhcpd.conf ]
    then
        cp $LOCAL_MNT/etc/udhcpd.conf $LOCAL_MNT/etc/udhcpd.conf.adhoc_bak
    fi

    if [ -e $LOCAL_MNT/etc/dhcpcd.conf ]
    then
        cp $LOCAL_MNT/etc/dhcpcd.conf $LOCAL_MNT/etc/dhcpcd.conf.adhoc_bak
    fi

    # Copy new files
    cp $SCRIPT_DIR/rc.local $LOCAL_MNT/etc
    cp $SCRIPT_DIR/udhcpd.conf $LOCAL_MNT/etc
    cp $SCRIPT_DIR/dhcpcd.conf $LOCAL_MNT/etc

    echo "Ad hoc network will start at next boot."
    exit 0

which is executed as

    ./switch_to_adhoc.sh

#### AD HOC -> LAN
##### On Raspberry Pi
To allow the Raspberry Pi to rejoin LAN at next reboot

    switch_to_lan

##### Off Raspberry Pi
To allow the Raspberry Pi to rejoin LAN at next reboot by executing the following script

*switch\_to\_lan.sh*

    #!/bin/bash

    #
    # Reversion script for RPiAdHocWifi (from macOS)
    #

    LOCAL_MNT="/Volumes/rootfs"
    SCRIPT_DIR=$LOCAL_MNT/home/pi/src/scripts/RPiAdHocWiFi

    # Check if Raspberry Pi card is inserted and mounted
    if [ ! -e $LOCAL_MNT ]
    then
       echo "'rootfs' partition not found, be sure RPi SD card is inserted"
       exit
    fi

    # Restore from backups if they exist or delete the files
    if [ -e $LOCAL_MNT/etc/rc.local.adhoc_bak ]
    then
        cp $LOCAL_MNT/etc/rc.local.adhoc_bak $LOCAL_MNT/etc/rc.local
    fi
    rm $LOCAL_MNT/etc/rc.local.adhoc_bak

    if [ -e $LOCAL_MNT/etc/udhcpd.conf.adhoc_bak ]
    then
        cp $LOCAL_MNT/etc/udhcpd.conf.adhoc_bak $LOCAL_MNT/etc/udhcpd.conf
    else
        rm $LOCAL_MNT/etc/udhcpd.conf
    fi
    rm $LOCAL_MNT/etc/udhcpd.conf.adhoc_bak

    if [ -e $LOCAL_MNT/etc/dhcpcd.conf.adhoc_bak ]
    then
        cp $LOCAL_MNT/etc/dhcpcd.conf.adhoc_bak $LOCAL_MNT/etc/dhcpcd.conf
    else
        rm $LOCAL_MNT/etc/dhcpcd.conf
    fi
    rm $LOCAL_MNT/etc/dhcpcd.conf.adhoc_bak

    echo "Raspberry Pi will join LAN at next boot."
    exit 0

which is executed as

    ./switch_to_lan.sh
