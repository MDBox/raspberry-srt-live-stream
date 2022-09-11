import depthai as dai

class CameraPipe:
    def __init__(self, pipe: str, max_kbps: int = 500, fps: int = 30):
        self._pipe = pipe
        self._max_kbps = max_kbps
        self._fps = fps

        pipeline = dai.Pipeline()

        camera = pipeline.create(dai.node.ColorCamera)
        camera.setBoardSocket(dai.CameraBoardSocket.RGB)
        camera.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

        camera_input_config = pipeline.create(dai.node.XLinkIn)
        camera_input_config.setStreamName('inputConfig')
        camera_input_config.out.link(camera.inputConfig)

        camera_input_control = pipeline.create(dai.node.XLinkIn)
        camera_input_control.setStreamName('inputControl')
        camera_input_control.out.link(camera.inputControl)


        video_encoder_h265 = pipeline.create(dai.node.VideoEncoder)
        video_encoder_h265.setDefaultProfilePreset(camera.getVideoSize(), camera.getFps(), dai.VideoEncoderProperties.Profile.H265_MAIN)
        video_encoder_h265.setBitrateKbps(self._max_kbps)

        camera_output = pipeline.create(dai.node.XLinkOut)
        camera_output.setStreamName('h265')

        camera.video.link(video_encoder_h265.input)
        video_encoder_h265.bitstream.link(camera_output.input)

        self.pipeline = pipeline


    def start(self):
        with dai.Device(self.pipeline) as device:
            video_queue = device.getOutputQueue(name='h265', maxSize=30, blocking=True)
            video_input_control_queue = device.getInputQueue(name='inputControl')

            input_control = dai.CameraControl()
            input_control.setSceneMode(dai.CameraControl.SceneMode.ACTION)
            video_input_control_queue.send(input_control)

            with open(self._pipe, 'wb') as output_pipe:
                print('Video Camera Started: Ctrl+c to stop')
                try:
                    while True:
                        h265_packet = video_queue.get()
                        output_pipe.write(h265_packet.getData().tobytes())
                except KeyboardInterrupt:
                    print("Video Camera Stopping...")