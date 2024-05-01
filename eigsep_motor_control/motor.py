import numpy as np
import time
from qwiic_scmd import QwiicScmd

MOTOR_ID = {"az": 0, "alt": 1}


class Motor(QwiicScmd):

    def __init__(self):
        """
        Class for controlling and monitoring DC motors using Sparkfun AutoPHat
        and associated software.

        """
        super().__init__(address=None, i2c_driver=None)
        assert self.begin(), "Initalization of SCMD failed."
        for i in [0, 1]:
            self.set_drive(i, 0, 0)
        self.enable()
        # current velocities of the form (direction, speed):
        self.velocities = {"az": (0, 0), "alt": (0, 0)}
        self.debounce_interval = 5  # debounce interval in seconds
        self.last_reversal_time = {
            "az": -5,
            "alt": -5,
        }  # last reversal timestamps for motors

    def start(self, az_vel=254, alt_vel=254):
        """
        Start one or both motors with the given velocities. The given motor
        will not start if the speed is set to 0.

        Parameters
        ----------
        az_vel : int
            The velocity of the azimuthal motor. Positive values indicate
            clockwise rotation as seen from the top. Must be in the
            range [-255, 254].
        alt_vel : int
            Same as ``speed_az'' for the altitude motor.

        """
        velocities = {"az": az_vel, "alt": alt_vel}
        for m, v in velocities.items():
            speed = np.abs(v)
            if speed == 0:
                continue
            direction = 1 if v > 0 else 0
            self.set_drive(MOTOR_ID[m], direction, speed)
            conventional_direction = 1 if direction == 1 else -1
            self.velocities[m] = (conventional_direction, speed)

    def should_reverse(self, motor):
        """
        Check if enough time has passed since the last reversal.

        Parameters
        ----------
        motor : str
            The motor to reverse. Valid names are ``az'' and ``alt'' for the
            azimuth and altitude motors, respectively.

        Returns
        -------
        bool
            Returns True if enough time has passed since last reversal, False
            otherwise.

        """
        current_time = time.time()
        if (
            current_time - self.last_reversal_time[motor]
            > self.debounce_interval
        ):
            return True
        return False

    def reverse(self, motor):
        """
        Reverse one of the motors. If debounce is active, ignore.

        Parameters
        ----------
        motors : str
            The motor to reverse. Valid names are ``az'' and ``alt'' for the
            azimuth and altitude motors, respectively.

        """
        if self.should_reverse(motor):
            d, s = self.velocities[motor]
            reverse_dir = -1 * d  # turn -1 to 1 and vice versa
            direction = 1 if reverse_dir > 0 else 0
            self.set_drive(MOTOR_ID[motor], direction, s)
            self.last_reversal_time[motor] = time.time()
            self.velocities[motor] = (reverse_dir, s)
        else:
            print(f"Debounce active. Skipping reversal for {motor}.")

    def stop(self, motors=["az", "alt"]):
        """
        Stop one or both motors.

        Parameters
        ----------
        motors : str or list of str
            The motor(s) to stop. Valid names are ``az'' and ``alt'' for the
            azimuth and altitude motors, respectively.

        """
        if isinstance(motors, str):
            motors = [motors]
        for m in motors:
            self.set_drive(MOTOR_ID[m], 0, 0)

    def stow(self, motors=["az", "alt"]):
        """Return to home."""
        raise NotImplementedError
