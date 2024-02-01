from machine import ADC, Pin
from time import sleep
import sys

adc = ADC(Pin(26))
uart = machine.UART(0, baudrate = 460800)

while True:
    value = adc.read_u16()
    #print("Analog value is: ", value, ", Volt value is: ",(3.3/65535)*value)
    print(value)
    #sys.stdout.flush()
    sleep(1)