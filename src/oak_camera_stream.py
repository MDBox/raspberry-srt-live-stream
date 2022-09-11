#!/usr/bin/env python3

import threading
import tempfile
import os
import sys
import time
from camerapipe import CameraPipe
from steam import GSTProcess, SRTProcess

def main():
    with tempfile.TemporaryDirectory() as tempdir:
        pipe_name = f'{tempdir}/video.pipe'
        os.mkfifo(pipe_name)

        camera_pipe = CameraPipe(pipe_name)
        gst_pipe = GSTProcess(pipe_name)
        #srt_pipe = SRTProcess()

        thread_camera = threading.Thread(target=camera_pipe.start())
        thread_camera.daemon = False
        thread_camera.start()

        thread_gst = threading.Thread(target=gst_pipe.start())
        thread_gst.daemon = False
        thread_gst.start()

        # thread_srt = threading.Thread(target=srt_pipe.start())
        # thread_srt.daemon = False
        # thread_srt.start()

        while True:
            time.sleep(30)
            if not thread_camera.isAlive():
                print('The camera thread crashed')
                sys.exit(1)
            if not thread_gst.isAlive():
                print('The gst thread crashed')
                sys.exit(1)
            # if not thread_srt.isAlive():
            #     print('The srt thread stopped')
            #     sys.exit(1)

if __name__ == '__main__':
    print('Starting Camera Stream')
    main()
