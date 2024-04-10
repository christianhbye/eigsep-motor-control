from argparse import ArgumentParser
import logging
import time
from threading import Thread, Event
import eigsep_motor_control as emc

parser = ArgumentParser(description="Control the motors")
parser.add_argument("-a", "--az", type=int, help="Azimuth motor velocity")
parser.add_argument("-e", "--el", type=int, help="Elevation motor velocity")
parser.add_argument("-p", "--pot", action="store_true", help="Monitor potentiometer")
args = parser.parse_args()

AZ_VEL = args.az if args.az else 0
ALT_VEL = args.el if args.el else 0

az_reverse = Event()
alt_reverse = Event()

if args.pot:
    pot = emc.Potentiometer()
    thd = Thread(target=pot.monitor, args=(az_reverse, alt_reverse), daemon=True)
    logging.info("Starting pot thread.")
    thd.start()
else:
    logging.warning("Potentiometers not being monitored.")

motor = emc.Motor()

def safe_motor_operation(motor, operation, *args, **kwargs):
    while True:
        try:
            # Attempt to get the operation from the motor object and call it
            action = getattr(motor, operation)
            action(*args, **kwargs)
            break  # Exit the loop if the operation is successful
        except Exception as e:
            logging.error(f"Error during {operation}: {e}. Retrying operation.")
            motor.stop(motors=["az", "alt"])
            time.sleep(1)  # Wait a bit before retrying
            motor.start(az_vel=AZ_VEL, alt_vel=ALT_VEL)
            # The loop now retries the operation

safe_motor_operation('start', az_vel=AZ_VEL, alt_vel=ALT_VEL)

while True:
    try:
        if az_reverse.is_set():
            logging.info("Reversing az motor.")
            safe_motor_operation('reverse', "az")
            az_reverse.clear()
        if alt_reverse.is_set():
            logging.info("Reversing alt motor.")
            safe_motor_operation('reverse', "alt")
            alt_reverse.clear()
        time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Exiting.")
        break

safe_motor_operation('stop', motors=["az", "alt"])
