import utime
from umqtt.robust2 import MQTTClient
import sys
import network
import os
import _thread
from time import sleep
from time import ticks_ms
from machine import Pin
from neopixel import NeoPixel

stop_thread = 0 #definere en variabel stop_thread

n = 12
p = 27
np = NeoPixel(Pin(p, Pin.OUT), n)

def sync_with_adafruitIO(): 
    # haandtere fejl i forbindelsen og hvor ofte den skal forbinde igen
    do_connect()
    if c.is_conn_issue():
        while c.is_conn_issue():
            # hvis der forbindes returnere is_conn_issue metoden ingen fejlmeddelse
            c.reconnect()
        else:
            c.resubscribe()
    c.check_msg() # needed when publish(qos=1), ping(), subscribe()
    c.send_queue()  # needed when using the caching capabilities for unsent messages
    

try:
    from credentials import credentials
except ImportError:
    print("Credentials are kept in credentials.py, please add them there!")
    raise
# WiFi connection information
WIFI_SSID = credentials["ssid"]
WIFI_PASSWORD = credentials["password"]

# turn off the WiFi Access Point
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# connect the device to the WiFi network
wifi = network.WLAN(network.STA_IF)
if wifi.isconnected():
    wifi.disconnect()#Fixer WiFi OS fejl!
wifi.active(True)

def set_color(r, g, b): #Definere set_color
    for pixels in range(n): #for loop
        np[pixels] = (r, g, b)
        np.write()
        sleep(0.001)

def neo_spin(): #definerer funktionen neo_spin
    spin = 0 #led starter med ikke at lyse
    connecting = 1 #Begynder at lyse
    while connecting == 1: #while loop, hvor neopixel lyser hvidt
        np[spin] = (15, 15, 15) #skarpest farve
        np[spin - 1] = (8, 8, 8) #mindre
        np[spin - 2] = (1, 1, 1) #mindst
        np[spin - 3] = (0, 0, 0) #slukket
        np.write() #starter neopixel
        spin = spin + 1 #plusser spin med 1 så neopix bliver ved med at køre rundt ring.
        if spin == 12: #if condition, hvis den er nået en hel omgang.
            spin = 0  #Starter forfra
        sleep(0.1) #sover 0.1
        if stop_thread == 1: #If condition hvis stop_thread == 1 stopper neopixel
            break #stopper

def thread1(thread_id): #Definerer thread1 med argumentet thread_id
    while True: #while true loop som før
        neo_spin() #Kører neo_spin funktion
        if stop_thread == 1: #if condition
            break #Stopper
    
def do_connect():
    if not wifi.isconnected():
        try:
            thread_id = 1
            _thread.start_new_thread(thread1, (thread_id,))
        except:
            pass
        print("Forbinder til wifi...")
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
        # wait until the device is connected to the WiFi network
        MAX_ATTEMPTS = 20
        attempt_count = 0
        while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
            attempt_count += 1
            
            utime.sleep(1)

        if attempt_count == MAX_ATTEMPTS: #hvis max attemps så print
            print('Kunne ikke forbinde til WiFi') #print i shell
            sys.exit() #Lukker programmet
            for i in range(3): #for loop skal køre 3 gange
                set_color(10, 0, 0) #Rød farve
                sleep(0.2) #sover 0.2sek
                set_color(0, 0, 0) #slukker
                sleep(0.2) #sover 0.2sek

do_connect()

besked = ""

def sub_cb(topic, msg, retained, duplicate):
    #print((topic, msg, retained, duplicate))
    m = msg.decode('utf-8')
    global besked
    besked = m.lower()
    print("\n",besked)
# create a random MQTT clientID
random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id = bytes('client_'+str(random_num), 'utf-8')

# connect to Adafruit IO MQTT broker using unsecure TCP (port 1883)
#
# To use a secure connection (encrypted) with TLS:
#   set MQTTClient initializer parameter to "ssl=True"
#   Caveat: a secure connection uses about 9k bytes of the heap
#         (about 1/4 of the micropython heap on the ESP8266 platform)
ADAFRUIT_IO_URL = credentials["ADAFRUIT_IO_URL"]
ADAFRUIT_USERNAME = credentials["ADAFRUIT_USERNAME"]
ADAFRUIT_IO_KEY = credentials["ADAFRUIT_IO_KEY"]
ADAFRUIT_IO_FEEDNAME = credentials["ADAFRUIT_IO_FEEDNAME"]


c = MQTTClient(client_id=mqtt_client_id,
                    server=ADAFRUIT_IO_URL,
                    user=ADAFRUIT_USERNAME,
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)
# Print diagnostic messages when retries/reconnects happens
c.DEBUG = True
# Information whether we store unsent messages with the flag QoS==0 in the queue.
c.KEEP_QOS0 = False
# Option, limits the possibility of only one unique message being queued.
c.NO_QUEUE_DUPS = True
# Limit the number of unsent messages in the queue.
c.MSG_QUEUE_MAX = 2

c.set_callback(sub_cb)

mqtt_feedname = '{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, ADAFRUIT_IO_FEEDNAME)

killThread = 0

def web_print2(text_in, feed):
    global killThread
    killThread = 1
    c.publish(topic=bytes(feed, 'utf-8'), msg=str(text_in))
    sleep(2)
    killThread = 0
    _thread.exit()
    
def web_print(text_in, feed = mqtt_feedname):
    if killThread == 0:
        #print(f"starting new thread \ntext_in: {text_in} \nfeed: {feed} \n killThread: {killThread}")
        _thread.start_new_thread(web_print2, (text_in, feed))
    else:
        print(f"Not sending: \nMessage: {text_in} \nTo feed: {feed}  \nplease wait 3 seconds or more before sending the next message.")


if not c.connect(clean_session=False): #if condition for hvis den ER connectet
    print("Forbinder til Adafruit IO, med klient ID: ",random_num) #Print i shell
    c.subscribe(mqtt_feedname)
    stop_thread = 1 #ændre stopthread til 1
    for i in range(3): #for loop der skal køre 3 gange, hvor farve = grøn
        set_color(0, 100, 0) #Grøn
        sleep(0.2) #sover 0.2
        set_color(0, 0, 0) #Slukker
        sleep(0.2) #sover 0.2
