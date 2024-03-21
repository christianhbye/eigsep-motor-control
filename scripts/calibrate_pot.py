from argparse import ArgumentParser
import time
import numpy as np
import eigsep_motor_control as emc

parser = ArgumentParser(description="Calibrate potentiometers.")
parser.add_argument("-a", "--az", action="store_true", help="Calibrate azimuth pot.")
parser.add_argument("-e", "--el", action="store_true", help="Calibrate elevation pot.")
args = parser.parse_args()

motors = []
if args.az:
    motors.append("az")
if args.el:
    motors.append("alt")
if not motors:
    print("Exiting...")
    import sys; sys.exit()

motor = emc.Motor()
pot = emc.Potentiometer()
vmax = {"az": 0, "alt": 0}

for m in motors:
    print(f"Calibrating {m.upper()} motor")
    if m == "az":
        az_vel = 254
        alt_vel = 0
    else:
        az_vel = 0
        alt_vel = 254
    motor.start(az_vel=az_vel, alt_vel=alt_vel)
    try:
        vprev = 0
        vcurr = 0
        vm = vmax[m]
        while vcurr >= vprev or vm-vcurr<0.1:  # loops until the switch is triggered
            print("Attack mode.")
            vprev = vcurr
            vcurr = pot.read_volts(motor=m)
            print(vcurr)
            vm = np.max([vcurr, vm])
            time.sleep(0.1)
        vmax[m] = (
            vm  # XXX feels like setting vmax slightly smaller than this would be better to never trigger the switch
        )
        while vcurr <= vprev:  # loops until the switch is released
            print("Switch is triggered, keep going until released!")
            vprev = vcurr
            vcurr = pot.read_volts(motor=m)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupting.")
    finally:
        print("Stopping.")
        motor.stop()

print(vmax)
