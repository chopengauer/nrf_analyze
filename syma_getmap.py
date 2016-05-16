#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import threading
import time
import re

isX5 = 0
chans = [0] * 4

def set_channels(address):
    global chans
    start_chans_1 = [0x0a, 0x1a, 0x2a, 0x3a]
    start_chans_2 = [0x2a, 0x0a, 0x42, 0x22]
    start_chans_3 = [0x1a, 0x3a, 0x12, 0x32]

    laddress = address & 0x1f

    num_rf_channels = 4;

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
        chans = [0x21, 0x41, 0x18, 0x38]
    else:
        chans = [0x21, 0x41, 0x19, 0x39]

def symax_init2(rx_tx_addr):
    chans_data_x5c = [0x1d, 0x2f, 0x26, 0x3d, 0x15, 0x2b, 0x25, 0x24, 0x27, 0x2c, 0x1c, 0x3e, 0x39, 0x2d, 0x22]
    if (isX5):
        global chans 
        chans = chans_data_x5c
    else:
        set_channels(rx_tx_addr[0])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        t = "a20009890f"
    else:
        t = sys.argv[1]

    s = [ord(i) for i in t.decode('hex')[-1::-1]]
    print s
    symax_init2(s)
    print re.sub(r'\[(.*)\]', r'\1',str(chans).replace(' ',''))
