import os, serial, time
from . import bus

UART = os.getenv("UART_PORT", "/dev/ttyUSB0")
BAUD = int(os.getenv("UART_BAUD", "115200"))

def run_stm32_thread():
    ser = serial.Serial(UART, BAUD, timeout=0.1)
    
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            print(f"[STM32] {line}")
            if "OBJECT" in line:  # Trigger camera only on object detection
                bus.trigger_camera.set()

        if not bus.to_stm32.empty():
            cmd = bus.to_stm32.get()
            ser.write((cmd + "\n").encode())

        time.sleep(0.01)

