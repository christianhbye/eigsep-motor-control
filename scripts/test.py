import eigsep_motor_control as emc
import time

motor = emc.Motor()
while True:
    try:
        motor.start(az_vel=0, alt_vel=254)
        time.sleep(2)
        motor.start(az_vel=0, alt_vel=-254)
        time.sleep(2)
    except KeyboardInterrupt:
        print("Stop")
        break

motor.stop()
