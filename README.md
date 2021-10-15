# PiDration

PiDration is a software and hardware implementation of a soil analytics platform 
that I use to monitor my plants because they kept dying. Horribly

# Table of Contents
- [Hardware](#hardware)
- [Software](#software)
  * [C++](#c--)
  * [Python](#python)
  * [RF24 library](#rf24-library)

# Hardware
The server is a Raspberry Pi 400 all-in-one. 

Each slave is a Arduino nano microcontroller that 
communicates with a hydration sensor via i2c.

Slaves and the server communicate via RF signal connected via SPI. 

# Software

## C++
Slaves run on a very C-like subset of C++. The communication is facilitated with the RF24 library. 

## Python
The server is a threaded python code. that spins up three threads. 
One for controlling output to a 16x2 LCD, One for listening for communications from the slaves, and 
a main thread that queries the Database. 

The database is a SQLite 3 DB. with the following shemea: 

    sensor        OTM ->     data                
    ----------               ---------
    *id                      *id
    name                     value
    node                     date
    threshold                sensor_id
                             FOREIGN KEY(sensor_id) REFERENCES sensor(sensor_id)
