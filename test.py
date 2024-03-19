from motor import Motor
from time import sleep

m = Motor(n_motors=2)
m.start(0, -254, float("inf"))
m.start(1, -254, float("inf"))

try:
    while True:
        print("...")
        sleep(1)
except KeyboardInterrupt:
    print("stopping")
    m.stop(0)
    m.stop(1)
