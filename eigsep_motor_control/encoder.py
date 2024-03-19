import logging
import numpy as np
import serial
from qwiic_dual_encoder_reader import QwiicDualEncoderReader
from eigsep_motor_control.motor import MOTOR_ID
from eigsep_motor_control.serial_params import BAUDRATE, INT_LEN


class Encoder(QwiicDualEncoderReader):

    def get_encoder(self, motor):
        """
        Read the encoder count of a motor.

        Parameters
        ----------
        motor : str
            Either ``az'' or ``alt''. The motor to read the encoder value of.
        """
        mid = MOTOR_ID[motor]
        if mid == 0:
            return self.encoder.count1
        elif mid == 1:
            return self.encoder.count2


class Potentiometer:

    NBITS = 16  # ADC number of bits
    PORT = "/dev/ttyACM0"  # serial connection constants

    def __init__(self):
        while True:
            try:
                self.ser = serial.Serial(port=self.PORT, baudrate=BAUDRATE)
                self.ser.reset_input_buffer()
                break
            except serial.SerialException as e:
                logging.error(f"Failed to open serial port {self.PORT}: {e}. Trying again.")
                # Additional error handling or recovery actions can be placed here
                continue #try again

        self.VOLT_RANGE = {"az": (0.7, 1.7), "alt": (0.7, 1.7)}

    def bit2volt(self, analog_value, motor):
        vmax = self.VOLT_RANGE[motor][1]
        res = 2**self.NBITS - 1
        ratio = vmax / res
        return ratio * analog_value

    def read_analog(self):
        while True:
            try:
                data = self.ser.readline().decode("utf-8").strip()
                data = [int(d) for d in data.split()]
                return np.array(data) / INT_LEN
            except (serial.SerialException, ValueError) as e:
                logging.error(f"Error reading analog data: {e}")
                continue #try again

        
    def read_volts(self, motor=None):
        while True:
            try:
                analog = self.read_analog()
                if motor == "az":
                    return self.bit2volt(analog[0], "az")
                elif motor == "alt":
                    return self.bit2volt(analog[1], "alt")
                else:
                    return [self.bit2volt(val, m) for val, m in zip(analog, ["az", "alt"])]
            except Exception as e:
                logging.error(f"Error converting analog to voltage for {motor}: {e}. Trying again.")
                continue  # try again
    
    def monitor(self, az_event, alt_event):
        names = ("az", "alt")
        events = (az_event, alt_event)
        vprev = None
        while True:
            try:
                volts = self.read_volts()
                msg = ""
                for m, v in zip(names, volts):
                    msg += f"{m}: {v:.3f} V "
                print(msg)
                if vprev is None:
                    vprev = volts
                    continue
                for i in range(2):
                    vmin = self.VOLT_RANGE[names[i]][0]
                    vmax = self.VOLT_RANGE[names[i]][1]
                    if volts[i] - vprev[i] > 0 and volts[i] >= vmax:
                        logging.warning(f"Pot {names[i]} at max voltage.")
                        events[i].set()
                    elif volts[i] - vprev[i] < 0 and volts[i] <= vmin:
                        logging.warning(f"Pot {names[i]} at min voltage.")
                        events[i].set()
                    vprev = volts
            except Exception as e:
                logging.error(f"Error during potentiometer monitoring: {e}")
                continue #try again
