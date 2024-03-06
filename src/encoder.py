import logging
import serial
import struct
import time
from qwiic_dual_encoder_reader import QwiicDualEncoderReader
from eigsep_motor_control.motor import MOTOR_ID
from .main import BAUDRATE, INT_LEN, SLEEP

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
    PORT = '/dev/ttyACM0'
    TIMEOUT = INT_LEN * SLEEP * 1.2  # set timeout to be sleep time + 20%

    def __init__(self)
        """
        Class for reading voltages from the potentiometers.
        """
        self.ser = serial.Serial(
            port=self.PORT, baudrate=BAUDRATE, timeout=self.TIMEOUT
        )
        sel.ser.reset_input_buffer()
        


    def bit2volt(self, analog_value):
        res = 2 ** self.NBITS - 1
        ratio = self.VMAX / res
        return ratio * analog_value

    def read_analog(self):
        """
        Read the analog values of the pots.

        Returns
        -------
        val : tuple
            Tuple of the analog values of the pots. The first value is the
            azimuth pot and the second value is the altitude pot.

        """
        data = self.ser.read(8)
        if len(data) < 8:
            logging.warning("Serial read timed out.")
            #XXX do something here
        else:
            val = struct.unpack("<ff", data)
            return val


    def read_volts(self, motor):
        analog = self.read_analog()
        if motor == "az":
            return self.bit2volt(analog[0])
        elif motor == "alt":
            return self.bit2volt(analog[1])

    def hit_edge(self, motor):
        """
        Check if the motor has rotated to the end of the pot voltage range.

        Parameters
        ----------
        motor : str
            Specify the motor, must be ``alt'' or ``az''.

        Returns
        -------
        bool
            True if the motor has hit the edge, False otherwise.

        """
        v = self.read_volts(motor)
        return v >= self.VMAX - self.TOL or v <= self.TOL:

    def monitor(self, az_event, alt_event):
        while True:
            if self.hit_edge("az"):
                az_event.set()
            if self.hit_edge("alt"):
                alt_event.set()
            # may need a sleep here, but read analog alredy sleeps
