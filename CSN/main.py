import RPi.GPIO as GPIO
import time
import multiprocessing

distance = 50

# PINS
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(4, GPIO.IN)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.output(18, GPIO.LOW)
GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.LOW)
GPIO.output(25, GPIO.LOW)
GPIO.output(26, GPIO.HIGH)
GPIO.output(19, GPIO.LOW)
GPIO.output(17, False)

# Invoer Code (Zwart:1 Groen:2 Blauw:3 Geel:4)
code = [1, 2, 2, 1]


# Functie Code intypen
def press(code):
    list = []
    code_inp = 0
    while True:
        while code_inp < 4:
            if GPIO.input(12) == 0:
                list += [1]
                time.sleep(0.5)
                code_inp += 1
            elif GPIO.input(16) == 0:
                list += [2]
                time.sleep(0.5)
                code_inp += 1
            elif GPIO.input(20) == 0:
                list += [3]
                time.sleep(0.5)
                code_inp += 1
            elif GPIO.input(21) == 0:
                list += [4]
                time.sleep(0.5)
                code_inp += 1
            if len(list) == 1:
                GPIO.output(18, GPIO.HIGH)
            elif len(list) == 2:
                GPIO.output(23, GPIO.HIGH)
            elif len(list) == 3:
                GPIO.output(24, GPIO.HIGH)
            elif len(list) == 4:
                GPIO.output(25, GPIO.HIGH)
                time.sleep(0.5)
        if list == code:
            GPIO.output(18, GPIO.LOW)
            GPIO.output(23, GPIO.LOW)
            GPIO.output(24, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
            return True
        elif list == [4, 4, 4, 4]:
            GPIO.cleanup()
            exit()
        else:
            code_inp = 0
            list = []
            GPIO.output(18, GPIO.LOW)
            GPIO.output(23, GPIO.LOW)
            GPIO.output(24, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
        if GPIO.input(19) == 1:
            GPIO.output(19, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(19, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(19, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(19, GPIO.HIGH)
            time.sleep(0.5)
        else:
            GPIO.output(19, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(19, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(19, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(19, GPIO.LOW)
            time.sleep(0.5)


def dis():
    distance = 0.5
    while distance >= 0.5:
        time.sleep(0.1)
        GPIO.output(17, True)
        time.sleep(0.00001)
        GPIO.output(17, False)
        while GPIO.input(4) == 0:
            pulse_start = time.time()
        while GPIO.input(4) == 1:
            pulse_end = time.time()
        distance = (pulse_end - pulse_start) * 171.50
        print
        round(distance, 2)
    else:
        while True:
            GPIO.output(19, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(19, GPIO.HIGH)
            time.sleep(0.5)

        #


while True:
    if press(code) == True and GPIO.input(26) == 1:
        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH)
        p2 = multiprocessing.Process(target=dis)
        p2.start()
    else:
        GPIO.output(19, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        p2.terminate()