import threading
import time
from camera_client import run_camera_thread
from stm32 import run_stm32_thread
from android import run_android_thread
from bus import to_stm32
from algo import run_algo_thread

def main():
    threads = [
	threading.Thread(target=run_algo_thread, daemon=True),
        threading.Thread(target=run_stm32_thread, daemon=True),
        threading.Thread(target=run_android_thread, daemon=True),
        threading.Thread(target=run_camera_thread, daemon=True),
    ]

    # Start all threads
    for t in threads:
        t.start()
    time.sleep(3)
#    to_stm32.put("A")
    #time.sleep(0.5)
    #to_stm32.put("S")
#    print("Send F to STM")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Exiting program.")

if __name__ == "__main__":
    main()
