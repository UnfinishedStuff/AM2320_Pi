# AM2320_Pi
A python script for running the AM2320 temperature and humidity sensor on a Raspberry Pi

This script owes a lot to the code by Joakim Lotsengård (https://github.com/Gozem/am2320), mostly by trying to understand the way that they accessed the i2c bus and then writing my own code to access the device in an object-oriented way.

This is an Object Oriented Programming version of the script.  If you don't know what that means don't worry, it's very easy to use.

** Suggested usage **

The easiest way to use this is to copy what is done in the `AM2320_demo.py` script:

*  Start by importing the AM2320 module by using `import AM2320`.
* Create a sensor object which fetches and holds all of the data.  To create a sensor object called "sensor" use the code `sensor = AM2320.AM2320()`.  You can change "sensor" to any name you like, just remember to change this in the later steps as well.
*  Just before you want a temperature or humidity value tell the sensor to take readings with the command `sensor.get_data()`.  It will take the readings and store them in the sensor object automatically.  Note that it automatically reads both temperature and humidity values.  This takes fractions of a second so doing both instead of one shouldn't slow your programs in any meaningful way.
*  The variables `sensor.temperature` and `sensor.humidity`, which are part of the sensor object, now hold the values for temperature (in degrees C) and humidity (in % relative humidity) respectively.  You can use these directly with the variable names `sensor.temparature` or `sensor.humidity`. For example, to print the temperature your code should look like `print(sensor.temperature)`.

That's it!  The only user-accessible function in the sensor class is `get_data`.


** A note on data integrity **

The AM2320 is interesting in that it provides a couple of ways to check that the data begin transmitted to the Pi is correct.  The temperature and humidity are both sent as two bytes, one is the Most Significant Byte (MSB) and the other is the Least Significant Byte (LSB).  The MSB needs to be shifted to the left by 8 bits (e.g., if it was 0b1111 1111 it should read 0b1111 1111 0000 0000), and then the LSB is added (so if the LSB was 0b1010 1010 the combination would look like 0b1111 1111 1010 1010).  However, if you ask the AM2320 for these four bytes (which are all you need to calculate the temperature and humidity) the sensor will actually try to send **8** bytes.  The first two are just a repeat of the commands which you sent to the sensor, so it confirms that it recieved the command which you wanted it to act on.  The next 2 bytes are for the humidity, and the 2 after that are for the temperature.  The final 2 bytes are the "Cyclic Redundancy Code", also in the MSB/LSB format.  To check data integrity the value 0xFFFF (or 65535 in decimal) is processed with the first 6 bytes in the data, byte by byte to calculate a variable.  The final value of this variable is wholly dependent on the values of the first 6 bytes.  This variable is then compared to the CRC, made of the last two bytes, and they should be equal.  If they're not then at least one of the bits of data was corrupted during transmission and the values may be wrong.  This feature probably isn't critically important for most people but it's a neat idea which most of the i2c devices I've encountered don't bother with.

** To Do **

Doesn't currently handle negative temperatures at all.
