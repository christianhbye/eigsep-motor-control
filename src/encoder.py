import serial
import time
from qwiic_dual_encoder_reader import QwiicDualEncoderReader
from .motor import MOTOR_ID

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

    def __init__(self, motors=["az", "alt"])
        """
        Class for reading voltages from the potentiometers.
        """
        #XXX should specify baud rate, port etc and open the serial connection.
        pass

    def bit2volt(self, analog_value):
        res = 2 ** self.NBITS - 1
        ratio = self.VMAX / res
        return ratio * analog_value

    def read_analog(self, motor):
        """
        Read the analog value from a pot.
        """
        raise NotImplementedError

    def read_volts(self, motor):
        analog = self.read_analog(motor)
        return self.bit2volt(analog)

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
