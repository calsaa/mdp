import os, requests, time
from picamera2 import Picamera2
from . import bus

SERVER = os.getenv("SERVER_URL", "http://<PC_IP>:5000/image")

def run_camera_thread():
    cam = Picamera2()
    cam.configure(cam.create_still_configuration())
    cam.start()

    while True:
        if bus.trigger_camera.is_set():
            filename = "/tmp/capture.jpg"
            cam.capture_file(filename)
            with open(filename, "rb") as f:
                r = requests.post(SERVER, files={"file": f}, timeout=5)
            bus.to_android.put(r.json())  # forward result to Android
            bus.trigger_camera.clear()
        time.sleep(0.1)
