import wave
import numpy as np
from numpy import fft
import spidev
import struct
import time

def read_song(song):
	return song.readframes(song.getnframes())
	
def unpack(frame):
	res = int.from_bytes(frame, 'little', signed = True) >> 4
	return res + 2048

def process(frames):
	split = [unpack(frames[i:i+2]) for i in range(0,len(frames),2)]
	return fft.ifft(fft.fft(split)).real	
	
def split_bytes(song_bytes):
	return [unpack(song_bytes[i:i+2]) for i in range(0, len(song_bytes),2)]
	
def chunk_frames(frame_array, length):
	return [frame_array[i:i+length] for i in range(0, len(frame_array),length)]
	
def process_fft(chunk):
	return fft.fft(chunk)
	
def process(bucket):
	return fft.ifft(bucket).real
	
def change_volume(bucket, percent):
	return bucket * (percent / 100)
	
if __name__ == '__main__':
	try:
		spi = spidev.SpiDev()
		spi.open(1,0)
		song = wave.open("closer.wav", 'rb')
		
		song_bytes = read_song(song)
		frame_array = split_bytes(song_bytes)
		buckets = [process_fft(chunk) for chunk in chunk_frames(frame_array, 1024)]
		print(len(buckets))
		print("Preprocessing done")
		for i, bucket in enumerate(buckets):
			if i > 500:
				bucket = change_volume(bucket,10)
			for frame in process(bucket):
				#print("Writing...")
				output = 0x3000 | int(frame)
				output_bytes = (output).to_bytes(2, 'big', signed=True)
				spi.writebytes(output_bytes)
		song.close()
		spi.close()
	except KeyboardInterrupt:
		song.close()
		spi.close()

	
	

