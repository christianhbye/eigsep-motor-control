from machine import ADC, Pin
from time import sleep

adc1 = ADC(Pin(27))
adc2 = ADC(Pin(28))
uart = machine.UART(0, baudrate = 115200)
count1 = 0
count2 = 0
value1 = 0
value2 = 0
placeholder1 = 0
placeholder2 = 0

while True:
    value1 += adc1.read_u16()
    value2 += adc2.read_u16()
    count1 += 1
    count2 += 1
    if count1 >= 10:
        placeholder1 = (int(value1/count1))
        value1 = 0
        count1 = 0
    if count2 >= 10:
        placeholder2 = (int(value2/count2))
        value2 = 0
        count2 = 0
    print(placeholder1, placeholder2)
    sleep(0.05)
