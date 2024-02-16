from qwiic_dual_encoder_reader import QwiicDualEncoderReader
from qwiic_scmd import QwiicScmd
import serial
import time

class Motor:
    def __init__(self, n_motors=2):
        self.motor = QwiicScmd()
        begin = self.motor.begin()
        assert begin, "Initalization of SCMD failed"
        assert begin, "Initalization of SCMD failed"
        for i in range(n_motors):
            self.motor.set_drive(i, 0, 0)
        self.motor.enable()
 
        self.encoder = QwiicDualEncoderReader()
        self.encoder.begin()


    def start(self, motor_id, velocity, distance):
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
        direction = 1 if velocity > 0 else 0
        
        distance = abs(distance) if velocity > 0 else -1*abs(distance)
        velocity = 254 if velocity == 255 else velocity
        speed = abs(velocity)
        
        if distance != float('inf'):
            original = self.get_encoder(motor_id)%32768
            destination = (original-distance)%32768
        else:
            original = self.get_encoder(motor_id)%32768
            destination = distance
            self.motor.set_drive(motor_id, direction, speed)
            return
        
        overflow = 0
        if original+abs(distance) > 32768:
            overflow = 1
        elif original-distance < 0:
            overflow = 1
        else:
            overflow = 0        

        self.motor.set_drive(motor_id, direction, speed)
        
        while overflow == 1:
            #print(self.get_encoder(motor_id)%32768, destination)
            if speed < 0:
                if self.get_encoder(motor_id)%32768 < destination:
                    overflow = 0
            elif speed > 0:
                if self.get_encoder(motor_id)%32768 > destination:
                    overflow = 0
            else:
                break

        while(self.get_encoder(motor_id) != destination):
            print(self.get_encoder(motor_id)%32768, destination)
            if velocity < 0:
                if self.get_encoder(motor_id)%32768 >= destination:
                    break
            elif velocity > 0:
                if self.get_encoder(motor_id)%32768 <= destination:
                    break
            else:
                break
            
        self.stop(motor_id)
                
            

    def stop(self, motor_id):
        self.motor.set_drive(motor_id, 0, 0)

    def get_encoder(self, motor_id):
        if motor_id == 0:
            return self.encoder.count1
        elif motor_id == 1:
            return self.encoder.count2
        else:
            raise KeyError("Invalid motor id.")
    
    def serial_read(self, port):
        baudrate = 921600
        #port for 1st pico is "/dev/ttyACM0"
        ser = serial.Serial(port, baudrate)

        ser.dtr = False
        time.sleep(0.5)
        ser.dtr = True

        analog_value=0

        while True:
            if ser.in_waiting:
                analog_str = ser.readline().decode('utf-8').strip()
                analog_value = int(analog_str)
                volt_value = (3.3/65535)*analog_value
                print("Analog Value: ", analog_value, " Voltage Value: ", volt_value)

        #port = "/dev/ttyACM0"
        #serial_connect(port, 'higher', 50000)

    def serial_motor_control(self, port, operator, threshold, motor_id, speed):
        print('Aligning operator and direction')
        if operator == 'higher':
            speed = -1*abs(speed)
        elif operator == 'lower':
            speed = abs(speed)
            speed = 254 if speed == 255 else speed
        else:
            print('Invalid operator')
            return
        direction = 1 if speed > 0 else 0
        
        if threshold>58000:
            threshold = 58000
        elif threshold<1000:
            threshold = 1000
        
        baudrate = 921600
        #port for 1st pico is "/dev/ttyACM0"
        ser = serial.Serial(port, baudrate)

        ser.dtr = False
        time.sleep(0.5)
        ser.dtr = True

        analog_value=0

        self.motor.set_drive(motor_id, direction, abs(speed))
        print('Attempting to reach ', threshold)
        while True:
            if ser.in_waiting:
                analog_str = ser.readline().decode('utf-8').strip()
                analog_value = int(analog_str)
                volt_value = (3.3/65535)*analog_value
                print("Analog Value: ", analog_value, " Voltage Value: ", volt_value)
                if operator == 'higher':
                    if analog_value >= threshold: 
                        print ('Reached target.')
                        break
                elif operator == 'lower':
                    if analog_value <= threshold:
                        print('Reached target')
                        break
        self.stop(motor_id)
        time.sleep(0.5)
        if abs(analog_value-threshold) >= 50:
            print('Correcting error.')
            direction = 1 if direction == 0 else 0
            self.motor.set_drive(motor_id, direction, 100)
            while True:
                if operator == 'higher':
                    if analog_value >= threshold: 
                        print ('Reached target.')
                        break
                elif operator == 'lower':
                    if analog_value <= threshold:
                        print('Reached target')
                        break
        
        self.stop(motor_id)
        print('Done!')
        #port = "/dev/ttyACM0"
        #serial_connect(port, 'higher', 50000, 0, -255)
