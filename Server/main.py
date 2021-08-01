import adafruit_character_lcd.character_lcd as characterlcd
from rf24libs import RF24
from RF24 import RF24, RF24_PA_LOW
import sqlite3
from sqlite3 import Error
import digitalio
import threading
import struct
import board
import time


class Sensor:
    ''' Sensor class '''
    def __init__(self, **kwargs):
        self.name    = kwargs.get("name")
        self.address = kwargs.get("address")
        self.id      = kwargs.get("id")
        self.data    = kwargs.get("data", [])

        self.threshold = kwargs.get("threshold", 400)
        self.panic = False

# Globals.
radio = RF24(25, 0)
db = None

# Dictionary of sensor data keyed on pipe address.
sensors = {
    0: None,
    1: None,
    2: None
}

addresses = [
    b"\x78" * 5,
    b"\xF1\xB6\xB5\xB4\xB3",
    b"\xCD\xB6\xB5\xB4\xB3",
    b"\xA3\xB6\xB5\xB4\xB3",
    b"\x0F\xB6\xB5\xB4\xB3",
    b"\x05\xB6\xB5\xB4\xB3"
]

sensors_lock = threading.Lock()

def reading_thread(radio, sensors, sensors_lock):
    ''' Thread that waits for sensors to report '''

    # Open existing pipes.
    for x, sensor in sensors.items():
        print('Opened pipe {} at address {}'.format(x, sensor.address))
        radio.openReadingPipe(x, sensor.address)
    radio.setPALevel(RF24_PA_LOW)
    radio.startListening()
    
    while True:
        # Read from radio. 
        data, pipe = radio.available_pipe()
        
        if data:
            node, data = struct.unpack("<ii", radio.read(radio.payloadSize))
            #print('Recieved {} from node {}'.format(data, node))
            sensors[node].data.append(data)
            sensors[node].panic = sensors[node].threshold <= data
        
        time.sleep(.25)

def display_thread(sensors, sensors_lock):
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
        print('CONNECTION TO SENSOR DATABASE ESTABLISED')
    except Error as e:
        print(e)
    
    return connection

def load_db(db, sensors):
    ''' Load sensor data from db '''
    count = 0

    db = connect_db('data/pidration.db')

    for x in sensors.keys():
        s = Sensor(name='Sens{}'.format(x), address=addresses[count], id=x)
        sensors[x] = s
        count += 1

if __name__ == "__main__":

    # Start reading thread.
    # Start display thread. 
    # Print menu. 
    try:
        # Set up preliminary raio things
        if not radio.begin():
            raise RuntimeError("radio hardware is not responding")
        radio.payloadSize = len(struct.pack("<ii", 0, 0))
        load_db(None, sensors)

        # Start up out threads.
        read = threading.Thread(target=reading_thread,
                                args=(radio, sensors, sensors_lock))
        read.start()   
        
        display = threading.Thread(target=display_thread,
                                args=(sensors, sensors_lock))
        display.start()

    except KeyboardInterrupt:
        read.join()
        
    finally:
        if db:
            db.close()