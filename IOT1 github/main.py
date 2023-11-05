### IMPORTS ###
from imu import MPU6050  
from time import sleep
from machine import Pin, I2C, ADC, UART
from neopixel import NeoPixel
import _thread
import umqtt_robust2 as mqtt
from gps_bare_minimum import GPS_Minimum

#### Variables and predefines ####
# gps #
gps_port = 2
gps_speed = 9600
uart = UART(gps_port, gps_speed)
gps = GPS_Minimum(uart)

# IMU #
i2c = I2C(0)
imu = MPU6050(i2c)

# Tackling tracking #
tackling_list = []
tacklinger = 0

# Battery #
Battery_procent = 100
batpin = 34
Max = 2400
Min = 1680
MaxInputVolt = 3.3
MaxMin = Max - Min
MaxMinPct = MaxMin / 100
OneVolt = Max / MaxInputVolt
battery = ADC(Pin(batpin),atten=3)

# Button #
knap = Pin(26, Pin.IN, Pin.PULL_UP)

# Neopixel #
n = 12
p = 27
np = NeoPixel(Pin(p, Pin.OUT), n)
sleep_tid_neopixel = 0.2

# Vibration motor #
buzpin = 25
buz = Pin(buzpin, Pin.OUT)

#### Functions ###
def clear():
    for i in range(n):
         np[i] = (0, 0, 0)
         np.write()

def NeoKnap():
    first = knap.value()
    sleep(0.01)
    second = knap.value()
    if first == 1 and second == 0:
        vis_tacklinger()

def vis_tacklinger():
    clear()
    tackl1 = tacklinger
    if tacklinger > 12:
        tackl1 = 12
        tackl2 = tacklinger - 12
        print(f'tackl1: {tackl1}')
        if tacklinger > 24:
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
    for pixels in range(tackl1):
        np[pixels] = (20, 0, 0)
        np.write()
        sleep(sleep_tid_neopixel)
    if tacklinger > 12:
        for pixels in range(tackl2):
            np[pixels] = (3, 17, 0)
            np.write()
            sleep(sleep_tid_neopixel)
    if tacklinger > 24:
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
    sleep(7)
    clear()
    Neobat()
    

def detect_tackling():
    acceleration = imu.accel
    sleep(0.1)
    if acceleration.x < 0.6:
        sleep(1)
        if acceleration.x > 0.6:
            global tacklinger
            tacklinger = tacklinger + 1
            print(f'tacklinger: {tacklinger}')

def get_adafruit_gps():
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


def set_color(r, g, b):
    for pixels in range(n):
        np[pixels] = (r, g, b)
        np.write()

def clear_np():
    set_color(0, 0, 0)

def Neobat():
    bat_procent_12 = Battery_procent / 8.33
    print(int(bat_procent_12))
    if int(bat_procent_12) < 3:
        for pixels in range(int(bat_procent_12)):
            np[pixels] = (40, 0, 0)
            np.write()
            sleep(0.001)
    elif int(bat_procent_12) < 6:
        for pixels in range(int(bat_procent_12)):
            np[pixels] = (20, 20, 0)
            np.write()
            sleep(0.001)
    else:
        for pixels in range(int(bat_procent_12)):
            np[pixels] = (0, 40, 0)
            np.write()
            sleep(0.001)

def show_battery():
    clear()
    if Battery_procent < 6:
        for i in range(10):
            buz.on()
            set_color(40, 0, 0)
            sleep(0.5)
            buz.off()
            clear()
            sleep(0.5)
    elif Battery_procent < 11:
        for i in range(6):
            buz.on()
            set_color(20, 20, 0)
            sleep(0.5)
            buz.off() 
            clear()
            sleep(0.5)
    Neobat()

def battery_procent(battery):
    global Battery_procent
    battery_val = battery.read()
    Battery_max = MaxMinPct
    Bat2 = battery_val - Min
    Battery_procent =  Bat2 / Battery_max

def batadafruit(Battery_procent):
    try:
        mqtt.web_print(int(Battery_procent), 'Studiegruppe2/feeds/batteri')
        print('Battery Data sent to adafruit')
    except:
        pass
        
#### Define Threads ####

def thread1(thread_id):
    while True:
        detect_tackling()

def thread2(thread_id):
    while True:
        NeoKnap()

def thread3(thread_id):
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

def thread4(thread_id, battery):
    while True:
        battery_procent(battery)
        batadafruit(Battery_procent)
        sleep(28)
        
def thread5(thread_id):
    while True:
        show_battery()
        sleep(120)
        
#### Start Threads ####

try:
    thread_id = 1
    _thread.start_new_thread(thread1, (thread_id,))
    
    thread_id = 2
    _thread.start_new_thread(thread2, (thread_id,))

    thread_id = 3
    _thread.start_new_thread(thread3, (thread_id,))

    thread_id = 4
    _thread.start_new_thread(thread4, (thread_id, battery))
    
    thread_id = 5
    _thread.start_new_thread(thread5, (thread_id,))
    
except:
    print("Error: Unable to start the thread")