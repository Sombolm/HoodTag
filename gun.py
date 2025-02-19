import network
import socket
import time
import config
import _thread
import ssd1306
import machine
from machine import Pin, I2C
from picozero import Speaker
import gc


ssid = config.SSID
password = config.PASSWORD
server_addr = config.SERVER_ADDR
server_port = config.PORT

# declaring gun modules
speaker = Speaker(config.BUZZER_PIN2)
laser = Pin(config.LASER_PIN, Pin.OUT)
trigger = Pin(config.TRIGGER_PIN, Pin.IN, Pin.PULL_DOWN)

canPistolShoot = True # gun shooting logic flag

i2c = I2C(1, sda=Pin(2), scl=Pin(3))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
def display_text(text):
    display.fill(0)
    for i in range(0, 6):
        display.text(text, 0, i * 10, 1)
    display.show()
    
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        display_text(fill_text_with_exclamations("CONNECTING WIFI"))
        print('Connecting to Wi-Fi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print("failed")
            display_text(fill_text_with_exclamations("FAILED"))
            time.sleep(0.5)
    print('Connected to Wi-Fi')
    display_text(fill_text_with_exclamations("CONNECTED"))
    print('Local ip:' + wlan.ifconfig()[0])


def display_setup():
    display_text('!!!SETTING UP!!!')

def display_game_mode():
    display_text('!!CHOOSE GAME!!!')

def display_start():
    display_text('!!!!PREPARE!!!!!')

def speaker_play():
    speaker.play(200, 0.1)

def fill_text_with_exclamations(base_text, total_length=16):
    filled_text = base_text
    while len(filled_text) < total_length:
        if len(filled_text) % 2 == 0:
            filled_text += "!"
        else:
            filled_text = "!" + filled_text
    return filled_text

def update_accuracy(acc):
    display.fill(0)
    for i in range(0, 6):
        text = fill_text_with_exclamations('ACCURACY: ' + str(acc) + str("%"), 16)
        display.text(text, 0, i * 10, 1)
    display.show()

def start_tcp_client(server_addr, server_port):
    display_text('!!STARTING TCP!!')
    print("Starting TCP client...")

    ai = socket.getaddrinfo(server_addr, server_port)
    addr = ai[0][-1]
    print(addr)

    client_socket = socket.socket()
    display_text('!!!TRYING TCP!!!')
    print("Trying to connect to TCP")
    client_socket.connect(addr)
    print(f"Connected to server at {addr}")
    display_text('!!!CONNECTED!!!!')
    client_socket.setblocking(False)
    
    return client_socket
    
def handle_gun(client_socket):
    while True:
        global canPistolShoot
        
        # Handle trigger and laser logic
        triggerVal = trigger.value()
        if canPistolShoot and triggerVal == 1:
            laser.value(1)
            speaker.play(200, 0.1)
            canPistolShoot = False
            time.sleep(0.1)
        elif not canPistolShoot and triggerVal == 0:
            laser.value(0)
            canPistolShoot = True
        else:
            laser.value(0)
        
        time.sleep(0.1)
        
        try:
            response = client_socket.recv(3)
            if response:
                response = response.decode().strip()
                print(response)
                if response == "-1":
                    display_game_mode()
                elif response == "-2":
                    display_start()
                elif response != "":
                    update_accuracy(response)
        except OSError as e:
            print(e)
            if e.errno == 11: 
                continue 
            else:
                client_socket.close()
                machine.reset()
        

def start():
    gc.enable
    display_setup()
    connect_wifi()
    client_socket = start_tcp_client(server_addr, server_port)
    handle_gun(client_socket)

start()




