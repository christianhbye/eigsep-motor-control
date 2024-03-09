from motor import Motor
from time import sleep

AZ_VEL = 254
ALT_VEL = 0

m = Motor(n_motors=2)
m.start(0, AZ_VEL, float("inf"))
m.start(1, ALT_VEL, float("inf"))

try:
    while True:
        print("...")
        sleep(1)
except KeyboardInterrupt:
    print("stopping")
    m.stop(0)
    m.stop(1)
