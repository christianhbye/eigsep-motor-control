# flake8: noqa


def serial_motor_control(self, threshold_0, threshold_1, speed_0, speed_1):
    print(
        "Attempting to reach ",
        threshold_0,
        "for threshold 0 and ",
        threshold_1,
        "for threshold 1.",
    )
    baudrate = 115200
    # port for 1st pico is "/dev/ttyACM0"
    port = "/dev/ttyACM0"
    ser = serial.Serial(port, baudrate)

    ser.dtr = False
    time.sleep(0.5)
    ser.dtr = True
    time.sleep(1)

    analog_value_0 = 0
    analog_value_1 = 0

    while True:
        if ser.in_waiting:
            analog_str = ser.readline().decode("utf-8").strip()
            try:
                a, b = analog_str.split()
                analog_value_0 = int(a)
                analog_value_1 = int(b)
                break
            except ValueError:
                print("Incomplete data received, trying again...")
                continue
    print(analog_value_0, analog_value_1)

    if threshold_0 > 52000:
        threshold_0 = 52000
    elif threshold_0 < 1000:
        threshold_0 = 1000

    if threshold_1 > 52000:
        threshold_1 = 52000
    elif threshold_1 < 1000:
        threshold_1 = 1000

    reached_0 = False
    reached_1 = False

    if abs(analog_value_0 - threshold_0) <= 100:
        print("Already at destination 0.")
        speed_0 = 0
        reached_0 = True

    if abs(analog_value_1 - threshold_1) <= 100:
        print("Already at destination 1.")
        speed_1 = 0
        reached_1 = True

    if analog_value_0 > threshold_0:
        direction_0 = 1
    elif analog_value_0 < threshold_0:
        direction_0 = 0
    if analog_value_1 > threshold_1:
        direction_1 = 1
    elif analog_value_1 < threshold_1:
        direction_1 = 0

    speed_0 = 254 if abs(speed_0) == 255 else speed_0
    speed_1 = 254 if abs(speed_1) == 255 else speed_1

    self.motor.set_drive(0, direction_0, abs(speed_0))
    self.motor.set_drive(1, direction_1, abs(speed_1))
    while True:
        if ser.in_waiting:
            try:
                analog_str = ser.readline().decode("utf-8").strip()
                a, b = analog_str.split()
                analog_value_0 = int(a)
                analog_value_1 = int(b)
                volt_value_0 = (3.3 / 65535) * analog_value_0
                volt_value_1 = (3.3 / 65535) * analog_value_1
                print(
                    "Analog Value 0: ",
                    analog_value_0,
                    " Voltage Value 0: ",
                    volt_value_0,
                    "  Analog Value 1: ",
                    analog_value_1,
                    " Voltage Value 1: ",
                    volt_value_1,
                )
                if direction_0 == 0 and reached_0 == False:
                    if analog_value_0 >= threshold_0:
                        print("Reached target 0.")
                        self.stop(0)
                        reached_0 = True
                elif direction_0 == 1 and reached_0 == False:
                    if analog_value_0 <= threshold_0:
                        print("Reached target 0.")
                        self.stop(0)
                        reached_0 = True
                if direction_1 == 0 and reached_1 == False:
                    if analog_value_1 >= threshold_1:
                        print("Reached target 1.")
                        self.stop(1)
                        reached_1 = True
                elif direction_1 == 1 and reached_1 == False:
                    if analog_value_1 <= threshold_1:
                        print("Reached target 1.")
                        self.stop(1)
                        reached_1 = True
                if reached_0 == True and reached_1 == True:
                    break
            except ValueError:
                print("Incomplete data received, trying again...")
                continue
    # self.stop(motor_id)
    time.sleep(0.5)
    reached_0 = False
    reached_1 = False

    if abs(analog_value_0 - threshold_0) <= 50:
        speed_0 = 0
        reached_0 = True

    if abs(analog_value_1 - threshold_1) <= 50:
        speed_1 = 0
        reached_1 = True

    if reached_0 == False or reached_1 == False:
        print("Correcting error.")
        direction_0 = 1 if direction_0 == 0 else 0
        direction_0 = 1 if direction_0 == 0 else 0

        self.motor.set_drive(0, direction_0, 100)
        self.motor.set_drive(1, direction_1, 100)
        while True:
            if ser.in_waiting:
                try:
                    analog_str = ser.readline().decode("utf-8").strip()
                    a, b = analog_str.split()
                    analog_value_0 = int(a)
                    analog_value_1 = int(b)
                    volt_value_0 = (3.3 / 65535) * analog_value_0
                    volt_value_1 = (3.3 / 65535) * analog_value_1
                    print(
                        "Analog Value 0: ",
                        analog_value_0,
                        " Voltage Value 0: ",
                        volt_value_0,
                        "  Analog Value 1: ",
                        analog_value_1,
                        " Voltage Value 1: ",
                        volt_value_1,
                    )
                    if direction_0 == 1 and reached_0 == False:
                        if analog_value_0 <= threshold_0:
                            print("Reached target 0.")
                            self.stop(0)
                            reached_0 == True
                    elif direction_0 == 0 and reached_0 == False:
                        if analog_value_0 >= threshold_0:
                            print("Reached target 0.")
                            self.stop(0)
                            reached_0 == True
                    if direction_1 == 1 and reached_1 == False:
                        if analog_value_1 <= threshold_1:
                            print("Reached target 1.")
                            self.stop(1)
                            reached_1 == True
                    elif direction_1 == 0 and reached_1 == False:
                        if analog_value_1 >= threshold_1:
                            print("Reached target 1.")
                            self.stop(1)
                            reached_1 == True
                    if reached_0 == True and reached_1 == True:
                        break
                except ValueError:
                    print("Incomplete data received, trying again...")
                    continue
    self.stop(0)
    self.stop(1)
    print("Done!")
    # port = "/dev/ttyACM0"
    # serial_connect(port, 'higher', 50000, 0, -255)
