#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Nrf
# Generated: Mon May 16 08:47:04 2016
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

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import osmosdr
import time
import wx


class nrf(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Nrf")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 4000000
        self.ch = ch = 25
        self.rf_gain = rf_gain = 0
        self.if_gain = if_gain = 20
        self.fsk_deviation_hz = fsk_deviation_hz = 170000
        self.freq_offset = freq_offset = -0
        self.fc = fc = 2399000000+ch*1000000
        self.bw = bw = samp_rate
        self.bitrate = bitrate = 250000
        self.bb_gain = bb_gain = 30

        ##################################################
        # Blocks
        ##################################################
        _rf_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._rf_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_rf_gain_sizer,
        	value=self.rf_gain,
        	callback=self.set_rf_gain,
        	label='rf_gain',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._rf_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_rf_gain_sizer,
        	value=self.rf_gain,
        	callback=self.set_rf_gain,
        	minimum=0,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.Add(_rf_gain_sizer)
        _if_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._if_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_if_gain_sizer,
        	value=self.if_gain,
        	callback=self.set_if_gain,
        	label='if_gain',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._if_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_if_gain_sizer,
        	value=self.if_gain,
        	callback=self.set_if_gain,
        	minimum=0,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.Add(_if_gain_sizer)
        _freq_offset_sizer = wx.BoxSizer(wx.VERTICAL)
        self._freq_offset_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_freq_offset_sizer,
        	value=self.freq_offset,
        	callback=self.set_freq_offset,
        	label='freq_offset',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._freq_offset_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_freq_offset_sizer,
        	value=self.freq_offset,
        	callback=self.set_freq_offset,
        	minimum=-1,
        	maximum=1,
        	num_steps=200,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_freq_offset_sizer)
        _bb_gain_sizer = wx.BoxSizer(wx.VERTICAL)
        self._bb_gain_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_bb_gain_sizer,
        	value=self.bb_gain,
        	callback=self.set_bb_gain,
        	label='bb_gain',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._bb_gain_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_bb_gain_sizer,
        	value=self.bb_gain,
        	callback=self.set_bb_gain,
        	minimum=0,
        	maximum=100,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.Add(_bb_gain_sizer)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="FFT Plot",
        	peak_hold=True,
        )
        self.Add(self.wxgui_fftsink2_0.win)
        self.osmosdr_source_0_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.osmosdr_source_0_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0_0.set_center_freq(fc, 0)
        self.osmosdr_source_0_0.set_freq_corr(0, 0)
        self.osmosdr_source_0_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0_0.set_gain_mode(True, 0)
        self.osmosdr_source_0_0.set_gain(rf_gain, 0)
        self.osmosdr_source_0_0.set_if_gain(if_gain, 0)
        self.osmosdr_source_0_0.set_bb_gain(bb_gain, 0)
        self.osmosdr_source_0_0.set_antenna("", 0)
        self.osmosdr_source_0_0.set_bandwidth(samp_rate, 0)
          
        self.low_pass_filter_0_0 = filter.fir_filter_fff(samp_rate/bitrate, firdes.low_pass(
        	1, samp_rate, bitrate, bitrate/2, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate, 2000000, 1000000, firdes.WIN_HAMMING, 6.76))
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        _ch_sizer = wx.BoxSizer(wx.VERTICAL)
        self._ch_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_ch_sizer,
        	value=self.ch,
        	callback=self.set_ch,
        	label='ch',
        	converter=forms.int_converter(),
        	proportion=0,
        )
        self._ch_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_ch_sizer,
        	value=self.ch,
        	callback=self.set_ch,
        	minimum=0,
        	maximum=128,
        	num_steps=128,
        	style=wx.SL_HORIZONTAL,
        	cast=int,
        	proportion=1,
        )
        self.Add(_ch_sizer)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, "tmp.raw", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_add_const_vxx_0 = blocks.add_const_vff((freq_offset, ))
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, -1000000, 1, 0)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.low_pass_filter_0_0, 0))    
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))    
        self.connect((self.blocks_add_const_vxx_0, 0), (self.digital_binary_slicer_fb_0, 0))    
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))    
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.wxgui_fftsink2_0, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.blocks_add_const_vxx_0, 0))    
        self.connect((self.osmosdr_source_0_0, 0), (self.blocks_multiply_xx_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_bw(self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 2000000, 1000000, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bitrate, self.bitrate/2, firdes.WIN_HAMMING, 6.76))
        self.osmosdr_source_0_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0_0.set_bandwidth(self.samp_rate, 0)
        self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)

    def get_ch(self):
        return self.ch

    def set_ch(self, ch):
        self.ch = ch
        self._ch_slider.set_value(self.ch)
        self._ch_text_box.set_value(self.ch)
        self.set_fc(2399000000+self.ch*1000000)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self._rf_gain_slider.set_value(self.rf_gain)
        self._rf_gain_text_box.set_value(self.rf_gain)
        self.osmosdr_source_0_0.set_gain(self.rf_gain, 0)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self._if_gain_slider.set_value(self.if_gain)
        self._if_gain_text_box.set_value(self.if_gain)
        self.osmosdr_source_0_0.set_if_gain(self.if_gain, 0)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self._freq_offset_slider.set_value(self.freq_offset)
        self._freq_offset_text_box.set_value(self.freq_offset)
        self.blocks_add_const_vxx_0.set_k((self.freq_offset, ))

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.osmosdr_source_0_0.set_center_freq(self.fc, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_bitrate(self):
        return self.bitrate

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.bitrate, self.bitrate/2, firdes.WIN_HAMMING, 6.76))

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self._bb_gain_slider.set_value(self.bb_gain)
        self._bb_gain_text_box.set_value(self.bb_gain)
        self.osmosdr_source_0_0.set_bb_gain(self.bb_gain, 0)


def main(top_block_cls=nrf, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()
