#!/usr/bin/env python3

import depthai as dai
import threading
import subprocess
import shlex
import sys

GST_COMMAND = shlex.split("gst-launch-1.0 filesrc location=/home/pi/video.out do-timestamp=true ! queue !  h265parse ! mpegtsmux name=mux ! queue ! udpsink host=127.0.0.1 port=5000 sync=false async=false alsasrc ! audioconvert ! audio/x-raw,channels=2,depth=16,width=16,rate=44100 ! voaacenc ! aacparse ! queue ! mux.")


def start_gst():
    gst_output=subprocess.Popen(GST_COMMAND, stdout=subprocess.PIPE)
    for c in iter(lambda: gst_output.stdout.read(1), b""):
        sys.stdout.buffer.write(c)

def start_camera():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    videoEnc = pipeline.create(dai.node.VideoEncoder)
    xout = pipeline.create(dai.node.XLinkOut)

    xout.setStreamName('h265')

    # Properties
    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    videoEnc.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)
    videoEnc.setBitrateKbps(500)
    videoEnc.setNumBFrames(1)

    # Linking
    camRgb.video.link(videoEnc.input)
    videoEnc.bitstream.link(xout.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        # Output queue will be used to get the encoded data from the output defined above
        q = device.getOutputQueue(name="h265", maxSize=30, blocking=True)

        # The .h265 file is a raw stream file (not playable yet)
        with open('video.out', 'wb') as videoFile:
            print("Press Ctrl+C to stop encoding...")
            try:
                while True:
                    h265Packet = q.get()  # Blocking call, will wait until a new data has arrived
                    videoFile.write(h265Packet.getData().tobytes())
            except KeyboardInterrupt:
                # Keyboard interrupt (Ctrl + C) detected
                pass

def main():
    thread = threading.Thread(target=start_gst)
    thread.daemon = False
    thread.start()

    start_camera()
    thread.join()


if __name__ == '__main__':
    print('Starting Camera Stream')
    main()
