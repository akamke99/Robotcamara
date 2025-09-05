from bbio import *
import Adafruit_BBIO.GPIO as GPIO
import time
import ctypes
import numpy as np

libc = ctypes.CDLL('libc.so.6')

def delayMicroseconds(us):
 # """ Delay microseconds with libc usleep() using ctypes. """
	libc.usleep(int(us))

def setup():
	SPI0.begin()
	SPI0.setClockMode(0, 0)
	SPI0.setMaxFrequency(0, 2400000)
	SPI0.setBitsPerWord(0, 8)

def loop():
	inMotor = raw_input('Motor: ')
	inSteps = np.int_(raw_input('Steps: '))
	sendCommand(inMotor, inSteps)

def sendCommand(motor, steps):
	#comunicacion spi
	recieveList = 0
	while(recieveList != 126  ):	
            delayMicroseconds(10000)
            recieveList = (SPI0.transfer(0, [ord('c')]))[0]
            delayMicroseconds(10000)
            recieveList = (SPI0.transfer(0, [ord(motor)]))[0]

            delayMicroseconds(10000)
            SPI0.transfer(0, [int(np.int32(steps) & int('0b11111111', 2))])
            delayMicroseconds(10000)	
            SPI0.transfer(0, [int((np.int32(steps) >> 8) & int('0b11111111', 2)) ])
            delayMicroseconds(10000)	
            SPI0.transfer(0, [int((np.int32(steps) >> 16) & int('0b11111111', 2)) ])
            delayMicroseconds(10000)
            SPI0.transfer(0, [int((np.int32(steps) >> 24) & int('0b11111111', 2)) ])        
            delayMicroseconds(10000)

            if (recieveList==126):
                return steps				
		#else:
		#	if (recieveList!=99):
		#		print 'respuesta: ' + str(recieveList)


		
	

setup()
#print 'SPI Ready'
#run(setup, loop)
