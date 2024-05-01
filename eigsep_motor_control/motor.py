import numpy as np
import time
from qwiic_scmd import QwiicScmd
from abc import ABC, abstractmethod

MOTOR_ID = {"az": 0, "alt": 1}

class Motor(ABC):
    def __init__(self):
        self.velocities = {"az": (0, 0), "alt": (0, 0)}
        self.debounce_interval = 5  # debounce interval in seconds
        self.last_reversal_time = {'az': -5, 'alt': -5}  # last reversal timestamps for motors

    @abstractmethod
    def start(self, az_vel, alt_vel):
        """Start the motors with specified velocities."""
        pass

    def should_reverse(self, motor):
        """Determine if the motor should reverse."""
        current_time = time.time()
        if current_time - self.last_reversal_time[motor] > self.debounce_interval:
            return True
        return False

    @abstractmethod
    def reverse(self, motor):
        """Reverse the specified motor."""
        pass

    @abstractmethod
    def stop(self, motors=["az", "alt"]):
        """Stop the specified motors."""
        pass

    @abstractmethod
    def stow(self, motors=["az", "alt"]):
        """Stow the specified motors (typically return to a safe position)."""
        pass

class QwiicMotor(Motor, QwiicScmd):
    def __init__(self):
        Motor.__init__(self)  # Initialize Motor attributes
        QwiicScmd.__init__(self, address=None, i2c_driver=None)
        assert self.begin(), "Initialization of SCMD failed."
        self.enable()
        for i in [0, 1]:
            self.set_drive(i, 0, 0)

    def start(self, az_vel=254, alt_vel=254):
        """Starts both motors (azimuth and altitude) with the given velocities."""
        velocities = {"az": az_vel, "alt": alt_vel}
        for m, v in velocities.items():
            speed = np.abs(v)
            if speed == 0:
                continue
            direction = 1 if v > 0 else 0
            self.set_drive(MOTOR_ID[m], direction, speed)
            conventional_direction = 1 if direction == 1 else -1
            self.velocities[m] = (conventional_direction, speed)

    def reverse(self, motor):
        """Reverses the specified motor (azimuth or altitude)."""
        if self.should_reverse(motor):
            d, s = self.velocities[motor]
            reverse_dir = -1 * d
            direction = 1 if reverse_dir > 0 else 0
            self.set_drive(MOTOR_ID[motor], direction, s)
            self.last_reversal_time[motor] = time.time()
            self.velocities[motor] = (reverse_dir, s)

    def stop(self, motors=["az", "alt"]):
        """Stops specified motors (azimuth and/or altitude)."""
        if isinstance(motors, str):
            motors = [motors]
        for m in motors:
            self.set_drive(MOTOR_ID[m], 0, 0)

    def stow(self):
        """Stow method for returning motors to a home position."""
        raise NotImplementedError("Stow method not implemented.")

try:
    from dual_max14870_rpi import motors, MAX_SPEED

    class PoluluMotor(Motor):
        def __init__(self):
            super().__init__()

        def start(self, az_vel=MAX_SPEED, alt_vel=MAX_SPEED):
            """Starts both motors (azimuth and altitude) with the given velocities."""
            az_direction = 1 if az_vel > 0 else 0
            alt_direction = 1 if alt_vel > 0 else 0
            motors.setSpeeds(az_vel, alt_vel)
            self.velocities["az"] = (az_direction, abs(az_vel))
            self.velocities["alt"] = (alt_direction, abs(alt_vel))

        def reverse(self, motor):
            """Reverses the specified motor (azimuth or altitude)."""
            if self.should_reverse(motor):
                if motor in self.velocities:
                    current_direction, current_speed = self.velocities[motor]
                    new_direction = 0 if current_direction == 1 else 1
                    new_speed = -current_speed if current_direction == 1 else current_speed
                    if motor == "az":
                        motors.motor1.setSpeed(new_speed)  # motor1 for azimuth
                    elif motor == "alt":
                        motors.motor2.setSpeed(new_speed)  # motor2 for altitude
                    self.velocities[motor] = (new_direction, abs(new_speed))

        def stop(self, motors=["az", "alt"]):
            """Stops specified motors (azimuth and/or altitude)."""
            for motor in motors:
                if motor == "az":
                    motors.motor1.setSpeed(0)
                elif motor == "alt":
                    motors.motor2.setSpeed(0)
                self.velocities[motor] = (self.velocities[motor][0], 0)

        def stow(self):
            """Stow method for returning motors to a home position."""
            raise NotImplementedError("Stow method not implemented.")
    
except ImportError:
    pass