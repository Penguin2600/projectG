#!/usr/bin/env python
import time
import wiringpi
import collections


class SpiConnection(object):
    """Setus up vars for maintaining an SPI connection"""
    def __init__(self, clk, miso, mosi, cs):
        super(SpiConnection, self).__init__()
        self.clkpin = clk
        self.misopin = miso
        self.mosipin = mosi
        self.cspin = cs


class AdcChannel(object):
    """Sets up vars for maintaining an adc channel and its values"""
    def __init__(self, adcpin, mult, hysteresisHigh, hysteresisLow, plotOffset):
        super(AdcChannel, self).__init__()
        self.adcpin = adcpin
        self.multiplier = mult
        self.plotOffset = plotOffset
        self.hysteresisHigh = hysteresisHigh
        self.hysteresisLow = hysteresisLow
        self.hysteresisValue = 0
        self.smoothWidth = 6
        self.smoothedValue = 0
        self._currentValue = 0
        self._lastValue = 0
        self.average = collections.deque(maxlen=self.smoothWidth)

        for i in range(0, self.smoothWidth):
            self.average.append(0)

    def smooth_input(self):
        self.average.append(self.currentValue)
        self.smoothedValue = sum(self.average)/self.smoothWidth

    def apply_hysteresis(self):
        if self.smoothedValue > self.hysteresisHigh:
            self.hysteresisValue = 1
        if self.smoothedValue < self.hysteresisLow:
            self.hysteresisValue = 0

    @property
    def currentValue(self):
        return self._currentValue

    @currentValue.setter
    def currentValue(self, value):
        self._currentValue = value
        self.smooth_input()
        self.apply_hysteresis()

    @property
    def lastValue(self):
        return self._lastValue

    @lastValue.setter
    def lastValue(self, value):
        self._lastValue = value


class DataReconstructor(object):
    """Reconstructs incomming data"""
    def __init__(self, dataChannel, clockChannel):
        super(DataReconstructor, self).__init__()
        self.dataChannel = dataChannel
        self.clockChannel = clockChannel
        self.lastClock = 0
        self.recoveredData = []

    def process(self):

        if self.lastClock == 1 and self.clockChannel.hysteresisValue == 0:
            self.recoveredData.append(self.dataChannel.hysteresisValue)
        self.lastClock = self.clockChannel.hysteresisValue

        if len(self.recoveredData) == 8:
            self.decodeAscii(self.recoveredData)
            self.recoveredData = []

    def decodeAscii(byteStr):
        chrVal = 0
        bitPos = 8

        for bit in byteStr:
            bitPos -= 1
            if bit == "1":
                chrVal += (2**bitPos)

        return chr(chrVal)


class DataLogger(object):
    """Dumps values list to comma separated file"""
    def __init__(self, fileName):
        super(DataLogger, self).__init__()
        self.fileName = fileName
        self.dataFile = open(self.fileName, "w")
        self.dataFile.write('')
        self.dataFile.close()

    def log(self, *args):
        self.dataFile = open(self.fileName, "a")
        newLine = ','.join([repr(value) for index, value in enumerate(args)])
        self.dataFile.write(newLine)
        self.dataFile.write("\n")
        self.dataFile.close()


def init_wiringpi(sCon):

    wiringpi.wiringPiSetup()

    wiringpi.pinMode(sCon.mosipin, 1)
    wiringpi.pinMode(sCon.misopin, 0)
    wiringpi.pinMode(sCon.clkpin,  1)
    wiringpi.pinMode(sCon.cspin,   1)
    wiringpi.pullUpDnControl(sCon.misopin, 0)


def read_adc(adcnum, sCon):

    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    wiringpi.digitalWrite(sCon.cspin, 1)
    wiringpi.digitalWrite(sCon.clkpin, 0)  # start clock low
    wiringpi.digitalWrite(sCon.cspin, 0)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            wiringpi.digitalWrite(sCon.mosipin, 1)
        else:
            wiringpi.digitalWrite(sCon.mosipin, 0)
        commandout <<= 1
        wiringpi.digitalWrite(sCon.clkpin, 1)
        wiringpi.digitalWrite(sCon.clkpin, 0)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        wiringpi.digitalWrite(sCon.clkpin, 1)
        wiringpi.digitalWrite(sCon.clkpin, 0)
        adcout <<= 1
        if (wiringpi.digitalRead(sCon.misopin)):
            adcout |= 0x1
    wiringpi.digitalWrite(sCon.cspin, 1)

    adcout >>= 1       # first bit is 'null' so drop it
    return adcout


def main():

    step = 0

    sCon = SpiConnection(1, 4, 5, 6)
    init_wiringpi(sCon)

    redChannel = AdcChannel(0, 1.0, 112, 56, 0.0)
    greenChannel = AdcChannel(1, 1.0, 112, 56, 1.0)
    blueChannel = AdcChannel(2, 1.4, 112, 56, 2.0)

    reCon = DataReconstructor(redChannel, blueChannel)
    logger = DataLogger("data.txt")

    while True:
        step = step + 1
        redChannel.currentValue = read_adc(redChannel.adcpin, sCon) * redChannel.multiplier
        greenChannel.currentValue = read_adc(greenChannel.adcpin, sCon) * greenChannel.multiplier
        blueChannel.currentValue = read_adc(blueChannel.adcpin, sCon) * blueChannel.multiplier

        reCon.process()
        logger.log(step, redChannel.currentValue, greenChannel.currentValue, blueChannel.currentValue,
                   redChannel.smoothedValue, greenChannel.smoothedValue, blueChannel.smoothedValue,
                   redChannel.hysteresisValue*0.2, ((greenChannel.hysteresisValue*0.2)+0.3), ((blueChannel.hysteresisValue*0.2)+0.6))

        time.sleep(0.001)

if __name__ == "__main__":
    main()
