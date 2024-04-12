from argparse import ArgumentParser
import sys
import time
import numpy as np
import eigsep_motor_control as emc

def limit_switch(motor, m,  pot):
    
    az_vel = 0
    alt_vel = 0    
    
    if motor == "az":
        az_dir, az_vel = m.velocities[0]
    elif motor == "alt":
        alt_dir, alt_vel = m.velocities[1]
    else:
        raise ValueError("Invalid motor.")
    
    if az_vel == 0 & alt_vel == 0:
        return False
       
    if pot.direction[motor] == az_dir:
        return False
    if pot.direction[motor] != az_dir:
        return True

def reverse_limit(m, pot, limits):
    
    if limit_switch("az", m, pot) == True:
        limits[0].set
    elif limit_switch("az", m, pot) == False and limits[0].is_set():
        m.reverse("az")
        time.sleep(1)
        limits[0].clear()

    if limit_switch("alt", m, pot) == True:
        limits[1].set
    elif limit_switch("alt", m, pot) == False and limits[1].is_set():
        m.reverse("alt")
        time.sleep(1)
        limits[1].clear()