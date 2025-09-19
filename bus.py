import threading
import queue

# Event to trigger camera capture
trigger_camera = threading.Event()

# Queue for sending messages to Android
to_android = queue.Queue()

# Queue for sending commands to STM32
to_stm32 = queue.Queue()
