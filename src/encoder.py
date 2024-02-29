import serial
import time
from qwiic_dual_encoder_reader import QwiicDualEncoderReader


class Encoder(QwiicDualEncoderReader):

    def get_encoder(self, motor_id):
        if motor_id == 0:
            return self.encoder.count1
        elif motor_id == 1:
            return self.encoder.count2
        else:
            raise KeyError("Invalid motor id.")

    def serial_read(self):
        baudrate = 115200
        # port for 1st pico is "/dev/ttyACM0"
        port = "/dev/ttyACM0"
        ser = serial.Serial(port, baudrate)

        ser.dtr = False
        time.sleep(0.5)
        ser.dtr = True


        while True:
            if ser.in_waiting:
                analog_string = ser.readline().decode("utf-8").strip()
                print(analog_string)
                a, b = analog_string.split()
                analog_value_0 = int(a)
                analog_value_1 = int(b)
                volt_value_0 = (3.3 / 65535) * analog_value_0
                volt_value_1 = (3.3 / 65535) * analog_value_1
                print(
                    "Analog Value 0: ",
                    analog_value_0,
                    " Voltage Value 0: ",
                    volt_value_0,
                    "  Analog Value 1: ",
                    analog_value_1,
                    " Voltage Value 1: ",
                    volt_value_1,
                )
        # port = "/dev/ttyACM0"
        # serial_connect(port, 'higher', 50000)
