import network
import time
import socket
import machine
from machine import Pin, I2C
import sh1106
import config
import random
from picozero import Speaker
import neopixel
import music
import gc

#wifi config
ssid = config.SSID
password = config.PASSWORD

#TCP config
port = config.PORT

#board config
max_sequence = config.MAX_SEQUENCE
min_sequence = config.MIN_SEQUENCE

max_delayFAST = config.MAX_DELAY /3
min_delayFAST = config.MIN_DELAY /3

max_delayMEDIUM = config.MAX_DELAY * 0.8
min_delayMEDIUM = config.MIN_DELAY * 0.8

max_delaySLOW = config.MAX_DELAY * 1.2
min_delaySLOW = config.MIN_DELAY * 1.2

#photoresistors
photo_pins_config = config.PHOTO_PINS
photo_pins = []
for pin in photo_pins_config:
    photo_pins.append(machine.Pin(pin, machine.Pin.IN))

#leds
led_circle_pins_config = config.LED_PINS
led_circles = []
for pin in led_circle_pins_config:
    led_circles.append(neopixel.NeoPixel(machine.Pin(pin), 8))

#buzzer
speaker = Speaker(config.BUZZER_PIN2)

#Display setup
sda=machine.Pin(config.SDA)
scl=machine.Pin(config.SCL)
i2c = I2C(1, scl=scl, sda=sda, freq=config.SCREEN_FREQ)
display = sh1106.SH1106_I2C(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, i2c, Pin(config.FREE_PIN), 0x3c)
display.sleep(False)

#global variables
stop = False
firstRecord = False



#TODO
# temp and rec store for delays and lights
#Each previously played sequence is stored in temp, if you want to, you can record it and replay it with rec
tempSequence = []
recSequence = []

#led related functions
def get_rgb(mode):
    if mode == 2:
        r = 20
        g = 0
        b = 0
    elif mode == 1:
        r = 0
        g = 0
        b = 20
    elif mode == 3:
        r = 0
        g = 20
        b = 0
    else:
        r = 20
        g = 0
        b = 15
    return r, g, b


#server related functions
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print("failed")
            time.sleep(0.5)
    print('Connected to Wi-Fi')
    print('Local ip:' + wlan.ifconfig()[0])

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    server_socket.bind(addr)
    server_socket.listen(20)

    print("Server is listening for connections...")

    while True:
        try:
            cl, addr = server_socket.accept()
            print('client connected from', addr)
            break


        except OSError as e:
            cl.close()
            print('connection closed')
            return
    return cl

#display related functions
def display_text(text):
    display.fill(0)
    for i in range(0, 6):
        display.text(text, 0, i * 10, 1)
    display.show()

def display_setup():
    display_text('!!!SETTING UP!!!')

def board(cl):
    
    def play_hit_sound():
        speaker.play(500, 0.1)

    def light_off_leds():
        for led in led_circles:
            led.fill((0, 0, 0))
            led.write()

    def light_off_led(np):
        np.fill((0, 0, 0))
        np.write()

    def speaker_play(song):
        speaker.play(song)

    def fill_text_with_exclamations(base_text, total_length=16):
        filled_text = base_text
        while len(filled_text) < total_length:
            if len(filled_text) % 2 == 0:
                filled_text += "!"
            else:
                filled_text = "!" + filled_text
        return filled_text

    def display_score(score):
        display.fill(0)
        for i in range(0, 6):
            display.text(fill_text_with_exclamations("SCORE: " + str(score)), 0, i * 10, 1)
        display.show()

    def display_game_mode():
        display_text('!!CHOOSE GAME!!!')

    def display_start():
        display_text('!!!!PREPARE!!!!!')

    def update_accuracy(accuracy, cl):
        #print('sending accuracy', str(accuracy))
        try:
            cl.send(accuracy)
        except OSError as e:
            cl.close()
            machine.reset()
            

    def restart_accuracy(cl):
        try:
            cl.send(str(-1))
        except OSError as e:
            cl.close()
            machine.reset()
            
    def fill_leds(mode):
        r, g, b = get_rgb(mode)
        
        for led in led_circles:
            led.fill((r, g, b))
            led.write()
        
    def countdown(mode):
        fill_leds(mode)
        speaker_play(music.COUNTDOWN[0])
        light_off_leds()
        time.sleep(0.1)
        
        fill_leds(mode)
        speaker_play(music.COUNTDOWN[1])
        light_off_leds()
        time.sleep(0.1)
        
        fill_leds(mode)
        speaker_play(music.COUNTDOWN[2])
        light_off_leds()
        time.sleep(0.2)
        
        fill_leds(mode)
        speaker_play(music.COUNTDOWN[3])
        light_off_leds()
        time.sleep(0.1)
        speaker_play(music.COUNTDOWN[4])
        
        
    def generate_sequence(mode, cl):
        
        global tempSequence
        global recSequence
        tempSequence = []
        
        try:
            cl.send("-2 ")
        except OSError as e:
            cl.close()
            machine.reset()

        if mode == 2:
            min_delay = min_delayFAST
            max_delay = max_delayFAST
        elif mode == 1:
            min_delay = min_delayMEDIUM
            max_delay = max_delayMEDIUM
        elif mode == 3:
            min_delay = min_delaySLOW
            max_delay = max_delaySLOW
        else:
            min_delay = min_delayFAST
            max_delay = max_delaySLOW

        score = 0
        count = 0
        
        countdown(mode)
        
        if mode == 4:
            print(recSequence)
            for rec in recSequence:
                pin_index = rec[0]
                delay = rec[1]
                pin_photo = photo_pins[pin_index]
                led = led_circles[pin_index]
                np = led

                count += 1

                stop = False
                while not stop:
                    start_time = time.ticks_ms()
                    n = 8
                    i = 0
                    r, g, b = get_rgb(mode)

                    for i in range(4 * n):
                        for j in range(n):
                            np[j] = (r, g, b)
                        if (i // n) % 2 == 0:
                            np[i % n] = (0, 0, 0)
                        else:
                            np[n - 1 - (i % n)] = (0, 0, 0)
                        np.write()
                        
                        current_time = time.ticks_ms()
                        elapsed_time = time.ticks_diff(current_time, start_time)

                        if pin_photo.value() != 1:
                            play_hit_sound()
                            stop = True
                            score += 1
                            time.sleep(0.1)
                            gc.collect()
                            break
                        elif elapsed_time >= delay:
                            stop = True
                            time.sleep(0.1)
                            gc.collect()
                            break
                        time.sleep_ms(60)

                light_off_led(led)
                accuracy = str(int(score/count*100))
                add_trailing_whitespaces(accuracy)
                update_accuracy(accuracy, cl)
                display_score(score)
            

        else:
            for x in range(random.randint(min_sequence, max_sequence)):
                temp = []
                pin_index = random.randint(0, 4)

                pin_photo = photo_pins[pin_index]
                led = led_circles[pin_index]
                np = led

                count += 1

                delay = random.uniform(min_delay, max_delay)
                temp.append(pin_index)
                temp.append(delay)
                tempSequence.append(temp)

                stop = False

                while not stop:
                    start_time = time.ticks_ms()
                    n = 8
                    i = 0

                    r, g, b = get_rgb(mode)

                    for i in range(4 * n):
                        for j in range(n):
                            np[j] = (r, g, b)
                        if (i // n) % 2 == 0:
                            np[i % n] = (0, 0, 0)
                        else:
                            np[n - 1 - (i % n)] = (0, 0, 0)
                        np.write()
                        
                        current_time = time.ticks_ms()
                        elapsed_time = time.ticks_diff(current_time, start_time)
                        
                        if pin_photo.value() != 1:
                            play_hit_sound()
                            stop = True
                            score += 1
                            time.sleep(0.1)
                            gc.collect()
                            break
                        elif elapsed_time >= delay:
                            stop = True
                            time.sleep(0.1)
                            gc.collect()
                            break
                        time.sleep_ms(60)

                light_off_led(led)
                accuracy = str(int(score/count*100))
                add_trailing_whitespaces(accuracy)
                update_accuracy(accuracy, cl)
                display_score(score)

        if score < count/2:
            speaker_play(music.LOOSER)
        else:
            speaker_play(music.WINNER)
        time.sleep(1)
        restart_accuracy(cl)
        display_game_mode()

    def turn_off(cl):
        cl.close()
        machine.reset()

    def handle_gamemode(mode, cl):
        light_off_leds()
        generate_sequence(mode, cl)
        gc.collect()
        time.sleep(0.5)
        
    def record_sequence():
        play_hit_sound()
        display_recording()

        global recSequence
        global tempSequence
        global firstRecord
        
        firstRecord = True
        recSequence = tempSequence

        speaker_play(music.RECORDING_START)
        
    def replay_sequence():
        global recSequence
        global tempSequence
        global firstRecord

        if recSequence == [] or not firstRecord:
            recSequence = tempSequence

        generate_sequence(4, cl)
        
    def display_recording():
        display_text('!!!RECORDING!!!')
        
    def add_trailing_whitespaces(string):
        missing = 3-len(string)
        if missing != 0:
            string  += missing*' '

    def choose_gamemode(cl):

        display_game_mode()

        medium_gamemode_pin = photo_pins[0]
        fast_gamemode_pin = photo_pins[1]
        slow_gamemode_pin = photo_pins[2]
        record_gamemode_pin = photo_pins[3]
        replay_gamemode_pin = photo_pins[4]

        while True:

            n = 8
            i = 0
            
            for i in range(4 * n):
                for indx, np in enumerate(led_circles):
                    for j in range(n):
                        r, g, b = get_rgb(indx + 1)
                        np[j] = (r, g, b)
                    if (i // n) % 2 == 0:
                        np[i % n] = (0, 0, 0)
                    else:
                        np[n - 1 - (i % n)] = (0, 0, 0)
                    np.write()

                    if fast_gamemode_pin.value() != 1:
                        display_start()
                        handle_gamemode(2, cl)

                    elif medium_gamemode_pin.value() != 1:
                        display_start()
                        handle_gamemode(1, cl)

                    elif slow_gamemode_pin.value() != 1:
                        display_start()
                        handle_gamemode(3, cl)

                    elif record_gamemode_pin.value() != 1:
                        print('recording')
                        record_sequence()

                    elif replay_gamemode_pin.value() != 1:
                        print('playing recorded')
                        replay_sequence()
                        

                    time.sleep_ms(60)

    light_off_leds()
    choose_gamemode(cl)

def setup_leds():
    for led in led_circles:
        led.fill((5, 5, 5))
        led.write()

def start():
    gc.enable()
    setup_leds()
    display_setup()
    connect_wifi()
    cl = start_tcp_server()
    board(cl)


start()
