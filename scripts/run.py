import time
from threading import Event, Thread
import eigsep_motor_control as emc

# motor velocities
AZ_VEL = 254
ALT_VEL = 0  # 254

pot = emc.Potentiometer()
# create events that tells motors to reverse direction
az_reverse = Event()
alt_reverse = Event()
# thread monitoring potentiometer voltage and setting events
thd = Thread(target=pot.monitor, args=(az_reverse, alt_reverse), daemon=True)
print("starting pot thread")
thd.start()

# start motors
print("start motors")
motor = emc.Motor()
motor.start(az_vel=AZ_VEL, alt_vel=ALT_VEL)

while True:
    print("...")
    try:
        if az_reverse.is_set():
            print("reverse az")
            motor.reverse("az")
            az_reverse.clear()
        if alt_reverse.is_set():
            print("reverse alt")
            motor.reverse("alt")
            alt_reverse.clear()
        time.sleep(0.1)
        continue
    except KeyboardInterrupt:
        break

motor.stop(motors=["az", "alt"])
# motor.stow(motors=["az", "alt"])
