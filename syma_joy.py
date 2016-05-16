#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import threading
import time

from RF24 import *
import RPi.GPIO as GPIO

ADDRESS_LEN = 5
BIND_CHANNEL = 9

def exp(value, koef=1.01, maximum=255):
    if value < 10:
        return value
    tmp = 160*(koef**(value)) / (koef**maximum)
    tmp = int(tmp) & 0xff
    return int(tmp)

def set_channels(address):
    num_rf_channels = 4
    chans = [0] *         num_rf_channels
    start_chans_1 = [0x0a, 0x1a, 0x2a, 0x3a]
    start_chans_2 = [0x2a, 0x0a, 0x42, 0x22]
    start_chans_3 = [0x1a, 0x3a, 0x12, 0x32]

    laddress = address & 0x1f

    if laddress < 0x10:
        if laddress == 6:
            laddress = 7
        for i in range(num_rf_channels):
            chans[i] = start_chans_1[i] + laddress
    elif (laddress < 0x18):
        for i in range(num_rf_channels):
            chans[i] = start_chans_2[i] + (laddress & 0x07)
        if (laddress == 0x16):
            chans[0] += 1
            chans[1] += 1
    elif (laddress < 0x1e):
        for i in range(num_rf_channels):
            chans[i] = start_chans_3[i] + (laddress & 0x07)
    elif (laddress == 0x1e):
        return [0x21, 0x41, 0x18, 0x38]
    else:
        return [0x21, 0x41, 0x19, 0x39]
    return chans

def symax_init2(isX5, rx_tx_addr):
    chans_data_x5c = [0x1d, 0x2f, 0x26, 0x3d, 0x15, 0x2b, 0x25, 0x24, 0x27, 0x2c, 0x1c, 0x3e, 0x39, 0x2d, 0x22]
    if (isX5):
        return chans_data_x5c
    else:
        return set_channels(rx_tx_addr[0])

class Syma(threading.Thread):
    def __init__(self, address):
        self.rx_tx_addr = [0]*ADDRESS_LEN
        self.address = int(address, 16)
        self.pipes =  [0xafaeadacab, self.address]
        for i in range(ADDRESS_LEN):
            self.rx_tx_addr[ADDRESS_LEN-1-i] = ord(address[2*i:2*i+2].decode('hex'))
        self.chans = symax_init2(0, self.rx_tx_addr)
        self.ch = 0
        self.chans_count = len(self.chans)
        self.packet_size = 10
        self.packet = [0] * self.packet_size
        self.running = 1
        self.bind = 0
        self.bind_prev = 0
        self.aileron  = 0
        self.elevator = 0
        self.throttle = 0
        self.rudder = 0

        print 'Address =', self.rx_tx_addr
        print 'Pipes =', self.pipes
        print 'Channels =', self.chans

        try:
            self.radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ)
            self.setup()
            pass
        except:
            print ("Error. No nrf module")
            exit(0)
        super(Syma, self).__init__()

    def setup(self):
        self.radio.begin()
        self.radio.setChannel(BIND_CHANNEL)
        self.radio.setDataRate(RF24_250KBPS)
        self.radio.setCRCLength(RF24_CRC_16)
        self.radio.setPayloadSize(self.packet_size)
        self.radio.setAutoAck(0)
        self.radio.setAddressWidth(ADDRESS_LEN)
        self.radio.openWritingPipe(self.pipes[0])

    def checksum(self, data):
        csum = data[0]
        for i in range(1, len(data)-1, 1):
            csum = (csum ^ data[i])
        return (csum + 0x55) % 256

    def build_packet(self):
        if (self.bind):
            self.packet[0] = self.rx_tx_addr[4]
            self.packet[1] = self.rx_tx_addr[3]
            self.packet[2] = self.rx_tx_addr[2]
            self.packet[3] = self.rx_tx_addr[1]
            self.packet[4] = self.rx_tx_addr[0]
            self.packet[5] = 0xaa
            self.packet[6] = 0xaa
            self.packet[7] = 0xaa
            self.packet[8] = 0x00
        else:
            self.packet[0] = self.throttle
            self.packet[1] = self.elevator
            self.packet[2] = self.rudder
            self.packet[3] = self.aileron
            self.packet[4] = 0x40
            self.packet[5] = 0x00#(elevator >> 2) | 0xc0;  // always high rates (bit 7 is rate control)
            self.packet[6] = 0x00#(rudder >> 2)   | (flags & FLAG_FLIP  ? 0x40 : 0x00);
            self.packet[7] = 0x00#aileron >> 2
            self.packet[8] = 0x00
        self.packet[9] = self.checksum(self.packet)

    def set_controls(self, aileron, elevator, throttle, rudder):
        self.aileron  = aileron
        self.elevator = elevator
        self.throttle = throttle
        self.rudder   = rudder

    def run(self):
        while (self.running):
            self.build_packet()
            if not self.bind and self.bind_prev:
                self.radio.openWritingPipe(self.pipes[1])
            if self.bind and not self.bind_prev:
                self.radio.setChannel(BIND_CHANNEL)
                self.radio.openWritingPipe(self.pipes[0])
            else:
                self.ch += 1
                self.ch = self.ch % self.chans_count
                self.radio.setChannel(self.chans[self.ch])
            self.radio.write(bytearray(self.packet))
            self.bind_prev = self.bind
            time.sleep(0.000001)

    def quit(self):
        self.running = 0

class App(threading.Thread):
    def __init__(self, address, joystick_file='/dev/hidraw0'):
        path = '/dev/'
        try:
            if not os.path.exists(joystick_file):
                file_list = [f for f in os.listdir(path) if f.startswith('hidr')]
                if file_list == []:
                    print ("No device hidraw")
                    exit(0)
                joystick_file = path + file_list[-1]
            self.joystick = open(joystick_file, 'r')
        except:
            print ("Error in init")
            #exit(0)
        super(App, self).__init__()
        self.syma = Syma(address)
        self.syma.start()

    def run(self):
        while (True):
            s = self.joystick.read(8)

            if (ord(s[6]) & 0x20):
                self.syma.quit()
                exit(0)

            if (ord(s[5]) & 0x10):
                self.syma.radio.openWritingPipe(self.syma.pipes[0])
                self.syma.bind = 1
            else:
                self.syma.bind = 0

            if (ord(s[5]) & 0x40):
                self.syma.radio.openWritingPipe(self.syma.pipes[1])

            if (ord(s[6]) & 0x10):
                self.syma.radio.printDetails()

            t = 2*(127 - ord(s[1]))
            if t < 0: 
                t = 0
            self.syma.throttle = exp(value=t)
            if (ord(s[6]) & 0x3):
                self.syma.throttle = 255
            #print self.syma.throttle, 255 - ord(s[1])
            #print s.encode('hex')

            t = ord(s[0])
            if t > 127:
                self.syma.rudder = t
            else:
                self.syma.rudder = 127 - t

            t = ord(s[4])
            if t > 127:
                self.syma.elevator = t
            else:
                self.syma.elevator = 127 - t

            t = ord(s[3])
            if t > 127:
                self.syma.aileron = t
            else:
                self.syma.aileron = 127 - t
            '''
            print 't', self.syma.throttle
            print 'r', self.syma.rudder
            print 'e', self.syma.elevator
            print 'a', self.syma.aileron
            '''
            time.sleep(0.0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app = App(address=sys.argv[1])
    else:
        app = App(address='a20009890f')
    app.start()
