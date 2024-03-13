from machine import ADC, Pin, UART
import struct
from time import sleep

led = Pin(25, Pin.OUT)

ADC_PIN1 = 27
ADC_PIN2 = 28
BAUDRATE = 115200
INT_LEN = 10  # number of readings to average
SLEEP = 0.05  # seconds between readings

adc1 = ADC(Pin(ADC_PIN1))  # azimuth
adc2 = ADC(Pin(ADC_PIN2))  # altitude
uart = UART(0)
uart.init(baudrate=BAUDRATE)

while True:
    value1 = 0
    value2 = 0
    for cnt in range(INT_LEN):
        value1 += adc1.read_u16()
        value2 += adc2.read_u16()
        sleep(SLEEP)
    data = struct.pack("<ii", value1, value2)
    uart.write(data)
    led.toggle()