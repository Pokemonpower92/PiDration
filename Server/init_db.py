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
    threshold                sensor_id
                             FOREIGN KEY(sensor_id) REFERENCES sensor(sensor_id)
'''
import sqlite3
from sqlite3 import Error
from Sensor import *



# Dictionary of sensor data keyed on pipe address.
sensors = [
    Sensor(node=0, name="Snake Plant", threshold=400),
    Sensor(node=1, name="Peace Lily", threshold=600)
]

def create_table(c, sql_command): 
    ''' Create  a table. 
        :param c: Connection
        :param sql_command: CREATE TABLE statement
        :return:
    '''

    try:
        cursor = c.cursor()
        cursor.execute(sql_command)

    except Error as e:
        print(e)


sql_create_sensor_table = ''' CREATE TABLE IF NOT EXISTS sensors (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                node integer NOT NULL,
                                threshold integer NOT NULL
                              ); '''

sql_create_data_table = ''' CREATE TABLE IF NOT EXISTS data (
                                id integer PRIMARY KEY,
                                value integer NOT NULL,
                                date text NOT NULL,
                                sensor_id integer NOT NULL,
                                FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                            ); '''

c = None


if __name__ == '__main__':
    try:
        c = sqlite3.connect('data/pidration.db')
        print('Connection to db established')

        create_table(c, sql_create_sensor_table)
        create_table(c, sql_create_data_table)

        for s in sensors:
            s.insert_sensor(c)

    except Error as e:
        print(e)
    finally:
        if c:
            c.close()