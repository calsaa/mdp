import os, serial, time
import bus

UART = os.getenv("UART_PORT", "/dev/ttyACM0")
BAUD = int(os.getenv("UART_BAUD", "115200"))

def run_stm32_thread():
    ser = serial.Serial(UART, BAUD, timeout=0.1)
    first_command = True
    waiting_for_ack = False
    last_send_command = None
    last_sent_time = None
    ACK_TIMEOUT = 5 

    while True:
        line = ser.readline().decode(errors="ignore").strip()
        
        if line == "ACK" and waiting_for_ack:
            print("ACK received from STM32")
            waiting_for_ack = False
            last_send_command = None
            last_sent_time = None
        
        if waiting_for_ack and last_sent_time and (time.time() - last_sent_time) > ACK_TIMEOUT:
            print(f"ACK timeout for command: {last_send_command}. Resending...")
            ser.write((last_send_command + "\n").encode())
            last_sent_time = time.time()

        if line or first_command:
            if line:
                print(f"[STM32] {line}")
            if "OBJECT" in line:
                bus.snap_obstacle_id.put(1)
                bus.trigger_camera.set()

            # only proceed if task1 has been pressed
            if bus.task_1_started.is_set():
                # send the next command to STM32 if its the first command or if FIN is received
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

                            # set up ACK waiting
                            waiting_for_ack = True
                            last_send_command = cmd
                            last_sent_time = time.time()

                            # send to android
                            android_cmd = bus.to_stm32.get()
                            print(f"sending {android_cmd} to android")
                            bus.to_android.put(android_cmd)
                        else:
                            # communicate to camera_client for CV
                            print("sending snap to bus")
                            bus.snap_obstacle_id.put(cmd[4])
                            bus.trigger_camera.set()
                            first_command = True
                            while bus.trigger_camera.is_set():
                                time.sleep(0.05)
                else:
                    continue
#        if not bus.to_stm32.empty():
#            cmd = bus.to_stm32.get()
#            ser.write((cmd + "\n").encode())
        time.sleep(0.01)

