from machine import ADC, Pin, UART
import struct
from time import sleep

ADC_PIN1 = 27
ADC_PIN2 = 28
BAUDRATE = 115200
INT_LEN = 10  # number of readings to average
SLEEP = 0.05  # seconds between readings

adc1 = ADC(Pin(ADC_PIN1))
adc2 = ADC(Pin(ADC_PIN2))
uart = UART(0)
uart.init(baudrate=BAUDRATE)

while True:
    cnt = 0
    value1 = 0
    value2 = 0
    while cnt < INT_LEN:
        value1 += adc1.read_u16()
        value2 += adc2.read_u16()
        sleep(SLEEP)
    data = struct.pack("<ff", value1 / INT_LEN, value2 / INT_LEN)
    uart.write(data)
