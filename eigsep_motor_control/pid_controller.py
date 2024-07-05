import time

class PIDController:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()

    def update(self, measurement):
        current_time = time.time()
        delta_time = current_time - self.last_time
        error = self.setpoint - measurement
        self.integral += error * delta_time
        derivative = (error - self.last_error) / delta_time if delta_time > 0 else 0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        self.last_time = current_time
        return output
