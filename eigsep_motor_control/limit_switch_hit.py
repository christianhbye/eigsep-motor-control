import time


def limit_switch(motor, m, pot):
    """
    Determine if a motor has reached its limit switch based on its current direction and velocity.

    Parameters
    ----------
    motor : str
        Identifier for the motor whose limit switch status is to be checked: az or alt.
    m : object
        A motor object from the Motor class
    pot : object
        A pot object from the Potentiometer class

    Returns
    ----------
    bool
        Returns True if the motor's current direction opposes the direction logged in the potentiometer,
        indicating that the limit switch has been reached. Returns False if there is no movement, or if
        the motor direction aligns with the potentiometer direction.

    """
    direction, velocity = m.velocities[motor]
    if velocity == 0:
        return False
    if pot.direction[motor] == 0:
        return False
    return pot.direction[motor] != direction

def reverse_limit(m, pot, limits):
    """
    Check and handle the limit switch status for motors. This function checks whether
    each motor specified in the sequence has reached its limit switch and manages
    the motor actions accordingly.

    Parameters
    ----------
    m : object
        A motor object from the Motor class
    pot : object
        A pot object from the Potentiometer class
    limits : list
        A list of event objects for each motor.

    Returns
    ----------
    limits : list
        The updated list of limit events after processing each motor.
        
    """
    for motor, limit in zip(["az", "alt"], limits):
        if limit_switch(motor, m, pot) and not limit.is_set():
            print(f"{motor}: Limit switch reached, setting event")
            limit.set()
        elif not limit_switch(motor, m, pot) and limit.is_set():
            # If the limit switch is no longer triggered but the event is set, reverse the motor.
            m.reverse(motor)
            time.sleep(1)  # XXX
            limit.clear()
            while limit_switch(motor, m, pot):
                # Continue checking if the limit is still active to ensure pot.direction is updated correctly.
                continue
    return limits
