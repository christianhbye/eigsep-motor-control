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

    VMAX = 3.3  # voltage range
    NBITS = 16  # ADC number of bits

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
        analog = self.read_analog()
        return self.bit2volt(analog)

    @property
    def 

    def get_position(self, motor):
        v = self.read_volts()
        #XXX convert voltage to position
        raise NotImplementedError
