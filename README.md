# Raspberry Pi SRT Live Stream (With Oak Camera)
How to set up an affordable and portable live stream for IRL adventures.

## Recommended Equipment

- Oak Camera (any model will work)
  - https://shop.luxonis.com/collections/usb/products/oak-1-lite
  - https://shop.luxonis.com/collections/usb/products/oak-1
- Raspberry Pi 4/nano 
- Smartphone with tethering (Tested with an iPhone 11)
  - Hotspot with decent connection

### Why Oak Camera

This tiny camera packs a punch in compute power.
But the main reason for this project is the onboard h265 video encoder. 
Without the onboard encoder you would need to the Pi to encode the video 
stream in h264 which will drain battery and use a higher bitrate.

## Set up the Pi

The quickest way to get started is to download the prebuilt image from Luxonis.
This almost includes everything you need to run the stream. 
I will also provide steps to install everything using the base Raspberry Pi image.

If you want to skip the setup process I will provide a super custom image that is ready to go.

This image will be a sponsor only link. This is in order to recover costs to store and distribute the image.

Once you have the image you are free to send it to anyone or host it yourself. 

### Sponsor Access Image -> [Become a sponsor]()


This image is ready to go. Just flash it to an SDcard and plug it into your Pi.


- [Custom Raspberry Pi Image]()

Feel Free to redistribute a self-hosted copy of this image!

### Easy Way (Download prebuilt image)
- [Raspberry Pi Image for Oak Camera](https://docs.luxonis.com/projects/hardware/en/latest/pages/guides/raspberrypi.html)

### Use the base image
- [Raspberry Pi Image](https://www.raspberrypi.com/software/operating-systems/)

#### Python/DepthAI Install

```shell
sudo curl -fL https://docs.luxonis.com/install_dependencies.sh | bash
python -m pip install --upgrade pip
python -m pip install depthai
```

#### SRT (Secure Reliable Transport)
SRT will help keep your video stream smooth while traveling around.

```shell
# Build tools
sudo apt-get update
sudo apt-get install cmake libssl-dev git tclsh pkg-config build-essential

# Set up SRT
git clone https://github.com/Haivision/srt
cd srt
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

#### Audio/Bluetooth Speaker

If you wish you can enable bluetooth and turn the Pi into a portable audio receiver.
This is useful if you want to use the mic from your smartphone.

```shell
# For Audio and bluetooth mic proxy
sudo apt-get update
sudo apt-get install pulseaudio bluez bluemon

bluetoothctl
[bluetooth]# power on
[bluetooth]# agent on
# Connect with a bluetooth device and Pair
[bluetooth]# trust
```

#### GStreamer

We use gstreamer as a way to repackage the h265 stream from the camera and mux into mpegts.
Doing this makes it possible to transport over UDP or SRT. There maybe other python libraries that can do the same thing but gstreamer is awesome.

```shell
sudo apt-get update
sudo apt-get install gstreamer1.0-tools \
                     gstreamer1.0-plugins-* \
                     gstreamer1.0-pulseaudio \
                     gstreamer1.0-alsa \
                     gstreamer1.0-rtsp \
                     gstreamer1.0-libav
```
