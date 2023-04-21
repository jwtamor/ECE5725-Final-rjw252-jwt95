import wave
import numpy as np
from numpy import fft
import spidev
import struct
import time

spi = spidev.SpiDev()
spi.open(1,0)
spi.lsbfirst = False
spi.cshigh = False
spi.max_speed_hz = 20000000

song = wave.open("closer.wav", 'rb')
print(song.getparams())
n = 1 #frame width

def unpack(frame):
	res = int.from_bytes(frame, 'little', signed = True) >> 4
	return res + 2048

def process(frames):
	split = [unpack(frames[i:i+2]) for i in range(0,len(frames),2)]
	return fft.ifft(fft.fft(split)).real
	
	
song.setpos(song.getnframes()//2)

for count in range(song.getnframes()//16):
	frame_array = process(song.readframes(1024))
	for frame in frame_array:
		print(frame)
		output = 0b0011000000000000 | int(frame)
		output = (output).to_bytes(2, 'big',signed=False)
		spi.xfer(output)

	
song.close()
spi.close()
