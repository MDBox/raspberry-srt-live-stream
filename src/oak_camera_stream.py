#!/usr/bin/env python3

import typer
import threading
import tempfile
import os
import sys
import time
from camerapipe import CameraPipe
from stream import GSTProcess, SRTProcess

app = typer.Typer()

@app.command()
def stream(
        remote_server: str = typer.Argument('srt://127.0.0.1:40000', envvar='STREAM_REMOTE_SERVER', help='enter srt host: srt://domain:port'),
        kbps: int = typer.Option(
            500, envvar='STREAM_KBPS',
            help='enter the kbps video encoder target'
        ),
        fps: int = typer.Option(
            30, envvar='STREAM_FPS',
            help='enter the target frames per second'
        ),
        local_port: str = typer.Option(
            5000, envvar="STREAM_LOCAL_PORT",
            help='enter the local port for passing UDP video frames'
        ),
        passphrase: str = typer.Option(
            None, prompt=True,
            confirmation_prompt=False,
            hide_input=True,
            envvar='STREAM_PASSPHRASE',
            prompt_required=False,
            help='enter the passphrase for the remote SRT server'
        )
):
    typer.echo('starting...')
    typer.echo(f'Setting remote stream server: {remote_server}')
    typer.echo(f'Setting target kbps: {kbps}')
    typer.echo(f'Setting fps: {fps}')
    typer.echo(f'Setting local listener UDP port: {local_port}')

    with tempfile.TemporaryDirectory() as tempdir:
        pipe_name = f'{tempdir}/video.pipe'
        os.mkfifo(pipe_name)

        camera_pipe = CameraPipe(pipe_name, max_kbps=kbps, fps=fps)
        gst_pipe = GSTProcess(pipe_name, local_port=local_port)
        srt_pipe = SRTProcess(remote_server=remote_server, passphrase=passphrase, local_port=local_port)

        thread_camera = threading.Thread(target=camera_pipe.start)
        thread_camera.daemon = False
        thread_camera.start()
        print('started camera thread')

        thread_gst = threading.Thread(target=gst_pipe.start)
        thread_gst.daemon = False
        thread_gst.start()
        print('started gst thread')

        thread_srt = threading.Thread(target=srt_pipe.start)
        thread_srt.daemon = False
        thread_srt.start()
        print('started srt thread')

        while True:
            time.sleep(30)
            if not thread_camera.is_alive():
                print('The camera thread crashed')
                sys.exit(1)
            if not thread_gst.is_alive():
                print('The gst thread crashed')
                sys.exit(1)
            if not thread_srt.is_alive():
                print('The srt thread stopped')
                sys.exit(1)


if __name__ == '__main__':
    app()
