import hid

gamepad = hid.device()
gamepad.open(0x2E8A, 0x010A)
gamepad.set_nonblocking(True)
previous_state = 0
while True:
    report = gamepad.read(64)
    if report:
        pressed = report[8:-3]
        if pressed[0] == 1 and previous_state == 0:
            print("Button 1 pressed")
        previous_state = pressed[0]
