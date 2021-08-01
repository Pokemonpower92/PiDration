'''  
    This script creates and initializes 
    the database used to store sensor data. 

    The database holds two tables - sensors and data
    Sensors have a one to many relationship with data

    sensor        OTM ->     data                
    ----------               ---------
    *id                      *id
    name                     value
    node                     date
    threshold
'''

import sqlite3
from sqlite3 import Error

c = None

try:
    c = sqlite3.connect('pidration.db')
    print('Connection to db established')


except Error as e:
    print(e)
finally:
    if c:
        c.close()