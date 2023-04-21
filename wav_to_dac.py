import wave
import numpy as np
import spidev
import struct
import time

spi = spidev.SpiDev()
spi.open(1,0)
spi.lsbfirst = False
spi.cshigh = False
# ~ spi.bits_per_word = 
# ~ print(spi.bits_per_word)
#spi.max_speed_hz = 20000000
#print(spi.max_speed_hz)

song = wave.open("closer48000.wav", 'rb')
# ~ print(song.getnframes())
# ~ print(song.getframerate())
print(song.getparams())
n = 1 #frame width

def process(frame):
	return frame
	
song.setpos(song.getnframes()//2)

for count in range(song.getnframes()//16):
	frame = process(song.readframes(n))
	unpack = int.from_bytes(frame, 'little', signed = True) >>4
	unpack = unpack + 2048
	output = 0b0011000000000000 | unpack 
	if (unpack < 0):
		print("False")
	output = (output).to_bytes(2, 'big',signed=True)
	spi.writebytes(output)
	
song.close()
spi.close()
