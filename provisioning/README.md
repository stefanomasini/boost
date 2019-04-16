# Provisioning

## Raspberry PI

Raspbian Stretch Lite
  - Version: April 2019
  - Release date: 2019-04-08
  - Kernel version: 4.14
  - [Image download page](https://www.raspberrypi.org/downloads/raspbian/)
  - [Installation instructions](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)
  
## Pre-provisioning

 - [Raspbian installation instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md): wrote the image to the SD card using `dd`
 - Uncommented `dtparam=i2c_arm=on` in `config.txt` in the boot partition (from the Mac) to activate I2C
 - Changed default password for `pi` user
 - [Activate SSH server](https://www.raspberrypi.org/documentation/remote-access/ssh/)
 - Configured public-key login:
     
       # "pi" user
       mkdir .ssh
       chmod 700 .ssh
       curl -o .ssh/authorized_keys https://github.com/stefanomasini.keys
       
       # "root" user
       sudo su -
       mkdir .ssh
       chmod 700 .ssh
       curl -o .ssh/authorized_keys https://github.com/stefanomasini.keys
       
 - Activate I2C
 
   - `sudo raspi-config`
   - `5 Interfacing Options`
   - `P5 I2C`
   - `Would you like the ARM I2C interface to be enabled?` -> `Yes`

 - Update Raspbian:
 
       sudo apt-get update


## Provisioning

 - Install Ansible dependencies
 
       ansible-galaxy install -r requirements.yml

 - Passwords are encrypted making them into their own individual inline vaults. With this command:
 
       ansible-vault encrypt_string

 - Provision with:
 
       ./provision.sh <raspberry Pi IP address>
