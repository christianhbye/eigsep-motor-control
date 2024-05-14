from argparse import ArgumentParser
import logging
import numpy as np
import time
import eigsep_motor_control as emc


def calibrate(motor, m, direction):
    """
    Calibrate the potentiometer corresponding to the motor.

    Parameters
    ----------
    motor : str
        Name of motor to calibrate. Either 'az' or 'alt'.
    m : Motor
        Instance of the emc.Motor class.
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
    pot = emc.Potentiometer()
    pot.reset_volt_readings()

    if direction == -1:
        vel = m.MIN_SPEED
    elif direction == 1:
        vel = m.MAX_SPEED
    else:
        raise ValueError("Invalid direction, must be -1 or 1.")
    if motor == "az":
        az_vel = vel
        alt_vel = 0
    elif motor == "alt":
        az_vel = 0
        alt_vel = vel
    else:
        raise ValueError("Invalid motor, must be ``az'' or ``alt''.")
    m.start(az_vel=az_vel, alt_vel=alt_vel)

    # loops until the switch is triggered
    m.logger.info("Attack mode.")
    try:
        while pot.direction[motor] == direction:
            v = pot.read_volts(motor=motor)
            m.logger.info(f"{v=}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        m.logger.warning("Interrupting.")
        m.stop()
    # get the extremum pot voltage (max if forward, min if reverse)
    vm = np.max(np.abs(pot.volts[:, emc.motor.MOTOR_ID[motor]]))

    # now: either the pot is stuck or the switch is triggered
    # this loops runs as long as the pot is stuck
    tol = 0.01  # XXX arbitrary threshold for pot being stuck
    stuck_cnt = np.count_nonzero(np.abs(pot.vdiff[motor]) < tol)
    try:
        while np.abs(pot.vdiff[motor])[-1] < tol:
            v = pot.read_volts(motor=motor)
            m.logger.info(f"{v=}")
            stuck_cnt += 1
            time.sleep(0.1)
        m.logger.info("Reverse until switch is released.")
        while pot.direction[motor] == -direction:
            v = pot.read_volts(motor=motor)
            m.logger.info(f"{v=}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        m.logger.warning("Interrupting.")
        m.stop()

    m.stop()
    return vm, stuck_cnt > 2


if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    parser = ArgumentParser(description="Calibrate potentiometers.")
    parser.add_argument(
        "-b",
        "--board",
        type=str,
        default="pololu",
        help="Motor board to use: ``pololu'' (default) or ``qwiic''.",
    )
    parser.add_argument(
        "-a", "--az", action="store_true", help="Calibrate azimuth pot."
    )
    parser.add_argument(
        "-e", "--el", action="store_true", help="Calibrate elevation pot."
    )
    args = parser.parse_args()

    motors = []
    if args.az:
        motors.append("az")
    if args.el:
        motors.append("alt")
    if not motors:
        raise ValueError("At least one motor must be selected.")

    if args.board == "pololu":
        m = emc.PololuMotor(logger=logger)
    elif args.board == "qwiic":
        m = emc.QwiicMotor(logger=logger)
    else:
        raise ValueError("Invalid board, must be ``pololu'' or ``qwiic''.")

    for motor in motors:
        logger.info(f"Calibrating {motor} potentiometer.")
        vm, stuck = calibrate(motor, m, 1)
        logger.info(f"Max voltage: {vm}")
        logger.info(f"Stuck: {stuck} \n")
        if not stuck:
            logger.info("Didn't get pot stuck, calibrate opposite direction.")
            vm, stuck = calibrate(motor, m, -1)
            logger.info(f"Min voltage: {vm}")
            logger.info(f"Stuck: {stuck} \n")
        else:
            logger.info("Pot was stuck, not calibrating opposite direction.")
