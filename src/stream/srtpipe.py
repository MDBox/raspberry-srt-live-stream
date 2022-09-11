import subprocess
import shlex
import sys

class SRTProcess:
    def __init__(self, remote_server: str, passphrase: str = None, local_port: int = 5000):
        self._command = shlex.split(f'srt-live-transmit -q -buffering 10000 udp://:{local_port} {remote_server}?passphrase={passphrase}&mode=caller')

    def start(self):
        srt_output = subprocess.Popen(self._command, stdout=subprocess.PIPE)
        for out in iter(lambda: srt_output.stdout.read(1), b""):
            sys.stdout.buffer.write(out)
