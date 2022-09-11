import subprocess
import shlex
import sys

class GSTProcess:
    def __init__(self, pipe: str, local_port: int = 5000):
        self._pipe = pipe
        self._gst_command = shlex.split(f"gst-launch-1.0 filesrc location={self._pipe} do-timestamp=true ! queue !  h265parse ! mpegtsmux name=mux ! queue ! udpsink host=127.0.0.1 port={local_port} sync=false async=false alsasrc ! audioconvert ! audio/x-raw,channels=2,depth=16,width=16,rate=44100 ! voaacenc ! aacparse ! queue ! mux.")

    def start(self):
        gst_output = subprocess.Popen(self._gst_command, stdout=subprocess.PIPE)
        for out in iter(lambda: gst_output.stdout.read(1), b""):
            sys.stdout.buffer.write(out)