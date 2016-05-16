#!/usr/bin/env python

import time

#preamb_def1 = [1,0,1,0,1,0,1,0]
#preamb_def1 = ['\x01','\x00','\x01','\x00','\x01','\x00','\x01','\x00']
#preamb_def2 = ['\x00','\x01','\x00','\x01','\x00','\x01','\x00','\x01']
#preamb_def1 = ['\x00\x01\x00\x01\x00\x01\x00\x01']
#preamb_def2 = ['\x01\x00\x01\x00\x01\x00\x01\x00']
preamb_def1 = 0xAA
preamb_def2 = 0x55

#preamb_def2 = [0,1,0,1,0,1,0,1]
#preamb_def2 = b'01010101'
#preamb = []
p_buff = []

#f_addr='\xf0\xf0\xf0\xf0\xf0' a20009890f
f_addr='\xa2\x00\x09\x89\x0f'

pay_len = 10

addr_len = 5

find_addr = False
show_badCRC = False
show_crc16 = True
show_crc8 = False
show_shockburst = False
show_simple = True
brute_len = False

color_base = {'grey':'\033[90m%s\033[0m', 'yellow':'\033[93m%s\033[0m', 'red':'\033[91m%s\033[0m', 'green':'\033[92m%s\033[0m','blue':'\033[94m%s\033[0m','purple':'\033[95m%s\033[0m','lblue':'\033[96m%s\033[0m'}
def color(string, color = 'grey'):
	if color in color_base:	return color_base[color] % string
	else: return color_base['grey'] % string

####### crc8 ###
def crc8_add(c):
        global crc8
        crc8 ^= c<<7
        crc8 <<= 1
        if (crc8 > 0xff):
                crc8 &= 0xff
                crc8 ^= 0x07


####### crc16 ###
def crc2_add(c):
	global crc2
        crc2 ^= c<<15
        crc2 <<= 1
        if (crc2 > 0xffff):
	        crc2 &= 0xffff
        	crc2 ^= 0x1021
######## crc16 ###

def make_byte(s):
	byt = s[0]<<7 | s[1]<<6 | s[2]<<5 | s[3]<<4 | s[4]<<3| s[5]<<2 | s[6]<<1 | s[7]
	return byt

if __name__=='__main__':
	print "Start"
#	fi = open('13M_2402_bin', 'rb')
	fi = open('13M_2402_crc8_bin', 'rb')
#	fi = open('/home/art/nrf/fifo', 'rb')
	pos1=0
	pos=0
	while True:
#		if len(p_buff) >= 340:
		if len(p_buff) >= 329:
			preamb = make_byte(p_buff[0:8])

                        if (preamb == preamb_def1) or (preamb == preamb_def2):
#				t = time.time()

#				buf3 =[]
				buf3 = p_buff[8:329]
				p_addr = ''
				## addr
				for k in range(addr_len):
					p_addr = p_addr + chr(make_byte(buf3[k*8:k*8+8]))
				## pcf
				p5_len = make_byte([0,0]+buf3[addr_len*8:addr_len*8+6])
#				print p5_len
				p5_id = make_byte([0,0,0,0,0,0]+buf3[addr_len*8+6:(addr_len+1)*8])
				p5_ack = make_byte([0,0,0,0,0,0,0]+buf3[(addr_len+1)*8:(addr_len+1)*8+1])
				## data
				for hh in range(0,33):
					p_data = ''
					p2_data = ''
					if p5_len >= 32: p5_len_c = 32
					else: p5_len_c = p5_len

					if brute_len:
						pay_len = hh
						p5_len_c = hh
						
					for k in range (p5_len_c):
						p_data = p_data + chr(make_byte(buf3[(addr_len+1+k)*8+1:(addr_len+2+k)*8+1]))
					for k in range (pay_len):
						p2_data = p2_data + chr(make_byte(buf3[(addr_len+k)*8:(addr_len+1+k)*8]))
				## crc
					p_crc8 = make_byte(buf3[(p5_len_c+addr_len+1)*8+1:(p5_len_c+addr_len+2)*8+1])	
					p_crc = (p_crc8<<8) + make_byte(buf3[(p5_len_c+addr_len+2)*8+1:(p5_len_c+addr_len+3)*8+1])
					p2_crc8 = make_byte(buf3[(addr_len+pay_len)*8:(addr_len+pay_len+1)*8])
					p2_crc = (p2_crc8<<8) + make_byte(buf3[(addr_len+pay_len+1)*8:(addr_len+pay_len+2)*8])
				## calc crc8
					crc8=0xff
					for k in range ((addr_len+1+p5_len_c)*8+1):
          	                              crc8_add(buf3[k])
                	                p_crc8_calc=crc8
                        	        crc8 = 0xff
                               	 	for k in range ((addr_len+pay_len)*8):
                                        	crc8_add(buf3[k])
                                	p2_crc8_calc=crc8
				## calc crc82
					crc8 = 0xff
					for k in range(10*8):
						crc8_add(buf3[4*8+k])
					crc82 = crc8
					
				
				## calc crc
					crc2 = 0xffff
					for k in range ((addr_len+1+p5_len_c)*8+1):
						crc2_add(buf3[k])
					p_crc_calc=crc2
					crc2 = 0xffff
					for k in range ((addr_len+pay_len)*8):
						crc2_add(buf3[k])
					p2_crc_calc=crc2
				
					addr = ''.join("{:02x}".format(ord(c)) for c in p_addr)
					p2ata = ''.join("{:02x}".format(ord(c)) for c in p2_data)
#				p2crc = ''.join("{:02x}".format(ord(c)) for c in p2_crc)
					p2crc = p2_crc
#				p2crc8 = ''.join("{:02x}".format(ord(c)) for c in p2_crc8)
					p2crc8 = p2_crc8
					pata = ''.join("{:02x}".format(ord(c)) for c in p_data)
#				pcrc = ''.join("{:02x}".format(ord(c)) for c in p_crc)
					pcrc = p_crc
#				pcrc8 = ''.join("{:02x}".format(ord(c)) for c in p_crc8)
					pcrc8 = p_crc8
					if p2_crc == p2_crc_calc and show_crc16 and show_simple:
						print color("0Position "+str(pos)+"\toffset "+str(pos-pos1)+"\tAddress " + addr  + "\tData "+p2ata+"\tCRC "+ format(p2crc,'04x')+"\tLen "+str(pay_len) + ' preamb = ' + format(preamb,'02x'), "green")
#						for k in range(addr_len+p5_len_c+2): del p_buff[0]
						pos1=pos
					elif p_crc == p_crc_calc and show_crc16 and show_shockburst:
						print color("1Position "+str(pos)+"\toffset "+str(pos-pos1)+"\tAddress " + addr +"\tLen "+str(p5_len)+"\tpID "+str(p5_id)+"\tack "+str(p5_ack)+ "\tData "+pata+"\tCRC "+ format(pcrc,'04x')+"\tLen "+str(pay_len), "green")
#					for k in range(addr_len+p5_len_c+2): del p_buff[0]
						pos1=pos
        	                        elif p2_crc8 == p2_crc8_calc and show_crc8 and show_simple:
                	                        print color("2Position "+str(pos)+"\toffset "+str(pos-pos1)+"\tAddress " + addr  + "\tData "+p2ata+"\tCRC "+ format(p2crc8,'02x')+"\tLen "+str(pay_len), "green")
                        	                pos1=pos
                                	elif p_crc8 == p_crc8_calc and show_crc8 and show_shockburst:
                                        	print color("3Position "+str(pos)+"\toffset "+str(pos-pos1)+"\tAddress " + addr +"\tLen "+str(p5_len)+"\tpID "+str(p5_id)+"\tack "+str(p5_ack)+"\tData "+pata+"\tCRC "+ format(pcrc8,'02x')+"\tLen "+str(pay_len), "green")
	                                        pos1=pos
					elif (p_addr == f_addr) & find_addr:
						if show_simple: print color("4Position "+str(pos)+"\tAddress " + addr  + "\tData "+p2ata+"\tCRC "+ format(p2crc,'04x')+"\tLen "+str(pay_len), "yellow")
						if show_shockburst: print color("5Position "+str(pos)+"\tAddress " + addr +"\tLen "+str(p5_len)+"\tpID "+str(p5_id)+"\tack "+str(p5_ack)+ "\tData "+pata+"\tCRC "+ format(pcrc,'04x')+"\tLen "+str(pay_len), "yellow")
					elif show_badCRC:
						if show_simple: print color("6Position "+str(pos)+"\tAddress " + addr  + "\tData "+p2ata+"\tCRC "+ format(p2crc,'02x')+"\tLen "+str(pay_len), "red")
						if show_shockburst: print color("7Position "+str(pos)+"\tAddress " + addr +"\tLen "+str(p5_len)+"\tpID "+str(p5_id)+"\tack "+str(p5_ack)+ "\tData "+pata+"\tCRC "+ format(pcrc,'04x')+"\tLen "+str(pay_len), "red")



					if not brute_len:
						break
#				print "proc",(time.time()-t)*1000000

				
#			p_buff = p_buff[1:] 
#			p_buff.pop(0)
			del p_buff[0]
			pos +=1
                else:
#			t = time.time()
                        buf = fi.read(4096)
                        if not buf: break
			for j in buf:
				p_buff.append(ord(j))


