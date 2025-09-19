import os, requests, time
from picamera2 import Picamera2
from . import bus

SERVER = os.getenv("SERVER_URL", "http://<PC_IP>:5000/image")

def run_camera_thread():
    cam = Picamera2()
    cam.configure(cam.create_still_configuration())
    cam.start()

    while True:
        # Wait for STM32 to signal an object detection
        if bus.trigger_camera.is_set():
            filename = "/tmp/capture.jpg"
            cam.capture_file(filename)
            
            # Send the image to the server
            with open(filename, "rb") as f:
                try:
                    r = requests.post(SERVER, files={"file": f}, timeout=5)
                    bus.to_android.put(r.json())  # Forward server result to Android
                except requests.RequestException as e:
                    print(f"[Camera] Error sending image: {e}")
            
            bus.trigger_camera.clear()  # Reset event for next detection

        time.sleep(0.05)  # avoid busy loop
