from machine import ADC, Pin
from time import sleep

adc = ADC(Pin(26))
uart = machine.UART(0, baudrate = 921600)
count = 0
value = 0

while True:
    value += adc.read_u16()
    count += 1
    if count >= 10:
        print(int(value/count))
        value = 0
        count = 0
    sleep(0.05)
