from machine import ADC, Pin
from time import sleep

led = Pin(25, Pin.OUT)

ADC_PIN1 = 27
ADC_PIN2 = 28
BAUDRATE = 115200
INT_LEN = 10  # number of readings to average
SLEEP = 0.05  # seconds between readings

adc1 = ADC(Pin(ADC_PIN1))  # azimuth
adc2 = ADC(Pin(ADC_PIN2))  # altitude

while True:
    value1 = 0
    value2 = 0
    for cnt in range(INT_LEN):
        value1 += adc1.read_u16()
        value2 += adc2.read_u16()
    print(value1, value2)
    led.toggle()
    sleep(SLEEP)
