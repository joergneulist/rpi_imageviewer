# RPi Imageviewer

This project is an attempt to turn an old screen and a Raspberry Pi into a stand-alone image viewer. The functionality works like this: The RPi (1B, in my case) is plugged into the screen's USB hub, so it powers up when the screen is plugged in. The only interaction works via two buttons. Whenever a USB stick is plugged in, its contents are automatically displayed. The viewer uses only the framebuffer, so it uses a fairly minimal system.


## Prerequisites

* An old screen, a Raspberry Pi, one or two buttons, a soldering iron
* The following projects and the capability to build them:
   * https://github.com/godspeed1989/fbv
   * https://github.com/ferk/udev-media-automount
* python3


## Setup

You'll need :

1. A USB automounter

That's what  [```udev```](https://github.com/ferk/udev-media-automount) does. Build & install this package, and all USB media will automatically appear in ```/media```.
   
2. Tooling to enable the python tool to actually display stuff on the framebuffer

* [```fbv```](https://github.com/godspeed1989/fbv): Build and install (It's not very actively maintained, so a glance at the PRs might save you from having to fix stuff yourself).
* ```sudo apt install poppler-utils```: The project can use pdftoppm to make PDF documents visible as well. If you don't use that, you don't need this library.

3. A way to run the python project immediately on start-up

*** TODO ***


## The Project

### Configuration

The config file is a json file that determines the behaviour.

In the "pins" key, you need to define the GPIOs connected to the two buttons "mode" and "step". In the "types" key, you'll define the commands to be run to display an image, substituting ```#``` for the file name. A full example:

```
{
	"pins": {
		"mode": 2,
		"step": 3
	},

	"types": {
		".jpg":  { "view": ["/usr/local/bin/fbv", "-ey", "#"]},
		".jpeg": { "view": ["/usr/local/bin/fbv", "-ey", "#"]},
		".png":  { "view": ["/usr/local/bin/fbv", "-ey", "#"]},
	}
}
```


### Python Code

```make install ``` will create an environment ```~/imvi``` and install the imvi package there. To launch it manually, execute ```~/imvi/bin/python3 -m imvi```.

```make kiosk``` will override ```getty@tty1.service``` to launch the viewer on boot.


### Optimisations

To simplify the system, you can disable some boot services and make the system read-only. I will document this later.
