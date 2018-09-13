#!/usr/bin/python

import time
import AM2320

#Create an object from the AM2320 class called "sensor"
sensor = AM2320.AM2320()

#Do the following continuously:
while True:
	#Tell the sensor object to read data from the physical sensor
	sensor.get_data()
	#Print the temp. and humidity values now stored in the sensor object
	print(str(sensor.temperature) + " degrees C")
	print(str(sensor.humidity) + " %R\n")
	#Delay before the next reading
	time.sleep(1)
