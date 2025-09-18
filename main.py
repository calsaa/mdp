import threading, time
from .camera_client import run_camera_thread
from .stm32 import run_stm32_thread
from .android import run_android_thread

def main():
    threads = [
        threading.Thread(target=run_stm32_thread, daemon=True),
        threading.Thread(target=run_android_thread, daemon=True),
        threading.Thread(target=run_camera_thread, daemon=True),
    ]
    [t.start() for t in threads]

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
