# RPi Imageviewer

This project is an attempt to turn an old screen and a Raspberry Pi into a stand-alone image viewer. The functionality works like this: The RPi is plugged into the screen's USB hub, so it powers up when the screen is plugged in. Whenever a USB stick is plugged in, its contents are automatically displayed. The only interaction works via two buttons that allow you to step through the available images. The viewer uses only the framebuffer, so the system is fairly minimal.


## Prerequisites

* An old screen, a Raspberry Pi, one or two buttons, a soldering iron
* The following project and the capability to build it:
   * https://github.com/ferk/udev-media-automount
* python3
* I've tested this with a Raspberry Pi 1B running the official Trixie Lite image.


You'll need :

1. A USB automounter.

That's what  [```udev-media-automount```](https://github.com/ferk/udev-media-automount) does. Build & install this package, and all USB media will automatically appear in ```/media```.
   
2. A way to run the python project immediately on start-up. We'll override ```getty@tty1.service``` to achieve that.

3. A nifty little program that does the actual work. You've found it.


## Setting up the system

Starting with the fresh Trixie image, you should update the system and uninstall a few things we will not need:
```
sudo apt update
sudo apt full-upgrade
sudo apt remove --purge avahi-daemon bluez cloud-init modemmanager triggerhappy wolfram-engine 
sudo apt autoremove --purge
```

To speed up boot, there's a few services, you can safely get rid of:
```
sudo systemctl disable apt-daily-upgrade.timer
sudo systemctl disable apt-daily.timer
sudo systemctl disable cron.service
```

You can also edit ```/boot/firmware/config.txt```, comment out camera and sound and add ```dtoverlay=disable-bt``` to turn off bluetooth.


## Installing the python application

```
sudo apt install git python3-numpy python3-pil python3-setuptools
git clone https://github.com/joergneulist/rpi_imageviewer.git
```

Adapt ```etc/imvi.json``` to the GPIOs you will be using for the buttons.


### Building

```make install ``` will create an environment ```/opt/imvi``` and install the imvi package there. To launch it manually, execute ```/opt/imvi/bin/python3 -m imvi```.

```make kiosk``` will override ```getty@tty1.service``` to launch the viewer on boot.

And you're done.


## Finishing touches

If you don't need the network, you can turn the services off. Be sure to inspect ```etc/network-services``` before running:
```
bin/net-off
```

***TODO***
Make the system read-only.
