#!/usr/bin/env python
import time
import os
import wiringpi
import collections

def init():

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

def main():

    init()

    redPin=0
    greenPin=1
    bluePin=2

    dataFile= open("data.txt", "w")
    step=0
    redAvg=collections.deque(maxlen=6)
    greenAvg=collections.deque(maxlen=6)
    blueAvg=collections.deque(maxlen=6)

    while True:
        step=step+1
        redChannel = readadc(redPin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        greenChannel = readadc(greenPin, SPICLK, SPIMOSI, SPIMISO, SPICS)*1.2
        blueChannel = readadc(bluePin, SPICLK, SPIMOSI, SPIMISO, SPICS)*1.2
            
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

        dataFile.write("%d,%d,%d,%d,%d,%d,%d\n" % (redChannel, greenChannel, blueChannel,step,x,y,z))
        lastGreen=greenChannel
        lastRed=redChannel 
        lastBlue=blueChannel
   
        time.sleep(0.01)

if __name__ == "__main__":
    main()