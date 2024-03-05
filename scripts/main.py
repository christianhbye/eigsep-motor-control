from machine import ADC, Pin, UART
from time import sleep

ADC_PIN1 = 27
ADC_PIN2 = 28
BAUDRATE = 115200
INT_LEN = 10  # number of readings to average
SLEEP = 0.05  # seconds between readings

adc1 = ADC(Pin(ADC_PIN1))
adc2 = ADC(Pin(ADC_PIN2))
uart = UART(0, baudrate=BAUDRATE)  # XXX is this necessary?
#uart.init?

while True:
    cnt = 0
    value1 = 0
    value2 = 0
    while cnt < INT_LEN:
        value1 += adc1.read_u16()
        value2 += adc2.read_u16()
        sleep(SLEEP)
    print(value1 / INT_LEN, value2 / INT_LEN)