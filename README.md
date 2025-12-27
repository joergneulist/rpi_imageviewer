# RPi Imageviewer

This project is an attempt to turn an old screen and a Raspberry Pi into a stand-alone image viewer. The functionality works like this: The RPi (1B, in my case) is plugged into the screen's USB hub, so it powers up when the screen is plugged in. The only interaction works via two buttons. Whenever a USB stick is plugged in, its contents are automatically displayed. The viewer uses only the framebuffer, so it uses a fairly minimal system.


## Prerequisites

* An old screen, a Raspberry Pi, one or two buttons, a soldering iron
* The following projects and the capability to build them:
   * https://github.com/godspeed1989/fbv
   * ...
 
* poppler-utils
* python3
* ...and the python libraries linked in the repo


## Setup

You'll need :

1. A USB automounter

That's what  ... does. Build & install.
   
2. A way to run the python project immediately on start-up

**TODO**
 
3. Tooling to enable the python tool to actually display stuff on the framebuffer

* [```fbv```](https://github.com/godspeed1989/fbv): Build and install (It's not very actively maintained, so a glance at the PRs might save you from having to fix stuff yourself).
```sudo apt install poppler-utils```: The project uses pdftoppm to make PDF documents visible as well. If you don't use that, you don't need this library.


## The Project

### Configuration

The config file determines the behaviour.
**TODO** definition

### Scripting

A short script takes the PDF handling away from the Python code.
**TODO**

### Python Code

**TODO** poetry or requirements? How to install?

