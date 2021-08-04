import sqlite3
from sqlite3 import Error
import time

class Sensor:
    ''' Sensor class '''
    def __init__(self, **kwargs):
        self.name    = kwargs.get("name")
        self.address = kwargs.get("address")
        self.node    = kwargs.get("node")
        self.data    = kwargs.get("data", [])
        self.id      = kwargs.get("id")

        self.threshold = kwargs.get("threshold", 400)
        self.panic = False
        

    def insert_sensor(self, db):
        ''' 
        Insert the sensor into the sensors table.
        :param db: Database connection object.
        :return: sensor_id
        '''

        sql_command = ''' INSERT INTO sensors(name, node, threshold)
                          VALUES(?, ?, ?) '''
        info = (self.name, self.node, self.threshold)

        c = db.cursor()
        c.execute(sql_command, info)
        db.commit()

        return c.lastrowid

    def insert_data(self, db, value):
        '''
        Insert data into table.
        :param db: Database
        :param value: Data point from sensor. 
        '''

        date = time.asctime(time.localtime(time.time()))

        sql_command = ''' INSERT INTO data(value, date, sensor_id)
                          VALUES(?, ?, ?) '''
        info = (value, date, self.id)

        c = db.cursor()
        c.execute(sql_command, info)
        db.commit()

        return self.id