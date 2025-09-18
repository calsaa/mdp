import os, bluetooth
from . import bus

UUID = os.getenv("BT_UUID", "94f39d29-7d6d-437d-973b-fba39e49d4ee")

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

    try:
        while True:
            # receive from Android
            data = client_sock.recv(1024)
            if not data:
                break
            msg = data.decode("utf-8").strip()
            print(f"[Android -> RPi] {msg}")

            if msg == "CAPTURE":
                bus.trigger_camera.set()
            else:
                bus.to_stm32.put(msg)  # forward commands to STM32

            # send queued messages back to Android
            if not bus.to_android.empty():
                reply = bus.to_android.get()
                client_sock.send(str(reply).encode("utf-8"))

    except OSError:
        pass

    print("[Android] Disconnected")
    client_sock.close()
    server_sock.close()
