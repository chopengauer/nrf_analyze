#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import threading
import time
import operator

from RF24 import *
import RPi.GPIO as GPIO

data = [0] * 32
scan_flag = 0
stat = {}

CHANNELS  = range(9, 10)
CHANNELS  = range(25, 26)

TIME = 10

radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)

radio.begin()
radio.setChannel(9)
radio.setPALevel(RF24_PA_MAX)
#radio.setDataRate(RF24_250KBPS)
radio.setDataRate(RF24_1MBPS)
#radio.setCRCLength(RF24_CRC_16)
radio.disableCRC()
radio.setPayloadSize(32)
radio.setAddressWidth(3)
radio.openReadingPipe(1, 0x00)
radio.startListening()

#radio.printDetails()

class ScanAddress(threading.Thread):
    def __init__(self, channel, address):
        threading.Thread.__init__(self)
        self.address = address
        self.channel = channel
        self.event = threading.Event()
        radio.stopListening()
        radio.setChannel(self.channel)
        radio.setAddressWidth(3)
        radio.openReadingPipe(1, self.address)
        #radio.printDetails()
        radio.startListening()

    def run(self):
        while (not self.event.is_set()):
            while(radio.available()):
                data = radio.read(32)
                hex_data = str(data).encode('hex')
                print hex_data
                num = hex(self.channel) + ' ' + hex(((self.address & 0xff) << 8) + data[0])#str(data).encode('hex')[:2]
                try:
                    stat[num] = stat[num] + 1
                except:
                    stat[num] = 1
                #self.event.wait(1)

    def stop(self):
        self.event.set()

def scan_channel(channel, radio):
    address = 0

#    for i in range(170, 176):
    for i in range(0, 256):
        if i & 0x80:
            address = (0xAA<<8)+i
        else:
            address = (0x55<<8)+i
        print '<channel = %s> Scanning address = %s' % (channel, hex(address))
        t = ScanAddress(channel, address)
        t.start()
        time.sleep(TIME)
        t.stop()

for channel in CHANNELS:
    scan_channel(channel, radio=radio)

print sorted(stat.items(), key=operator.itemgetter(1), reverse=True)[:10]

'''
radio.setAddressWidth(3)
radio.openReadingPipe(1, 0x00AAAF)
radio.startListening()
radio.printDetails()
while(True):
    while(radio.available()):
    data = radio.read(32)
    print str(data).encode('hex')
'''
