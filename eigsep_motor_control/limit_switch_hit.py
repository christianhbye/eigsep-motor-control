import time


def limit_switch(motor, m, pot):

    direction, velocity = m.velocities[motor]
    if velocity == 0:
        return False

    return pot.direction[motor] != direction


def reverse_limit(m, pot, limits):
    # print(limit_switch("az", m, pot))
    for motor, limit in zip(["az", "alt"], limits):
        if limit_switch(motor, m, pot) and not limit.is_set():
            print(f"Setting event for {motor}")
            limit.set()
        elif not limit_switch(motor, m, pot) and limit.is_set():
            m.reverse(motor)
            time.sleep(1)  # XXX
            limit.clear()
            while limit_switch(motor, m, pot):
                continue
    return limits
