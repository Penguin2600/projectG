#!/usr/bin/env python
import time
import os
import wiringpi
import collections

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        wiringpi.digitalWrite(cspin, 1)

        wiringpi.digitalWrite(clockpin, 0)  # start clock low
        wiringpi.digitalWrite(cspin, 0)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        wiringpi.digitalWrite(mosipin, 1)
                else:
                        wiringpi.digitalWrite(mosipin, 0)
                commandout <<= 1
                wiringpi.digitalWrite(clockpin, 1)
                wiringpi.digitalWrite(clockpin, 0)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                wiringpi.digitalWrite(clockpin, 1)
                wiringpi.digitalWrite(clockpin, 0)
                adcout <<= 1
                if (wiringpi.digitalRead(misopin)):
                        adcout |= 0x1
        wiringpi.digitalWrite(cspin, 1)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired
SPICLK = 1
SPIMISO = 4
SPIMOSI = 5
SPICS = 6

#Do Setup
wiringpi.wiringPiSetup()

# set up the SPI interface pins
wiringpi.pinMode(SPIMOSI, 1)
wiringpi.pinMode(SPIMISO, 0)
wiringpi.pinMode(SPICLK,  1)
wiringpi.pinMode(SPICS,   1)

wiringpi.pullUpDnControl(SPIMISO, 0)

redPin=0
greenPin=1
bluePin=2

lastRed=0
lastGreen=0
lastBlue=0

tolerance=10


dataFile= open("data.txt", "w")
step=0
redAvg=collections.deque(maxlen=10)
greenAvg=collections.deque(maxlen=10)
blueAvg=collections.deque(maxlen=10)

while True:
	step=step+1
	redChannel = readadc(redPin, SPICLK, SPIMOSI, SPIMISO, SPICS)
	greenChannel = readadc(greenPin, SPICLK, SPIMOSI, SPIMISO, SPICS)*1.5
	blueChannel = readadc(bluePin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        
	deltaRed=abs(lastRed-redChannel)
        deltaGreen=abs(lastGreen-greenChannel)
        deltaBlue=abs(lastGreen-greenChannel)
	
	if (deltaRed > tolerance or deltaGreen >tolerance or deltaBlue >tolerance):
		redAvg.append(redChannel)
		x=0
		for i in redAvg:
			x+=i
		x=x/len(redAvg)

		greenAvg.append(greenChannel)
		y=0
		for i in greenAvg:
			y+=i
		y=y/len(greenAvg)

		blueAvg.append(blueChannel)
		z=0
		for i in blueAvg:
			z+=i
		z=z/len(blueAvg)

		#os.system("clear")
	        print "R:", redChannel
	        print "G:", greenChannel
	        print "B:", blueChannel
#        	dataFile.write("%d,%d,%d,%d,%d,%d,%d\n" % (redChannel, greenChannel, blueChannel,step,x,y,z))
	        lastGreen=greenChannel
	        lastRed=redChannel 
                lastBlue=blueChannel
	else:
		pass
	#	dataFile.write("%d,%d,%d,%d,%d,%d,%d\n" % (redChannel, greenChannel, blueChannel,step,x,y,z))     
        time.sleep(0.1)
