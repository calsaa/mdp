import threading
import queue

# Event to signal start of Task 1
task_1_started = threading.Event()

# Event to trigger camera capture
trigger_camera = threading.Event()

# Queue for sending messages to Android
to_android = queue.Queue()

# Queue for sending commands to STM32
to_stm32 = queue.Queue()

# Queue for sending commands to Algo
to_algo = queue.Queue()

snap_obstacle_id = queue.Queue()
