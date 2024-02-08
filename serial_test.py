import serial
import time

def serial_connect(port, operator, threshold):
	baudrate = 921600
	#port for 1st pico is "/dev/ttyACM0"
	ser = serial.Serial(port, baudrate, timeout = 1)

	analog_value=0

	while True:
		if ser.in_waiting:
			analog_str = ser.readline().decode('utf-8').strip()
			analog_value = int(analog_str)
			volt_value = (3.3/65535)*analog_value
			print("Analog Value: ", analog_value, " Voltage Value: ", volt_value)
			if operator == 'higher':
				if analog_value >= threshold:
					print('Done!')
					break
			elif operator == 'lower':
				if analog_value <= threshold:
					print('Done!')
					break
			else:
				print('Invalid operator.')
				break

#port = "/dev/ttyACM0"
#serial_connect(port, 'higher', 50000)
