import time
import eigsep_motor_control as emc

motor = emc.Motor()
pot = emc.Potentiometer()
vmax = {}

for m in ["az", "alt"]:
    print(f"Calibrating {m.upper()} motor")
    if m == "az":
        az_vel = 254
        alt_vel = 0
    else:
        az_vel = 0
        alt_vel = 254
    motor.start(az_vel=az_vel, alt_vel=alt_vel)
    vprev = 0
    vcurr = 0
    while vcurr >= vprev:  # loops until the switch is triggered
        vprev = vcurr
        vcurr = pot.read_volts(motor=m)
        print(vcurr)
        time.sleep(0.1)
    vmax[m] = (
        vcurr  # XXX feels like setting vmax slightly smaller than this would be better to never trigger the switch
    )
    while vcurr <= vprev:  # loops until the switch is released
        vprev = vcurr
        vcurr = pot.read_volts(motor=m)
        time.sleep(0.1)
    motor.stop()

print(vmax)
