# RPi Imageviewer

This project is an attempt to turn an old screen and a Raspberry Pi into a stand-alone image viewer. The functionality works like this: The RPi is plugged into the screen's USB hub, so it powers up when the screen is plugged in. Whenever a USB stick is plugged in, its contents are automatically displayed. The only interaction works via two buttons that allow you to step through the available images. The viewer uses only the framebuffer, so the system is fairly minimal.

## Prerequisites

* An old screen, a Raspberry Pi, one or two buttons, a soldering iron
* Only a moderate fear of using buildroot

The code is very much self-contained. It will handle udev-events and automount USB-Sticks, draw images to framebuffer, and handle GPIO for the user interaction.
On the main branch, you'll see this running on the official Trixie Raspbian, but here, we're digging deeper.

## Setting up the system

Get [buildroot](https://buildroot.org/) and configure a few things:

1. ```make raspberrypi_defconfig``` or whatever matches your hardware (I'm using an RPi 1B) to set up the system defaults.
2. ```make menuconfig``` and change the following things:
   a. System configuration
      * Set hostname, banner, and root password according to taste
      * Set root filesystem overlay directories to ```_overlay```
   b. Kernel
      * Linux kernel tools, activate GPIO
   c. Target packages
      * Hardware handling, activate pigpio and raspi-gpio
      * Interpreter languages and scripting, activate python3
      * Libraries / Graphics, activate jpeg support and libpng
      * Python3 external packages, activate python-gpiozero, python-pillow, and python-pyudev
3. Create the subfolder ```_overlay``` and copy this project there (you only need ```imvi.json``` and the ```.py``` sources, to be exact)
4. **TODO** Changes to make imvi start automatically
5. Run ```make``` and take a long walk.
6. Flash ```output/sdcard.img``` and boot your RPi from it. Done.
