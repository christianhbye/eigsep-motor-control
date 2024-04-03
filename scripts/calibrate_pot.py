from argparse import ArgumentParser
import sys
import time
import numpy as np
import eigsep_motor_control as emc


def calibrate(motor, direction):
    """
    Calibrate the potentiometer corresponding to the motor.

    Parameters
    ----------
    motor : str
        Motor to calibrate. Either 'az' or 'alt'.
    direction : int
        Direction of the motor. 1 for forward (increasing pot voltages),
        -1 for reverse (decreasing pot voltages).

    Returns
    -------
    vm : float
        Maximum/minimum pot voltage (depending on the direction).
    stuck : bool
        True if the pot was stuck, False otherwise.

    """
    if motor == "az":
        motor_id = 0
        az_vel = 254
        alt_vel = 0
    elif motor == "alt":
        motor_id = 1
        az_vel = 0
        alt_vel = 254
    else:
        raise ValueError("Invalid motor.")

    az_vel *= direction
    alt_vel *= direction

    motor = emc.Motor()
    pot = emc.Potentiometer()
    motor.start(az_vel=az_vel, alt_vel=alt_vel)
    pot.reset_volt_readings()

    # loops until the switch is triggered
    print("Attack mode.")
    while pot.direction[motor] == direction:
        v = pot.read_volts(motor=motor)
        print(v)
        time.sleep(0.1)
    # get the extremum pot voltage (max if forward, min if reverse)
    vm = np.max(direction * pot.volts[:, motor_id])

    # now: either the pot is stuck or the switch is triggered
    # this loops runs as long as the pot is stuck
    tol = 0.01  # XXX arbitrary threshold for pot being stuck
    stuck_cnt = np.count_nonzero(np.abs(pot.vdiff[motor]) < tol)
    while np.abs(pot.vdiff[motor])[-1] < tol:
        v = pot.read_volts(motor=motor)
        print(v)
        stuck_cnt += 1
        time.sleep(0.1)
    print("Reverse until switch is released.")
    while pot.direction[motor] == -direction:
        v = pot.read_volts(motor=motor)
        print(v)
        time.sleep(0.1)

    return vm, stuck_cnt > 2


if __name__ == "__main__":

    parser = ArgumentParser(description="Calibrate potentiometers.")
    parser.add_argument(
        "-a", "--az", action="store_true", help="Calibrate azimuth pot."
    )
    parser.add_argument(
        "-e", "--el", action="store_true", help="Calibrate elevation pot."
    )
    args = parser.parse_args()

# #XXX
# motors = []
# if args.az:
#     motors.append("az")
#     motors.append("az_reverse")
# if args.el:
#     motors.append("alt")
#     motors.append("alt_reverse")
# if not motors:
#     print("Exiting...")
#     sys.exit()
#
#     #XXX
#     try:
#         pass
#     except KeyboardInterrupt:
#         print("Interrupting.")
#     finally:
#         print("Stopping.")
#         motor.stop()
#
# print(vmax)
