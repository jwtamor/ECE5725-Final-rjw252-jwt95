import wave
import numpy as np
from numpy import fft
import spidev
import struct
import time
import loading
	
def unpack(frame):
	res = int.from_bytes(frame, 'little', signed = True) >> 4
	return res + 2048
	
def chunk_frames(frame_array, length):
	return [frame_array[i:i+length] for i in range(0, len(frame_array),length)]
	
def process_fft(chunk):
	return fft.rfftn(chunk)
	
def make_buckets(song):
	song_bytes = song.readframes(song.getnframes())
	frame_list = [unpack(song_bytes[i:i+2]) for i in range(0, len(song_bytes),2)]
	buckets = [process_fft(chunk) for chunk in chunk_frames(frame_list, 1024)]
	return buckets

def change_volume(bucket, percent):
	return bucket * (percent / 100)

def process(bucket):
	return fft.irfft(bucket)
	
if __name__ == '__main__':
	try:
		spi = spidev.SpiDev()
		spi.open(1,0)
		song = wave.open("closer.wav", 'rb')
		buckets = make_buckets(song)
		for i, bucket in enumerate(buckets):
			processed = process(bucket)
			for frame in processed:
				#print("Writing...")
				output = 0x3000 | int(frame)
				output_bytes = (output).to_bytes(2, 'big', signed=True)
				spi.writebytes(output_bytes)
		song.close()
		spi.close()
	except KeyboardInterrupt:
		song.close()
		spi.close()

	
	

