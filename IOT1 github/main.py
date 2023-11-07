### IMPORTS ###
from imu import MPU6050  #Her importer vi MPU fra modulet IMU.
from time import sleep #Importere sleep fra time modulet, så vi kan bruge sleep()
from machine import Pin, I2C, ADC, UART #Importere klassen Pin fra machine modulet, så vi kan bruge pins fra vores esp32
from neopixel import NeoPixel #Importere klassen Neopixel fra modulet neopixel, så vi kan bruge led ringen
import _thread #Importere multithreading modulet, så vi kan køre flere loops på samme tid.
import umqtt_robust2 as mqtt #importere mqtt modulet, så vi kan kommunikere med adafruit
from gps_bare_minimum import GPS_Minimum #Importere klassen GPS_minimum fra modulet gps_bare_minimum

#### Variables and predefines #### 
# gps # ####NICKY!!!!!
gps_port = 2 
gps_speed = 9600
uart = UART(gps_port, gps_speed)
gps = GPS_Minimum(uart)

# IMU # #####VICTOR!!!!
i2c = I2C(0)
imu = MPU6050(i2c)

# Tackling tracking #
tackling_list = [] #Definere tackling_list til en liste
tacklinger = 0 #Definere en variabel ved navnet tacklinger der starter ved 0

# Battery #
Battery_procent = 100 #Laver variabel hvor Battery_procent = 100
batpin = 34 #Definere batpin til esp pin nummer 34.
Max = 2400 #Definere max værdien for input ved max batterispænding
Min = 1680 #Definere min værdien for input ved min batterispænding
MaxMin = Max - Min #Definere MaxMin ved at finde differencen mellem minimum og maximum
MaxMinPct = MaxMin / 100 #differencen divideres med 100, så ved hvad 1% er af input værdien
battery = ADC(Pin(batpin),atten=3) #Definere hvilken pin battery funktionen skal bruge, og klassen ADC.  ###hvad er atten=3

# Button #
knap = Pin(26, Pin.IN, Pin.PULL_UP) #Definere knap, så det er sat til pin 26 ESP32 med argumenten Pin.PULL_UP. ###Tjek Pin.PULL_UP

# Neopixel #
n = 12 # Definere antallet af pixels på neopixe ringen
p = 27 #Definere hvilken Pin neopixel ringen er tisluttet på ESP32
np = NeoPixel(Pin(p, Pin.OUT), n) #Definere np som Neopixel funktionen, så den bruger pin 27 med output
sleep_tid_neopixel = 0.2 #definere en varibal, så neopixels hastighed er lig 0.2sec

# Vibration motor #
buzpin = 25 #Definere Buzpin, så den er tilsluttet Pin 25 på esp32
buz = Pin(buzpin, Pin.OUT) #Definere buz som Pin funktionen, så den bruger Pin 25 med output.

#### Functions ###
def clear(): #definere en clear funktion, så vi kan slukke neopixel ringen
    for i in range(n): # Laver et for loop for neopixelringen
         np[i] = (0, 0, 0) #Definere NP[i] værdien til (0,0,0) fordi vi vil skulle led ringen.
         np.write() #Bruges til at starte neopixel ringen.

def NeoKnap(): #Definere en knap til neopixel
    first = knap.value() #definere funktion first med knap.value()
    sleep(0.01) #indsætter en sleep funktion
    second = knap.value() #Definere nr. 2 funktion second med knap.value()
    if first == 1 and second == 0: #Laver en if condition, hvor vis_tacklinger() bliver sat i gang hvis first == 1 og second == 0, altså hvis knappen bliver trykket ned.
        vis_tacklinger() #eksekverer vis_tacklinger

def vis_tacklinger(): #Definere funktionen vis_tacklingere()
    clear() #slukker neopixel
    tackl1 = tacklinger #Definere variablen tacklinger
    if tacklinger > 12: #Laver en if condition hvor tackling er større 12
        tackl1 = 12 #definerer variablen tackl1
        tackl2 = tacklinger - 12 #definerer variablen tackl2 med tacklinger
        print(f'tackl1: {tackl1}') #printer funktion tackl1, så vi holde øje med hvor mange tacklinger der er i shell.
        if tacklinger > 24: #Gentager tidligere if condition med 24 istedet for 12
            tackl2 = 12
            tackl3 = tacklinger - 24
            print(f'tackl2: {tackl2}')
            if tacklinger > 36:
                tackl3 = 12
                tackl4 = tacklinger - 36
                print(f'tackl3: {tackl3}')
                if tacklinger > 48:
                    tackl4 = 12
                    tackl5 = tacklinger - 48
                    print(f'tackl4: {tackl4}')
                    print(f'tackl5: {tackl5}')
    print(f'Antal tacklinger: {tacklinger}')
    for pixels in range(tackl1): #Laver et for loop der sammenkopler neopixel og antal tacklinger.
        np[pixels] = (20, 0, 0) # Definere Neopixel, så der bliver lyst rødt så længe vi er på variablen tackl1
        np.write() #Køre neopixel
        sleep(sleep_tid_neopixel) #Bruger den tidligere sleep variablen der var 0.2sec
    if tacklinger > 12: #if condition hvis tackling antal er større end 12
        for pixels in range(tackl2): #For loop for tackl2
            np[pixels] = (3, 17, 0) #skifter farve hvis tacklinger er over 12
            np.write() #køre program
            sleep(sleep_tid_neopixel) #Samme som i linke 86
    if tacklinger > 24: #If condition hvis mængden af tacklinger er større end 24
        for pixels in range(tackl3):
            np[pixels] = (0, 6, 14)
            np.write()
            sleep(sleep_tid_neopixel)
    if tacklinger > 36:
        for pixels in range(tackl4):
            np[pixels] = (5, 0, 15)
            np.write()
            sleep(sleep_tid_neopixel)
    if tacklinger > 48:
        for pixels in range(tackl5):
            np[pixels] = (7, 13, 0)
            np.write()
            sleep(sleep_tid_neopixel)
    sleep(7) #Sørger for at led ikke slukker inden vi har set hvor mange tacklinger der er
    clear() #Clear slukker neopixel
    Neobat() #Kører funktionen Neobat
    

def detect_tackling(): #Definere detect_tackling():
    acceleration = imu.accel #Definere variablen acceleration fra imu.
    sleep(0.1) #sover 0.1 sek
    if acceleration.x < 0.6: #If condition hvis accelaration på x aksen for imu er mindre end 0.6
        sleep(1) #sover 1sek, så der ikke sker to tacklinger på en gang
        if acceleration.x > 0.6: #if condition for acceleration hvis x aksen på imu er større end 0.6
            global tacklinger #gør tacklinger globalt, så vi kan bruge funktionen i hele programmet
            tacklinger = tacklinger + 1 # plusser tacklinger med 1, så hver gang en tackling bliver registreret lægger den 1 til det totalte antal.
            print(f'tacklinger: {tacklinger}') #printer antal tacklinger i shell

def get_adafruit_gps(): #####NICKYYYYY!!!!:DDD
    speed = lat = lon = None 
    if gps.receive_nmea_data():
        if gps.get_speed() != -999 and gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            speed =str(gps.get_speed())
            lat = str(gps.get_latitude())
            lon = str(gps.get_longitude())
            return speed + "," + lat + "," + lon + "," + "0.0"
        else: 
            print(f"GPS data to adafruit not valid")
            return False
    else:
        return False


def set_color(r, g, b): #Definerer set_color, så vi kan styre farverne på neopixel ringen
    for pixels in range(n): #Laver et for loop med neopixel
        np[pixels] = (r, g, b) #Definere neopixel med (r, g, b)
        np.write() #Starter neopixel

def clear_np(): #Definerer en clear funktion
    set_color(0, 0, 0) #Slukker neopixel ringen

def Neobat(): #Definere Neobat, så vi kan vise batteri kapacitet/procent.
    bat_procent_12 = Battery_procent / 8.33 #Dividere 12med 100, så vi får 8.33# på hver pixel, da der er 12 pixels på en neopixel ring
    print(int(bat_procent_12)) #Printer batteriprocent som en integer
    if int(bat_procent_12) < 3: #Laver en if condtion, hvis færre end tre neopixels lyser.
        for pixels in range(int(bat_procent_12)): # Laver et for loop med batteriprocent
            np[pixels] = (40, 0, 0) #Sætter 2 eller færre neopixel  til farven rød hvis if er sandt.
            np.write() #Starter neopixel
            sleep(0.001) #Sover i 0.001 sek
    elif int(bat_procent_12) < 6: #laver en elif, så den bliver kørt hvis færre end 6 neopixel lyser. Kører integer, så der ikke er decimal tal.
        for pixels in range(int(bat_procent_12)): samme som linje149
            np[pixels] = (20, 20, 0)
            np.write()
            sleep(0.001)
    else:
        for pixels in range(int(bat_procent_12)): #laver en else funktion, hvis intet af det ovenstående er sandt, vil neopixels farve være grønt.
            np[pixels] = (0, 40, 0)
            np.write()
            sleep(0.001)

def show_battery(): #Definere showbattery, så vi kan aktivere buzzeren under et bestemt batterikapacitet.
    clear() #Slukker neopixel
    if Battery_procent < 6: #Laver en if condition, der starter hvis batteriprocenten er under 6%
        for i in range(10): #laver et for loop, så buzzeren kører 10 gange hvis batteriprocenten er under 6&
            buz.on() #Starter buzzeren
            set_color(40, 0, 0) #Den farve neopixel skal lyse på alle 12 led'er hvis buzzeren starter
            sleep(0.5) #Sover et halvt sekund
            buz.off() #Slukker buzzeren
            clear() #Slukker neopixel
            sleep(0.5) #Sover et halv sekund
    elif Battery_procent < 11: #Laver en elif condtion hvis batteriprocenten er under 11%
        for i in range(6): #laver et for loop, så buzzeren kører 6 gange hvis elif er sandt
            buz.on() #Start buzzer
            set_color(20, 20, 0) #Sætter neopixel farve
            sleep(0.5) # sover halvt sekund
            buz.off()  #Slukker buzzeren
            clear() #Slukker neopixel ringen
            sleep(0.5) #sover halv sekund
    Neobat() #Starter neobat

def battery_procent(battery): #Definerer batteryprocent med argumentet battery
    global Battery_procent #Laver battery_procent global så vi kan bruge det i hele programmet
    battery_val = battery.read() # Laver en funktion ved navn batter_val
    Battery_max = MaxMinPct  #Laver en variabel  ved navn Battery_max
    Bat2 = battery_val - Min #Laver en variablen ved navn batter_val
    Battery_procent =  Bat2 / Battery_max #Laver variablen battery_procent

def batadafruit(Battery_procent): #Definerer batadafruit med argumentet Battery_procent
    try:
        mqtt.web_print(int(Battery_procent), 'Studiegruppe2/feeds/batteri') #Sender batteriprocent til adafruit feeded
        print('Battery Data sent to adafruit') #Printer i shell
    except:
        pass #gå videre hvis try ikke virker
        
#### Define Threads ####

def thread1(thread_id): #definerer hvad thread1 skal gøre, i dette tilfælde køres detect_tackling funktionen
    while True:
        detect_tackling()

def thread2(thread_id): #definerer hvad thread1 skal gøre, i dette tilfælde køres neolnap funktionen
    while True:
        NeoKnap()

def thread3(thread_id): ####malthefar os alle:D
    while True:
        try:
            gps_data = get_adafruit_gps()
            if gps_data:
                mqtt.web_print(gps_data, 'Studiegruppe2/feeds/gps/csv')                     
            sleep(1)
            if len(mqtt.besked) != 0:
                mqtt.besked = ""            
            mqtt.sync_with_adafruitIO()            
        except:
            pass

def thread4(thread_id, battery): #definerer hvad thread1 skal gøre, i dette tilfælde køres battery_procent først, så der kan sendes data til adafruit. 
    while True:
        battery_procent(battery)
        batadafruit(Battery_procent)
        sleep(28)
        
def thread5(thread_id):  #definerer hvad thread1 skal gøre, i dette tilfælde køres show_battery funktion og sover 2minutter
    while True:
        show_battery()
        sleep(120)
        
#### Start Threads ####

try: #forsøger at køre threads
    thread_id = 1 #definerer variablen thread id
    _thread.start_new_thread(thread1, (thread_id,)) #Her startes thread1
    
    thread_id = 2
    _thread.start_new_thread(thread2, (thread_id,))

    thread_id = 3
    _thread.start_new_thread(thread3, (thread_id,))

    thread_id = 4
    _thread.start_new_thread(thread4, (thread_id, battery))
    
    thread_id = 5
    _thread.start_new_thread(thread5, (thread_id,))
    
except: #Hvis try ikke går igennem
    print("Error: Unable to start the thread") #Printes i shell
