#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import threading
import time
import operator

from RF24 import *
import RPi.GPIO as GPIO

import select
import tty
import termios

stat = {}

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def setup(channel, address, data_rate, crc = 0):
    if not crc:
        radio.disableCRC()
    else:
        radio.setCRCLength(crc)
    radio.stopListening()
    radio.setPayloadSize(payload_size)
    time.sleep(0.01)
    radio.setDataRate(data_rate)
    radio.setChannel(channel)
 
    radio.openReadingPipe(1, address)
    radio.startListening()

old_settings = termios.tcgetattr(sys.stdin)


#address = [bytearray('00AA'.decode('hex')), bytearray('0055'.decode('hex'))]
address = [0x00AA, 0x0055]
address_index = 0
data_rate = [RF24_250KBPS, RF24_1MBPS, RF24_2MBPS]
data_rate_index = 0
crc = [0, RF24_CRC_8, RF24_CRC_16]
crc_index = 0
payload_size = 32
channel = 9
aack = False

radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)
radio.begin()
radio.setChannel(channel)
radio.setPALevel(RF24_PA_MAX)
radio.setAutoAck(aack)
radio.setDataRate(RF24_250KBPS)
radio.setAddressWidth(2)
radio.disableCRC()
radio.setPayloadSize(32)

setup(channel, address[address_index], data_rate[data_rate_index], crc[crc_index])
try:
    tty.setcbreak(sys.stdin.fileno())
    running = True
    while (running):
        if isData():
            if (1):
                c = sys.stdin.read(1)
                if c == '\x1b' or c == 'q' or c == 'Q':
                    tmp = raw_input('You want to quit? Y/N:\n')
                    if tmp == 'Y' or tmp == 'y':
                        running = False
                        break
                if c == '\x20':
                    radio.printDetails()
                    print sorted(stat.items(), key=operator.itemgetter(1), reverse=True)[:10]
                    tmp = raw_input('Press Enter to continue:\n')
                elif c == '\n':
                    print " 'q' - Quit\n ' ' - Info\n 'w' - channel++\n 's' - channel--\n 'z' - AutoAck\n '0' - clear Stat\n 'r' - change data rate\n 'e' - use next address\n 'a' - set address\n 'p' - set payload len\n 'c' - change crc\n '2-5' use address lenght"
                    tmp = raw_input('Press Enter to continue:\n')
                elif c == 'z' or c == 'Z':
                    aack = not aack
                    print 'autoack', aack
                    radio.setAutoAck(aack)
                elif c == 'w' or c == 'W':
                    channel = channel + 1
                    if channel > 127: channel = 127
                elif c == 's' or c == 'S':
                    channel = channel - 1
                    if channel < 0: channel = 0
                elif c == 'e' or c == 'E':
                    address_index = (address_index + 1) % len(address)
                    print 'address', address[address_index]
                elif c == 'r' or c == 'R':
                    data_rate_index = (data_rate_index + 1) % len(data_rate)
                    print 'data_rate', data_rate[data_rate_index]
                elif c == 'c' or c == 'C':
                    crc_index = (crc_index + 1) % len(crc)
                    print 'crc', crc[crc_index]
                elif c == 'a' or c == 'A':
                    tmp = raw_input('Enter address:\n')
                    address.append(int(tmp, 16))
                    address_index = len(address) - 1
                elif c == 'p' or c == 'P':
                    tmp = raw_input('Enter packet size:\n')
                    payload_size = int(tmp, 10)
                elif c == '0':
                    stat = {}
                elif c >= '2' and c <= '5':
                    tmp = int(c, 10)
                    radio.setAddressWidth(tmp)
                else:
                    print " 'q' - Quit\n ' ' - Info\n 'w' - channel++\n 's' - channel--\n 'z' - AutoAck\n '0' - clear Stat\n 'r' - change data rate\n 'e' - use next address\n 'a' - set address\n 'p' - set payload len\n 'c' - change crc\n '2-5' use address lenght"
                setup(channel, address[address_index], data_rate[data_rate_index], crc[crc_index])
                print 'Channel = %s, Address = %s Data Rate = %s AutoAck = %s' % (channel, hex(address[address_index]), data_rate[data_rate_index], aack)
                time.sleep(0.05)
            #except:
            #    pass
        while(radio.available()):
            data = radio.read(payload_size)
            hex_data = str(data).encode('hex')
            print hex_data
            try:
                num = hex(channel) + ' ' + hex_data[0:10]
                stat[num] = stat[num] + 1
            except:
                stat[num] = 1
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)