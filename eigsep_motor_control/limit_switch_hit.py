import time


def limit_switch(motor, m, pot):
    """
    Function to check if the limit switch has been hit.
    """
    direction, velocity = m.velocities[motor]
    if velocity == 0:
        return False

    return pot.direction[motor] != direction


def reverse_limit(m, pot, limits):
    # print(limit_switch("az", m, pot))
    for motor, limit in zip(["az", "alt"], limits):
        if limit_switch(motor, m, pot) and not limit.is_set():
            print(f"{motor}: Limit switch reached, setting event")
            limit.set()
        elif not limit_switch(motor, m, pot) and limit.is_set():
            # limit is released, can safely revere motor
            m.reverse(motor)
            time.sleep(1)  # XXX
            limit.clear()
            while limit_switch(motor, m, pot):
                continue
    return limits
