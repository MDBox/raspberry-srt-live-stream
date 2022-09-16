import depthai as dai

class CameraPipe:
    def __init__(self, pipe: str, max_kbps: int = 500, fps: int = 30, flip: bool = True):
        self._pipe = pipe
        self._max_kbps = max_kbps
        self._fps = fps
        self._is_active = True
        self._flip = flip

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
        video_encoder_h265.setDefaultProfilePreset(camera.getFps(), dai.VideoEncoderProperties.Profile.H265_MAIN)
        video_encoder_h265.setBitrateKbps(self._max_kbps)

        video_encoder_h264 = pipeline.create(dai.node.VideoEncoder)
        video_encoder_h264.setDefaultProfilePreset(camera.getFps(), dai.VideoEncoderProperties.Profile.H264_MAIN)

        camera_output = pipeline.create(dai.node.XLinkOut)
        camera_output_264 = pipeline.create(dai.node.XLinkOut)
        camera_output.setStreamName('h265')
        camera_output_264.setStreamName('h264')

        camera.video.link(video_encoder_h265.input)
        camera.video.link(video_encoder_h264.input)
        video_encoder_h265.bitstream.link(camera_output.input)
        video_encoder_h264.bitstream.link(camera_output_264.input)

        self.pipeline = pipeline


    def start(self):
        print('camera thread active')
        with dai.Device(self.pipeline) as device:
            video_queue = device.getOutputQueue(name='h265', maxSize=30, blocking=True)
            video_queue_264 = device.getOutputQueue(name='h264', maxSize=30, blocking=True)
            video_input_control_queue = device.getInputQueue(name='inputControl')
            video_input_config_queue = device.getInputQueue(name='inputConfig')

            input_control = dai.CameraControl()
            input_control.setSceneMode(dai.CameraControl.SceneMode.ACTION)
            video_input_control_queue.send(input_control)

            input_config = dai.ImageManipConfig()
            input_config.setHorizontalFlip(self._flip)
            video_input_config_queue.send(input_config)


            with open(self._pipe, 'wb') as output_pipe, open('video.h264', 'wb') as out_file:
                print('Video Camera Started: Ctrl+c to stop')
                while self._is_active:
                    h265_packet = video_queue.get()
                    output_pipe.write(h265_packet.getData().tobytes())
                    h264_packet = video_queue_264.get()
                    h264_packet.getData().tofile(out_file)

    def stop(self):
        self._is_active = False
