import serial
import time

port = "/dev/ttyACM0"
baudrate = 460800
ser = serial.Serial(port, baudrate, timeout = 1)

analog_value=0

while True:
	if ser.in_waiting:
		analog_value = ser.readline().decode('utf-8').strip()
		print(f"Analog Value: {analog_value}")
	if int(analog_value)>50000:
		print('Done!')
		break
