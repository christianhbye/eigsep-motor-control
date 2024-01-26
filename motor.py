from qwiic_dual_encoder_reader import QwiicDualEncoderReader
from qwiic_scmd import QwiicScmd


class Motor:
    def __init__(self, n_motors=2):
        self.motor = QwiicScmd()
        begin = self.motor.begin()
        assert begin, "Initalization of SCMD failed"
        for i in range(n_motors):
            self.motor.set_drive(i, 0, 0)
        self.motor.enable()

        self.encoder = QwiicDualEncoderReader()
        self.encoder.begin()

    def start(self, motor_id, speed, distance):
        """
        Start the motor with the given speed.

        Parameters
        ----------
        motor_id : int
            The id of the motor to start.
        speed : int
            The speed to start the motor at. Positive values are forward,
            negative values are backward. Must be between -255 and 255.
        """
        direction = 1 if speed > 0 else 0
        
        distance = abs(distance) if speed > 0 else -1*abs(distance)
        
        speed = abs(speed)
        
        if distance != float('inf'):
            original = get_encoder(motor_id)
            destination = original+distance
        else:
            destination = distance
        
        self.motor.set_drive(motor_id, direction, speed)
        
        while(get_encoder(motor_id) != destination):
            
        stop(motor_id)
                
            

    def stop(self, motor_id):
        self.motor.set_drive(motor_id, 0, 0)

    def get_encoder(self, motor_id):
        if motor_id == 0:
            return self.encoder.count1
        elif motor_id == 1:
            return self.encoder.count2
        else:
            raise KeyError("Invalid motor id.")
