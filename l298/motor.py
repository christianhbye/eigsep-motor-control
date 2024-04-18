import time
from RPi import GPIO

# motor driver to GPIO pin map
IN1 = 23
IN2 = 24

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([IN1, IN2], GPIO.OUT)
    GPIO.output(23, 0)
    GPIO.output(24, 1)
    while True:
        try:
            print("...")
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    GPIO.cleanup()
