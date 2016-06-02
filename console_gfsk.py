#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Gfsk
# Generated: Mon May 30 18:44:29 2016
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import osmosdr
import time
#import wx
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Gfsk")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.ch = ch = 25
        self.rf_gain = rf_gain = 0
        self.if_gain = if_gain = 20
        self.fsk_deviation_hz = fsk_deviation_hz = 170000
        self.fc = fc = 2400000000+ch*1000000
        self.bw = bw = samp_rate
        self.bitrate = bitrate = 250000
        self.bb_gain = bb_gain = 30

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink( args="numchan=" + str(1) + " " + "" )
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(fc, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(rf_gain, 0)
        self.osmosdr_sink_0.set_if_gain(if_gain, 0)
        self.osmosdr_sink_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_sink_0.set_antenna("", 0)
        self.osmosdr_sink_0.set_bandwidth(samp_rate, 0)
          
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
        	samples_per_symbol=samp_rate/bitrate,
        	sensitivity=0.5,
        	bt=0.5,
        	verbose=False,
        	log=False,
        )
        self.blocks_vector_source_x_1 = blocks.vector_source_b([0x00, 0xaa, 0xa2, 0x00, 0x09, 0x89, 0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x95, 0x7f, 0x1e]+ [0x00]*100, True, 1, [])
        (self.blocks_vector_source_x_1).set_min_output_buffer(0)
        (self.blocks_vector_source_x_1).set_max_output_buffer(0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_vector_source_x_1, 0), (self.digital_gfsk_mod_0, 0))    
        self.connect((self.digital_gfsk_mod_0, 0), (self.osmosdr_sink_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.osmosdr_sink_0.set_bandwidth(self.samp_rate, 0)
        self.set_bw(self.samp_rate)

    def get_ch(self):
        return self.ch

    def set_ch(self, ch):
        self.ch = ch
        self.set_fc(2400000000+self.ch*1000000)
        self._ch_slider.set_value(self.ch)
        self._ch_text_box.set_value(self.ch)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self._rf_gain_slider.set_value(self.rf_gain)
        self._rf_gain_text_box.set_value(self.rf_gain)
        self.osmosdr_sink_0.set_gain(self.rf_gain, 0)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self._if_gain_slider.set_value(self.if_gain)
        self._if_gain_text_box.set_value(self.if_gain)
        self.osmosdr_sink_0.set_if_gain(self.if_gain, 0)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.osmosdr_sink_0.set_center_freq(self.fc, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_bitrate(self):
        return self.bitrate

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self._bb_gain_slider.set_value(self.bb_gain)
        self._bb_gain_text_box.set_value(self.bb_gain)
        self.osmosdr_sink_0.set_bb_gain(self.bb_gain, 0)


if __name__ == '__main__':
    tb = top_block()
    tb.start()
    tb.blocks_vector_source_x_1.set_data([0x00, 0xaa, 0x00])
    tb.blocks_vector_source_x_1.set_data([0x00, 0xaa, 0x11])
    tb.blocks_vector_source_x_1.set_data([0x00, 0xaa, 0x22])
    raw_input('Press Enter to quit: ')
    tb.stop()
    tb.wait()
