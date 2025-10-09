
import os
import requests
#import time
import json
#from picamera import PiCamera
#from picamera.array import PiRGBArray
import bus

SERVER = os.getenv("SERVER_URL", "http://192.168.40.11:8000/algo/live")

def run_algo_thread():
	print("[Algo] Algo thread started")
	finish = False
	test = {"cat":"obstacles","value":{"obstacles":[],"mode":0, "initial_position":{"x":0,"y":0,"theta":1.57}}}
	try:
		while True:
			data=bus.to_algo.get()
			#if not bus.to_algo.empty():
				#print("test")
				#obstacle = bus.to_algo.get()
			print(data)
			#print(type(data))
			if isinstance(data, dict):
				print("test robot start")
				test["value"]["initial_position"]=data
			if isinstance(data, list):
				print("test obstacle")
				test["value"]["obstacles"] = data
			if "FINISH" in data:
				finish = True
			print("Algo receives:",test)
			if test["value"]["initial_position"] and test["value"]["obstacles"] and finish:
				finish = False
				try:
					r = requests.post(SERVER,json=test,timeout=120)
					print(r.text)
					try:
						msg=r.json()
						#msg = r
					except:
						msg=json.loads(r.text)
				except requests.RequestException as e:
					print("[Algo] Error sending message: {}".format(e))
				if msg:
					for items in msg["commands"]:
						bus.to_stm32.put(items["value"])
						print("algo " + items["value"])
						if "FIN" in items["value"]:
							msg_to_send_finish = "STATUS, FINISH"
							bus.to_stm32.put(msg_to_send_finish)
						elif "SNAP" not in items["value"]:
							direction = items["end_position"]["d"]
							prefix = items["value"].split(",")[0]
							#if items["end_position"]["d"]==1:
								#direction = "N"
							#elif items["end_position"]["d"]==2:
								#direction = "S"
							#elif items["end_position"]["d"]==3:
								#direction = "E"
							#elif items["end_position"]["d"]==4:
								#direction = "W"
							msg_to_send = prefix + "." + "ROBOT, "+str(items["end_position"]["x"])+", "+str(items["end_position"]["y"])+", " + direction+"\n"
							bus.to_stm32.put(msg_to_send)
#						elif "FIN" in items["value"]:
#							msg_to_send_finish = "STATUS, FINISH"
#							bus.to_stm32.put(msg_to_send_finish) 
				#msg = msg["commands"][0]["value"]
				#bus.to_stm32.put(msg)
				#print("Sending", msg, "to STM")

	except KeyboardInterrupt:
        	print("\n[Algo] Exiting thread.")
