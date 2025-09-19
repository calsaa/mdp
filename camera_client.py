import os
import requests
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import bus

SERVER = os.getenv("SERVER_URL", "http://127.0.0.1:5000/docs")

def run_camera_thread():
    cam = PiCamera()
    cam.resolution = (640, 480)
    raw_capture = PiRGBArray(cam, size=(640, 480))
    time.sleep(0.1)  # Allow camera to warm up

    print("[Camera] Camera thread started.")

    try:
        while True:
            # Wait for STM32 to signal an object detection
            if bus.trigger_camera.is_set():
                filename = "/tmp/capture.jpg"
                cam.capture(filename)  # Capture image to file

                # Send the image to the server
                with open(filename, "rb") as f:
                    try:
                        r = requests.post(SERVER, files={"file": f}, timeout=5)
                        bus.to_android.put(r.json())  # Forward server result to Android
                    except requests.RequestException as e:
                        print("[Camera] Error sending image: {}".format(e))

                bus.trigger_camera.clear()  # Reset event for next detection

            time.sleep(0.05)  # avoid busy loop

    except KeyboardInterrupt:
        print("\n[Camera] Exiting camera thread.")
    finally:
        cam.close()
