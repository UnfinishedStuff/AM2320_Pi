#!/usr/bin/env python3

import os
import fcntl
import time
import struct

class AM2320:
	#Constructor to set up the class
	def __init__(self):
		#Set the i2c address
		self.address = 0x5c
		#I *think* this is about setting the address for i2c
		# slave requests in the Linux kernel (?)
		self.slave = 0x0703

		#Open the i2c bus in read/write mode as a file object
		self.fd = os.open("/dev/i2c-1", os.O_RDWR)
		fcntl.ioctl(self.fd, self.slave, self.address)

		#List for holding raw read data
		self.raw_data = [0,0,0,0]

		#Initial values for variables
		self.temperature = 0
		self.humifity = 0

	#A function to read data from the sensor, calculate temp and
	#humidity and store in the variables in the object
	def get_data(self):
		#The AM2320 drops into sleep mode when not interacted
		#with for a while.  It wakes up when poked across the i2c bus
		#but doesn't return data immediately, so poke it to wake it
		#and ignore the fact that no acknowledgement is recieved.
		try:
			os.write(self.fd, b'\0x00')
		except:
			pass

		os.write(self.fd, b'\x03\x00\x04')

		#Give the sensor a few microseconds to take measurements
		#(If you don't it gives an I/O Error)
		time.sleep(0.000003)

		#Read the data into raw_data
		self.raw_data = bytearray(os.read(self.fd, 8))

		#Process the temperature bytes into degrees C
		self.temperature = ((self.raw_data[4] << 8)\
 + self.raw_data[5])/10.0

		#Process the humidity bytes to %RH
		self.humidity = ((self.raw_data[2] << 8) \
 + self.raw_data[3])/10.0
