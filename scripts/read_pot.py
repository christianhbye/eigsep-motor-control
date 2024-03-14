import time
from eigsep_motor_control import Potentiometer

pot = Potentiometer()
print(pot.TIMEOUT)

while True:
    v = pot.read_volts()
    print(v)
    time.sleep(0.1)
