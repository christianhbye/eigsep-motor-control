import logging
import numpy as np
import serial
import time
from threading import Event
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

        Returns
        -------
        encoder : int
            The encoder value corresponding to the given motor.

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
        self.VOLT_RANGE = {"az": (0.3, 2.5), "alt": (1.0, 2.25)}
        self.POT_ZERO_THRESHOLD = 0.03

        # voltage measurements (az, alt)
        size = 3  # number of measurements to store XXX
        self.volts = np.zeros((size, 2))
        self.reset_volt_readings()

    @property
    def vdiff(self):
        """
        Finds the difference between the last {size} voltage readings of each pot.

        """
        az, alt = np.diff(self.volts, axis=0).T
        return {"az": az, "alt": alt}

    @property
    def direction(self):
        """
        Determines direction of az/alt motors based on last {size} voltage readings of the respective pot.

        """
        # XXX might need to adjust the size so that we can pick up change
        # of direction quickly enough
        d = {}
        for k, v in self.vdiff.items():
            x = np.mean(v)
            d[k] = np.sign(x) if np.abs(x) > self.POT_ZERO_THRESHOLD else 0 #return a direction of 1 or 0 only if it is determined to not be stationary
        return d

    def bit2volt(self, analog_value):
        """
        Converts an analog value from digital-to-analog converter (DAC) units to volts.

        Parameters
        -------
        analog_value : int
            The digital value to be converted to volts.

        Returns
        -------
        voltage : float
            The calculated voltage corresponding to the given digital value.

        """
        res = 2**self.NBITS - 1
        voltage = (self.VMAX / res)*analog_value
        return voltage

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
        """
        Reads the current voltage from an analog sensor, converts it to volts, and updates the internal voltage history.

        Parameters
        -------
        motor : str, optional
            The motor identifier ('az' for azimuth or 'alt' for altitude) for which the voltage
            is to be returned. If no motor is specified, the voltage for all motors is returned.

        Returns
        -------
        v : float/np.ndarray
            The voltage reading for the specified motor, or an array of voltages if no motor is specified.

        """
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
            time.sleep(0.05)

    def monitor(self, az_event, alt_event):
        """
        Continuously monitors the voltage levels of the 'az' (azimuth) and 'alt' (altitude)
        motors and checks these against predefined voltage ranges to trigger events if 
        voltage limits are reached.

        Parameters
        -------
        az_event : threading.Event
            An event triggered when the azimuth motor reaches its voltage limit.
        alt_event : threading.Event
            An event triggered when the altitude motor reaches its voltage limit.
            
        """
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
                # Check if the current voltage exceeds the maximum limit during positive direction.
                if d > 0 and volts[i] >= vmax:
                    logging.warning(f"Pot {names[i]} at max voltage.")
                    events[i].set()
                    self.reset_volt_readings()
                # Check if the current voltage goes below the minimum limit during negative direction.
                elif d < 0 and volts[i] <= vmin:
                    logging.warning(f"Pot {names[i]} at min voltage.")
                    events[i].set()
                    self.reset_volt_readings()
