import time


def limit_switch(motor, m, pot):

    az_vel = 0
    alt_vel = 0

    if motor == "az":
        az_dir, az_vel = m.velocities["az"]
    elif motor == "alt":
        alt_dir, alt_vel = m.velocities["alt"]
    else:
        raise ValueError("Invalid motor.")

    if az_vel == 0 & alt_vel == 0:
        return False
    
    if motor == "az":
        if pot.direction[motor] == az_dir:
            return False
        if pot.direction[motor] != az_dir:
            return True
    if motor == "alt":
        if pot.direction[motor] == alt_dir:
            return False
        if pot.direction[motor] != alt_dir:
            return True
        
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
