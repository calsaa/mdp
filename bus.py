import queue, threading

# Events
trigger_camera = threading.Event()

# Queues
to_stm32 = queue.Queue()
to_android = queue.Queue()
