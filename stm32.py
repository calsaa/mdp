import os, serial, time
import bus

UART = os.getenv("UART_PORT", "/dev/ttyACM0")
BAUD = int(os.getenv("UART_BAUD", "115200"))

def run_stm32_thread():
    ser = serial.Serial(UART, BAUD, timeout=0.1)
    first_command = True
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line or first_command:
                if line:
                    print(f"[STM32] {line}")
                if "OBJECT" in line:
                    bus.snap_obstacle_id.put(1)
                    bus.trigger_camera.set()
                if bus.task_1_started.is_set():
                    if "FIN" in line or first_command:
                        if not bus.to_stm32.empty():
                            if first_command:
                                first_command = False
                            cmd = bus.to_stm32.get()
                            cmd = cmd.strip()
                            print(f"command from stm32 bus {cmd}")
                            if "SNAP" not in cmd:
                                #if "FIN" not in cmd:
                                print(f"sending {cmd} to stm32")
                                ser.write((cmd + "\n").encode())
                                android_cmd = bus.to_stm32.get()
                                print(f"sending {android_cmd} to android")
                                bus.to_android.put(android_cmd)
                                ack_received = False
                                #time.sleep(2)
                            else:
                                print("sending snap to bus")
                                bus.snap_obstacle_id.put(cmd[4])
                                bus.trigger_camera.set()
                                first_command = True
                                time.sleep(3)
                else:
                    continue
        #if not bus.to_stm32.empty():
        #    cmd = bus.to_stm32.get()
        #    ser.write((cmd + "\n").encode())

        time.sleep(0.01)

