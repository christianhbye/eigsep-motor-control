from argparse import ArgumentParser
import sys
import time
import numpy as np
import eigsep_motor_control as emc

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
    
    #pot.reset_volt_readings()
    #time.sleep(3)
    #print(pot.direction[motor], az_dir)   
    if pot.direction[motor] == az_dir:
        return False
    if pot.direction[motor] != az_dir:
        return True

def reverse_limit(m, pot, limits):
    new_limits = [limits[0], limits[1]]
    #print(limit_switch("az", m, pot))
    if limit_switch("az", m, pot) and not new_limits[0].is_set():
        print("Setting event")
        new_limits[0].set()
    elif not limit_switch("az", m, pot) and new_limits[0].is_set():
        m.reverse("az")
        time.sleep(10)
        new_limits[0].clear()
    print(new_limits[0].is_set())    

    if limit_switch("alt", m, pot) and not new_limit[1].is_set():
        new_limits[1].set()
    elif not limit_switch("alt", m, pot) and new_limits[1].is_set():
        m.reverse("alt")
        time.sleep(1)
        new_limits[1].clear()

    return new_limits
