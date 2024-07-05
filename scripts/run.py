from argparse import ArgumentParser
import logging
import time
from threading import Event, Thread
import eigsep_motor_control as emc

start_time = time.time()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

parser = ArgumentParser(description="Control the motors")
parser.add_argument("-b", "--board", type=str, default="pololu", help="Motor board type: ``pololu'' (default) or ``qwiic''")
parser.add_argument("-a", "--az", type=int, nargs="?", const=None, default=0, help="Azimuth motor velocity")
parser.add_argument("-e", "--el", type=int, nargs="?", const=None, default=0, help="Elevation motor velocity")
parser.add_argument("-p", "--pot", action="store_true", help="Monitor potentiometer")
parser.add_argument("-s", "--safe", action="store_true", help="Monitor pot, limit switch, and check for no movement.")
parser.add_argument("-d", "--dummy_pot", action="store_true", help="Dummy potentiometer mode for testing purposes.")
parser.add_argument("-m", "--dummy_motor", action="store_true", help="Dummy motor mode for testing purposes.")
args = parser.parse_args()

if args.board == "dummy":
    args.dummy_motor = True
if args.dummy_motor:
    args.dummy_pot = True
if args.safe or args.dummy_pot:
    args.pot = True

if args.dummy_motor or args.board == "dummy":
    args.board = "dummy"
    motor = emc.DummyMotor(logger=logger)
elif args.board not in ["pololu", "qwiic"]:
    logging.info("No valid motor argument given, defaulting to pololu.")
    args.board = "pololu"
    motor = emc.PololuMotor(logger=logger)
elif args.board == "pololu":
    motor = emc.PololuMotor(logger=logger)
elif args.board == "qwiic":
    motor = emc.QwiicMotor(logger=logger)    

AZ_VEL = args.az if args.az is not None else emc.motor.MAX_SPEED[args.board]
ALT_VEL = args.el if args.el is not None else emc.motor.MAX_SPEED[args.board]

if args.pot:
    reverse_events = [Event() if vel != 0 else None for vel in [AZ_VEL, ALT_VEL]]
    pot = emc.DummyPotentiometer(motor) if args.dummy_pot else emc.Potentiometer()
    thd = Thread(target=pot.monitor, args=reverse_events, daemon=True)
    logging.info("Starting pot thread.")
    thd.start()

    kp, ki, kd = 1.0, 0.1, 0.01
    az_pid = emc.PIDController(kp, ki, kd, pot.VOLT_RANGE['az'][1])
    alt_pid = emc.PIDController(kp, ki, kd, pot.VOLT_RANGE['alt'][1])
else:
    logging.warning("Potentiometers not being monitored.")

motor.set_velocity(AZ_VEL, ALT_VEL)

if args.safe:
    limits = [Event(), Event()]

last_motion = time.time()
try:
    while True:
        if not args.pot:
            time.sleep(1)
            continue

        if args.safe:
            if pot.direction["az"] != 0 or pot.direction["alt"] != 0:
                last_motion = time.time()
            elif time.time() >= last_motion + 10:
                logging.warning("No movement detected from either motor. Exiting.")
                break
            limits = emc.reverse_limit(motor, pot, limits)

        for name, event in zip(["az", "alt"], reverse_events):
            if event is None:
                continue
            if event.is_set():
                print(f"Reversing {name} motor.")
                motor.reverse(name)
                time.sleep(0.5)
                event.clear()

        az_voltage = pot.read_volts('az')
        alt_voltage = pot.read_volts('alt')
        az_adjustment = az_pid.update(az_voltage)
        alt_adjustment = alt_pid.update(alt_voltage)

        new_az_vel = AZ_VEL - az_adjustment
        new_alt_vel = ALT_VEL - alt_adjustment

        motor.set_velocity(new_az_vel, new_alt_vel)

        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting.")
finally:
    run_time = time.time() - start_time
    print(f"Run Time: {run_time} seconds, {run_time/3600} hours.")
    motor.cleanup()
