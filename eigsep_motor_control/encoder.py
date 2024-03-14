import logging
import serial
import struct
import numpy as np
from qwiic_dual_encoder_reader import QwiicDualEncoderReader
from eigsep_motor_control.motor import MOTOR_ID
from eigsep_motor_control.serial_params import BAUDRATE, INT_LEN, SLEEP


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
    VMAX = 3.3  # voltage range of pot (V)
    TOL = 0.5  # how close to 0 or VMAX we can go in volts before reversing

    # serial connection constants (BAUDRATE defined in main.py)
    PORT = "/dev/ttyACM0"
    TIMEOUT = INT_LEN * SLEEP * 2  # set timeout to be sleep time * 2

    def __init__(self):
        """
        Class for reading voltages from the potentiometers.
        """
        self.ser = serial.Serial(
            port=self.PORT, baudrate=BAUDRATE, timeout=self.TIMEOUT
        )
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
        val : np.ndarray
            The analog values of the pots. The first value is the
            azimuth pot and the second value is the altitude pot.

        """
        print("Reading")
        data = self.ser.readline().decode("utf-8").strip() 
        print("read")
        if len(data) < 8:  # timeout before all data was read
            logging.warning("Serial read timed out.")
            # XXX do something here
        else:
            val = struct.unpack("<ii", data)
            return np.array(val) / INT_LEN

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
            if vprev is None:
                vprev = volts
                continue
            for i, v in enumerate(volts):
                print(v)
                break
                if v - vprev[i] > 0 and v >= self.VMAX - self.TOL:
                    logging.warning(f"Pot {names[i]} at max voltage.")
                    events[i].set()
                elif v - vprev[i] < 0 and v <= self.TOL:
                    logging.warning(f"Pot {names[i]} at min voltage.")
                    events[i].set()
            vprev = volts
            # may need a sleep here, but read analog alredy sleeps
