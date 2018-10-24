import RPi.GPIO as GPIO
import time
import multiprocessing
from urllib.request import urlopen
hostname='192.168.1.10:5000'





# PINS Setup
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

# PINS Begin output
GPIO.output(18, GPIO.LOW)
GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.LOW)
GPIO.output(25, GPIO.LOW)
GPIO.output(26, GPIO.HIGH)
GPIO.output(19, GPIO.LOW)
GPIO.output(17, False)

# De 4 kleuren code voor het alarm (Zwart:1 Groen:2 Blauw:3 Geel:4)
code = [1, 2, 2, 1]

# While loop voor ledje laten knipperen
def zoeken():
    while True:
        GPIO.output(26, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(26, GPIO.LOW)
        time.sleep(0.5)

#Verbinding maken met de server (Andere pi)
def httpconnect(action):
    url='http://{}/{}'.format(hostname,action)
    #Proberen te verbinden en groen ledje laten branden (Teken va verbinding)
    try:
    #Pi's kunnen niet verbinden en probeert het een seconde later weer tot dat er verbinding is
        print(urlopen(url).read().decode())
        led.terminate()
    except:
        time.sleep(1)
        httpconnect("")


#Multi proccesing ledje knipperen en zoeken naar andere pi
led = multiprocessing.Process(target=zoeken)
led.start()

httpconnect('')




# Functie kleuren code intypen
def press(code):
    list = []
    code_inp = 0
    while True:
        #Er word een lijst gemaakt van de 4 knoppen die worden ingedrukt
        while code_inp < 4:
            if GPIO.input(12) == 0:
                list += [1]
                #Wacht 0,5 seconden voor bounce button
                time.sleep(0.5)
                #Als er een knop in gedrukt word word code_inp een maar zodat die de waarde heeft voor hoeveel knoppen er al zijn ingedrukt
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
            #Laat de aantal ledjes branden als aantal knoppen die zijn ingedrukt
            if len(list) == 1:
                GPIO.output(18, GPIO.HIGH)
            elif len(list) == 2:
                GPIO.output(23, GPIO.HIGH)
            elif len(list) == 3:
                GPIO.output(24, GPIO.HIGH)
            elif len(list) == 4:
                GPIO.output(25, GPIO.HIGH)
                time.sleep(0.5)
        #Kijkt of de lijst (Ingedrukte code) gelijk is aan de goede kleuren code. Zet alle ledjes uit en functie returnt True
        if list == code:
            GPIO.output(18, GPIO.LOW)
            GPIO.output(23, GPIO.LOW)
            GPIO.output(24, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
            return True
        #Als de code vier keer geel is ingedrukt word het programma stop gezet
        elif list == [4, 4, 4, 4]:
            GPIO.cleanup()
            httpconnect('off')
            exit()
        #Als de verkeerde code is ingedrukt gaan alle 4 de ledjes uit en gaat een rood ledje twee keer knipperen
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

#Functie die de afstand bepaalt vanaf de sensor
def dis():
    distance = 1
    while distance >= 1:
        # Als distance groter is dan 1 meter rekent hij opnieuw de afstand uit.
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
        # Als distance kleiner is dan 1 meter geeftie een signaal naar de andere pi (Die laat het speakertje afgaan) en rood ledje blijft knipperen
        httpconnect('on')
        while True:
            GPIO.output(19, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(19, GPIO.HIGH)
            time.sleep(0.5)



#Laat het programmetje altijd lopen
while True:
    #Laat functie press runnen en vraagt of de goede code is ingevult. Als het groene ledje brand en goede code is ingevuld laatie het rode ledje branden en start de functie dis als multiprocces
    # Alarm staat uit en zet het alarm erop
    if press(code) == True and GPIO.input(26) == 1:
        GPIO.output(26, GPIO.LOW)
        GPIO.output(19, GPIO.HIGH)
        p2 = multiprocessing.Process(target=dis)
        p2.start()
    else:
    #Als goede code is ingevult en het rode lampje brand laat hij het groene ledje branden en geeftie een signaal naar de andere pi dat het speakertje moet stoppen.
    #Alarm staat aan en zet het alarm uit
        GPIO.output(19, GPIO.LOW)
        GPIO.output(26, GPIO.HIGH)
        httpconnect('off')
        p2.terminate()