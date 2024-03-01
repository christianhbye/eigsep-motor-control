import serial
import time

def bit2volt(analog_value, vmax=3.3, nbits=16):
    ratio = vmax / (2**nbits - 1)
    return ratio * analog_value


def serial_connect(port, operator, threshold):
    baudrate = 115200 # 921600
    ser = serial.Serial(port, baudrate)

    ser.dtr = False
    time.sleep(0.5)
    ser.dtr = True

    while True:
        if ser.in_waiting:
            analog_str = ser.readline().decode('utf-8').strip()
            a, b = analog_str.split()
            a = int(a)
            b = int(b)
            analog_values = np.array([a, b])
            volt_values = bit2volt(analog_values)
            print("Analog Value: ", analog_values, " Voltage Value: ", volt_values)
            # XXX
            # if operator == 'higher':
            #     if analog_value >= threshold:
            #         print('Done!')
            #         break
            # elif operator == 'lower':
            #     if analog_value <= threshold:
            #         print('Done!')
            #         break
            # else:
            #     print('Invalid operator.')
            #     break

if __name__ == "__main__":
    port = "/dev/ttyACM0"
    serial_connect(port, 'higher', 50000)
