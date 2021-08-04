import adafruit_character_lcd.character_lcd as characterlcd
from Sensor import *
from rf24libs import RF24
from RF24 import RF24, RF24_PA_LOW
import sqlite3
from sqlite3 import Error
import digitalio
import threading
import struct
import board
import time

# Globals.
radio = RF24(25, 0)
options = 3

addresses = [
    b"\x78" * 5,
    b"\xF1\xB6\xB5\xB4\xB3",
    b"\xCD\xB6\xB5\xB4\xB3",
    b"\xA3\xB6\xB5\xB4\xB3",
    b"\x0F\xB6\xB5\xB4\xB3",
    b"\x05\xB6\xB5\xB4\xB3"
]

# Sensor dictionary
sensors = {}

def reading_thread(radio, sensors):
    ''' Thread that waits for sensors to report '''

    db = connect_db('data/pidration.db')

    try:
        # Open existing pipes.
        for x, sensor in sensors.items():
            radio.openReadingPipe(x, sensor.address)
        radio.setPALevel(RF24_PA_LOW)
        radio.startListening()
        
        while True:
            # Read from radio. 
            data, pipe = radio.available_pipe()
            
            if data:
                node, data = struct.unpack("<ii", radio.read(radio.payloadSize))
                print('Recieved {} from node {}'.format(data, node))
                sensors[node].data.append(data)
                sensors[node].insert_data(db, data)
                sensors[node].panic = sensors[node].threshold <= data
            
            time.sleep(.25)
    finally:
        if db:
            db.close()

def display_thread(sensors):
    ''' Thread that controls the lcd '''

    # LCD initialization. 
    lcd_columns = 16
    lcd_rows = 2

    lcd_rs = digitalio.DigitalInOut(board.D22)
    lcd_en = digitalio.DigitalInOut(board.D24)
    lcd_d4 = digitalio.DigitalInOut(board.D19)
    lcd_d5 = digitalio.DigitalInOut(board.D13)
    lcd_d6 = digitalio.DigitalInOut(board.D6)
    lcd_d7 = digitalio.DigitalInOut(board.D16)

    lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                        lcd_d7, lcd_columns, lcd_rows)
    lcd.clear()

    while True:
        for sensor in sensors.values():
            line1 = sensor.name + ': \n'
            if len(sensor.data):
                line2 = str(sensor.data[-1])
            else:
                line2 = 'No data'
            
            if sensor.panic:
                line2 += ' PAINIC!'

            lcd.clear()
            lcd.message = line1+line2

            time.sleep(5)

def connect_db(filename: str) -> sqlite3.Connection:
    ''' Connect to the database and return that connection. '''
    connection = None

    try:
        connection = sqlite3.connect(filename)

    except Error as e:
        print(e)
    
    return connection

def load_sensors(sensors):
    ''' Load sensor data from db '''

    db = connect_db('data/pidration.db')

    cur = db.cursor()
    cur.execute("SELECT * FROM sensors")

    all = cur.fetchall()
    
    for s in all:
        id = s[0]
        name = s[1]
        node = s[2]
        threshold = s[3]

        sensors[node] = Sensor(node=node, 
                               name=name, 
                               threshold=threshold,
                               address=addresses[node],
                               id=id)

    return sensors

def print_menu():
    print("Make a selection from the menu below")
    print("by entering the number of the selection.")
    print()

    print("1. Examine sensor data.")
    print("2. Quit.")
    print()

def process_input(inp, sensors):
    inp = int(inp)

    if inp not in range(1, 3):
        print("Invalid selection.")
        return
    
    if inp == 1:
        pass
    elif inp == 2:
        exit()
        
if __name__ == "__main__":

    # Start reading thread.
    # Start display thread. 
    # Print menu. 
    try:
        # Set up preliminary raio things
        if not radio.begin():
            raise RuntimeError("radio hardware is not responding")
        radio.payloadSize = len(struct.pack("<ii", 0, 0))

        sensors = load_sensors(sensors)

        # Start up out threads.
        read = threading.Thread(target=reading_thread,
                                args=(radio, sensors),
                                daemon=True)
        read.start()   
        
        display = threading.Thread(target=display_thread,
                                args=(sensors,),
                                daemon=True)
        display.start()

        # Start up the menu.
        while True:
            print_menu()
            process_input(input('> '), sensors)

    except KeyboardInterrupt:
        read.join()
        display.join()