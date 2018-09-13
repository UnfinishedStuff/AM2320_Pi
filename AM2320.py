#!/usr/bin/env python3

#These are needed for talking to the i2c bus
import os
import fcntl

import time


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

		#Initial value for CRC check
		self.CRC = 0xFFFF

	#A function to read data from the sensor, calculate temp and
	#humidity and store in the variables in the object
	def get_data(self):

		#Reset the CRC variable
		self.CRC = 0xFFFF

		#The AM2320 drops into sleep mode when not interacted
		#with for a while.  It wakes up when poked across the i2c bus
		#but doesn't return data immediately, so poke it to wake it
		#and ignore the fact that no acknowledgement is recieved.
		try:
			os.write(self.fd, b'\0x00')
		except:
			pass

		#Tell the sensor you want to read data (0x03), starting at register 0 
		#(0x00), and that you want 4 bytes of sensor data.  This starts the read
		#at the humidity most significant byte, passes through the humidity least
		#significant and temperature most significant bytes and stops after
		#reading the temperature least significant byt.
		os.write(self.fd, b'\x03\x00\x04')

		#Give the sensor a few microseconds to take measurements (if you don't it
		# gives an I/O Error).  The value was arrived at by trial and error, it
		#may need tweaking or may possibly be turned down a bit.
		time.sleep(0.0001)

		#Read the data into the list called "raw_data".  Bytes 0 and 1 are the
		#instructions given to the device (0x03 and 0x04), given to check that 
		#what was read is what was asked for.  Bytes 2 and 3 are the
		# humidity high and low bytes respectively.  Bytes 4 and 5 are the
		# temperature high and low bytes respectively.  Bytes 6 and 7 are the CRC
		# high and low bytes respectively (see below).
		self.raw_data = bytearray(os.read(self.fd, 8))

		#Do the Cyclic Redundancy Code (CRC) check.  This progressively combines
		#the first 6 bytes recieved (raw_data bytes 0-5) with a variable of value
		#0xFFFF in a way which should eventually result in a value which is equal
		#to the combined CRC bytes.  If this check fails then something has been
		#corrupted during transmission.
		for byte in self.raw_data[0:6]:
			self.CRC = self.CRC ^ byte
			for x in range (0,8):
				if (self.CRC & 0x01 == 0x01):
					self.CRC = self.CRC >> 1
					self.CRC = self.CRC ^ 0xA001
				else:
					self.CRC = self.CRC >> 1
		#If raw_data 0 + 1 (the returned intruction codes) don't match 0x03 and
		#0x04 (the instructions which were given) alert the user to the error
		if ((self.raw_data[0] != 0x03) or (self.raw_data[1] != 0x04)):
			print("ERROR: recieved bytes 0 and 1 corrupt")
		#If the CRC bytes don't equal the calculated CRC code alert the user to
		#the error.
		elif (self.CRC != ((self.raw_data[7] << 8) + self.raw_data[6])):
			print("CRC error, data corrupt!")
		#Otherwise, everything is fine and calculate the temp/humidity values
		else:
			#Bitshift the temperature most significant byte left by 8 bits
			#and combine with the least significant byte.  Divide by 10 to 
			#give the temperature in degrees celsius according to the datasheet
			self.temperature = ((self.raw_data[4] << 8)\
 + self.raw_data[5])/10.0
			#Bitshift the humidity most significant byte left by 8 bits and add
			#it to the least significant byte.  Divide this by 10 to give the
			#humidity in % relative humidity, according to the datasheet.
			self.humidity = ((self.raw_data[2] << 8) \
 + self.raw_data[3])/10.0
