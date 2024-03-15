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
    # pot voltage range (center is 1.2V, one turn is ~0.5V)
    VMIN = 0.7
    VMAX = 1.7

    # serial connection constants (BAUDRATE defined in main.py)
    PORT = "/dev/ttyACM0"

    def __init__(self):
        """
        Class for reading voltages from the potentiometers.
        """
        self.ser = serial.Serial(port=self.PORT, baudrate=BAUDRATE)
        self.ser.reset_input_buffer()

    def bit2volt(self, analog_value):
        res = 2**self.NBITS - 1
        ratio = self.VMAX / res
        return ratio * analog_value

    def read_analog(self):
        """
        Read the analog values of the pots.

        Returns
        -------
        data : np.ndarray
            The analog values of the pots averaged over INT_LEN
            measurements. The first value is associated with the azimuth
            pot, the second value is the altitude pot.

        """
        data = self.ser.readline().decode("utf-8").strip()
        data = [int(d) for d in data.split()]
        return np.array(data) / INT_LEN

    def read_volts(self, motor=None):
        analog = self.read_analog()
        if motor == "az":
            return self.bit2volt(analog[0])
        elif motor == "alt":
            return self.bit2volt(analog[1])
        else:
            return self.bit2volt(analog)

    def monitor(self, az_event, alt_event):
        names = ("az", "alt")
        events = (az_event, alt_event)
        vprev = None
        while True:
            volts = self.read_volts()
            msg = ""
            for m, v in zip(names, volts):
                msg += f"{m}: {v:.3f} V "
            print(msg)
            if vprev is None:
                vprev = volts
                continue
            for i, v in enumerate(volts):
                if v - vprev[i] > 0 and v >= self.VMAX:
                    logging.warning(f"Pot {names[i]} at max voltage.")
                    events[i].set()
                elif v - vprev[i] < 0 and v <= self.VMIN:
                    logging.warning(f"Pot {names[i]} at min voltage.")
                    events[i].set()
            vprev = volts
