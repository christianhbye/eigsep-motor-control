from argparse import ArgumentParser
import logging
import time
from threading import Event, Thread
import eigsep_motor_control as emc
from RPi import GPIO

GPIO.setwarnings(False)
start_time = time.time()
# Setup logging for information and debugging.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Argument parsing setup to configure motor velocities and monitoring options.
parser = ArgumentParser(description="Control the motors")
parser.add_argument(
    "-b",
    "--board",
    type=str,
    default="pololu",
    help="Motor board type: ``pololu'' (default) or ``qwiic''",
)
parser.add_argument(
    "-a",
    "--az",
    type=int,
    nargs="?",
    const=None,
    default=0,
    help="Azimuth motor velocity",
)
parser.add_argument(
    "-e",
    "--el",
    type=int,
    nargs="?",
    const=None,
    default=0,
    help="Elevation motor velocity",
)
parser.add_argument(
    "-p", "--pot", action="store_true", help="Monitor potentiometer"
)
parser.add_argument(
    "-s",
    "--safe",
    action="store_true",
    help="Monitor pot, limit switch, and check for no movement.",
)
args = parser.parse_args()

if args.safe:
    args.pot = True

if args.board not in ["pololu", "qwiic"]:
    logging.info("No valid motor argument given, defaulting to pololu.")
    args.board = "pololu"

# default motor speed is set to the maximum speed for the given board
if args.az is None:
    AZ_VEL = emc.motor.MAX_SPEED[args.board]
else:
    AZ_VEL = args.az
if args.el is None:
    ALT_VEL = emc.motor.MAX_SPEED[args.board]
else:
    ALT_VEL = args.el

if args.pot:
    # Initialize events for reversing motor direction based on pot monitoring.
    reverse_events = []
    for vel in [AZ_VEL, ALT_VEL]:
        if vel != 0:
            event = Event()
        else:
            event = None
        reverse_events.append(event)
    pot = emc.Potentiometer()
    # Create and start a separate thread to monitor potentiometer if enabled.
    thd = Thread(target=pot.monitor, args=reverse_events, daemon=True)
    logging.info("Starting pot thread.")
    thd.start()
else:
    logging.warning("Potentiometers not being monitored.")

# Start the motors with the specified velocities.
logging.info(f"Starting motors with speeds: az={AZ_VEL}, alt={ALT_VEL}.")
if args.board == "qwiic":
    motor = emc.QwiicMotor(logger=logger)
elif args.board == "pololu":
    motor = emc.PololuMotor(logger=logger)
motor.set_velocity(AZ_VEL, ALT_VEL)

# Initialize limit switch events if monitoring is enabled.
if args.safe:
    # events indicating limit switches are triggered
    limits = [Event(), Event()]

last_motion = time.time()  # time of last motor movement
try:
    while True:
        if not args.pot:  # nothing is happening, there are no safety checks
            time.sleep(1)
            continue

        # else we monitor the potentiometer
        if args.safe:
            # check if both motors show no movement
            if pot.direction["az"] != 0 or pot.direction["alt"] != 0:
                last_motion = time.time()
            # no movement detected for 10 seconds
            elif time.time() >= last_motion + 10:
                logging.warning(
                    "No movement detected from either motor. Exiting."
                )
                break

            # check and handle limit switch events
            limits = emc.reverse_limit(motor, pot, limits)

        # Check and react to reverse signals set by potentiometer monitoring.
        for name, event in zip(["az", "alt"], reverse_events):
            if event is None:
                continue
            if event.is_set():
                print(f"Reversing {name} motor.")
                motor.reverse(name)
                time.sleep(0.5)
                event.clear()

        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting.")
finally:
    # ensure motors are stopped on exit.
    run_time = time.time() - start_time
    print(f"Run Time: {run_time} seconds, {run_time/3600} hours.")
    motor.cleanup()
