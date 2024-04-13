import logging
import numpy as np
import serial
import time
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
    VMAX = 3.3

    # serial connection constants (BAUDRATE defined in main.py)
    PORT = "/dev/ttyACM0"

    def __init__(self):
        """
        Class for reading voltages from the potentiometers.
        """
        self.ser = serial.Serial(port=self.PORT, baudrate=BAUDRATE)
        self.ser.reset_input_buffer()

        # voltage range of the pots
        self.VOLT_RANGE = {"az": (0, 5), "alt": (0.7, 2.7)}

        # voltage measurements (az, alt)
        size = 5  # number of measurements to store XXX
        self.volts = np.zeros((size, 2))
        self.reset_volt_readings()

    @property
    def vdiff(self):
        az, alt = np.diff(self.volts, axis=0).T
        return {"az": az, "alt": alt}

    @property
    def direction(self):
        # XXX might need to adjust the size so that we can pick up change
        # of direction quickly enough
        d = {}
        for k, v in self.vdiff.items():
            x = np.sign(np.mean(v))
            d[k] = x if x == 1 else 0
        return d

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
        v = self.bit2volt(self.read_analog())
        self.volts = np.concatenate((self.volts[1:], v[None]), axis=0)
        if motor == "az":
            return v[0]
        elif motor == "alt":
            return v[1]
        else:
            return v

    def reset_volt_readings(self):
        """
        Read pot voltages quickly in succesion to reset the buffer. This
        is useful to get meaningful derivatives.
        """
        for i in range(self.volts.shape[0]):
            _ = self.read_volts()
            time.sleep(0.1)

    def monitor(self, az_event, alt_event):
        names = ("az", "alt")
        events = (az_event, alt_event)
        while True:
            volts = self.read_volts()
            msg = ""
            for m, v in zip(names, volts):
                msg += f"{m}: {v:.3f} V "
            print(msg)
            for i in range(2):
                vmin = self.VOLT_RANGE[names[i]][0]
                vmax = self.VOLT_RANGE[names[i]][1]
                d = self.direction[names[i]]
                if d > 0 and volts[i] >= vmax:
                    logging.warning(f"Pot {names[i]} at max voltage.")
                    events[i].set()
                    self.reset_volt_readings()
                elif d < 0 and volts[i] <= vmin:
                    logging.warning(f"Pot {names[i]} at min voltage.")
                    events[i].set()
                    self.reset_volt_readings()
            #time.sleep(0.5)
