#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import threading
import time

from RF24 import *
import RPi.GPIO as GPIO

data = [0] * 32

radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)

radio.begin()
radio.setChannel(9)
radio.setPALevel(RF24_PA_MAX)
radio.setDataRate(RF24_250KBPS)
radio.setCRCLength(RF24_CRC_16)

radio.disableCRC()
radio.setPayloadSize(32)
radio.printDetails()
radio.setAddressWidth(2)
radio.openReadingPipe(1, 0x00AA)
radio.startListening()

radio.printDetails()

while(True):
    while(radio.available()):
    data = radio.read(32)
    print str(data).encode('hex')
