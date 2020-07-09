#!/bin/bash

current_directory=$(pwd)

cd $HOME/src/scripts/RPiAdHocWiFi
sudo ./revert.sh

cd $current_directory
