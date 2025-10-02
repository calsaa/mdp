from picamera import PiCamera
import time

camera = PiCamera()
camera.start_preview()
time.sleep(2)
tmp_file_path = "/tmp/capture.jpg"
camera.capture(tmp_file_path)
camera.stop_preview()
