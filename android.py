import json
import os, bluetooth, threading, time
import bus
import math
import socket
UUID = os.getenv("BT_UUID", "00001101-0000-1000-8000-00805F9B34FB")
obstacle_messages = []
robotstart = ""

def receive_thread(client_sock):
    try:
        while True:
            # receive from Android
            data = client_sock.recv(1024)
            if not data:
                break
            msg = data.decode("utf-8").strip()
            print(f"[Android -> RPi] {msg}")

            if msg == "OBJECT":
                bus.trigger_camera.set()
            elif "CONFIRMATION" in msg:
                if "OBSTACLE" in msg:
                   sections = msg.split("\n")
                   for section in sections:
                      if section == "FINISHED":
                         bus.to_algo.put(section)
                         continue
                      parts = section.split(",")
                      d = 1
                      if parts[4] == 'S':
                         d = 2
                      elif parts[4] == 'E':
                         d = 3
                      elif parts[4] == 'W':
                         d = 4
                      obstacle = {"id": int(parts[1]), "x":int(parts[2]),"y":int(parts[3]),"d":d}
                      obstacle_messages.append(obstacle)
                      print("Added",msg,"to Obstacle List")
                elif "ROBOT" in msg:
                   parts = msg.split(",")
                   radian_direction = 1.57
                   if parts[3] == 'E':
                        radian_direction = 0
                   elif parts[3] == 'S':
                        radian_direction = -1.57
                   elif parts[3] == 'W':
                        radian_direction  = 3.14
                   robot = {"x":int(parts[1]), "y":int(parts[2]), "theta":radian_direction}
                   robotstart = robot
                elif "FINISHED" in msg:
                   bus.to_algo.put(msg)
                if obstacle_messages:
                   bus.to_algo.put(obstacle_messages)
                #print("Android->Algo",bus.to_algo.get())
                #print("Android->Algo",robotstart)
                if robotstart:
                   bus.to_algo.put(robotstart)
            elif "FINISHED" in msg:
                bus.to_algo.put(msg)
            elif msg == "TASK 1 START":
                bus.task_1_started.set()
                print("Task 1 started!")
            else:
                bus.to_stm32.put(msg)  # forward commands to STM32
#               bus.to_algo.put(msg)
                print("[Android->STM]", msg)

    except OSError:
        pass

def run_android_thread():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    bluetooth.advertise_service(
        server_sock,
        "RpiAndroidService",
        service_id=UUID,
        service_classes=[UUID, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print(f"[Android] Waiting for connection on RFCOMM channel {port}...")

    client_sock, client_info = server_sock.accept()
    print(f"[Android] Connected from {client_info}")
    
    recv_thread = threading.Thread(target=receive_thread, args=(client_sock,))
    recv_thread.daemon = True
    recv_thread.start()
    #first_run = True
#    client_sock.setblocking(False)

    try:
        while True:
            if not bus.to_android.empty():
                print("android bus not empty")
                reply = bus.to_android.get()
                client_sock.send(str(reply).encode("utf-8"))
                
            if not recv_thread.is_alive():
                break
            
            time.sleep(0.1)
    except OSError:
        pass
    

    print("[Android] Disconnected")
    client_sock.close()
    server_sock.close()
