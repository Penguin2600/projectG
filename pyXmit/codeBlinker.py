#!/usr/bin/env python

import sys
import pygame
import time


def a2b(a):
    ai = ord(a)
    return ''.join('01'[(ai >> x) & 1] for x in xrange(7, -1, -1))

def do_fill(screen, color):

    screen.fill(color)
    pygame.display.flip()

def do_transmit(screen,data,transmitMode,clockSpeed):

    clockState=0
    dataState=0
    bitStream=""

    for char in data:
        dataPointer=-1
        clockCount=1
        print char
        bitStream=a2b(char)
        print bitStream
        dataState=bitStream[dataPointer]

        while clockCount <= (len(bitStream)*2):

            clockState = clockCount % 2

            if clockState:
                dataPointer+=1
                dataState=bitStream[dataPointer]

            xord = clockState ^ int(dataState);
          
            if (transmitMode==1):
                redValue=(xord*255);
                greenValue=0
                blueValue=0
                
            if (transmitMode==2):
                redValue=(int(dataState)*255);
                greenValue=0
                blueValue=(clockState*255);
                

            color=(redValue, greenValue, blueValue)
            do_fill(screen,color)
            time.sleep((1.0/clockSpeed))

            clockCount+=1

if __name__ == "__main__":

    pygame.init()

    size = width, height = 320, 240
    data = "Data"
    screen = pygame.display.set_mode(size)
    transmitMode=2
    clockSpeed=10.0

    while 1:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_SPACE :
                        do_fill(screen,(0,0,0))
                        time.sleep(1)
                        do_transmit(screen,data,transmitMode,clockSpeed)
                        do_fill(screen,(0,0,0))
                        time.sleep(1)
                
