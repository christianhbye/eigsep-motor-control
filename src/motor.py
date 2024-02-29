import numpy as np
from qwiic_scmd import QwiicScmd


class Motor(QwiicScmd):

    MOTOR_ID = {"az": 0, "alt": 1}

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

    def start(self, speed_az=254, speed_alt=254):
        """
        Start one or both motors with the given velocities. The given motor
        will not start if the speed is set to 0.

        Parameters
        ----------
        speed_az : int
            The velocity of the azimuthal motor. Positive values indicate
            clockwise rotation as seen from the top. Must be in the
            range [-255, 254].
        speed_alt : int
            Same as ``speed_az'' for the altitude motor.

        """
        velocities = {"az": speed_az, "alt": speed_alt}
        for m, v in velocities.items():
            speed = np.abs(v)
            if speed == 0:
                continue
            direction = 1 if v > 0 else 0
            self.set_drive(self.MOTOR_ID[m], direction, speed)

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
            self.motor.set_drive(self.MOTOR_ID[m], 0, 0)

    def stow(self, motors=["az", "alt"]):
        """Return to home."""
        raise NotImplementedError
