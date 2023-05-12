import wave
import numpy as np
from numpy import fft
import spidev
import struct
import time
import loading
import sys
import multiprocessing as mp

"""
Rosie Wildermuth (rjw252) and Jacob Tamor (jwt95)
Final Project: RPi DJ
04/11/2023
This code runs all of the audio preprocessing for the songs. It waits for
input from the shared queues it has with the interface code, then loads
the appropriate song, performs the FFT, mutates the song according to user
input, reverses the FFT, and then outputs the song through SPI to the DAC.
When the song ends, it waits for the user to exit back to the main screen
before rerunning the loop and waiting for a new song selection.
"""

# User Control Variables
v = 50
b = 50
m = 50
t = 50
	
def main(q,p):	# Preprocessing Main Function
	global v, b, m, t
	while not q.empty():	# Wait for a song selection
		q.get()
	# ~ print(q.get())
	get = ''
	try:
		song_name = None
		while song_name is None: # Get Sone input from queue
			song_name = q.get()
		song = None
		while song is None: # Quit or open the correct song accorind to queue output
			if song_name == 'Quit':
				sys.exit()
			elif song_name == 'Closer':
				song = wave.open("closer.wav", 'rb')
			elif song_name == 'Disturbia':
				song = wave.open("disturbia.wav", 'rb')
			elif song_name == 'Boom':
				song = wave.open("boomboompow.wav", 'rb')
			elif song_name == 'Thunderstruck':
				song = wave.open("thunderstruck.wav", 'rb')
			elif song_name == 'Thriller':
				song = wave.open("thriller.wav", 'rb')
			elif song_name == 'Poker':
				song = wave.open("pokerface.wav", 'rb')
			elif song_name == 'Let':
				song = wave.open("letitbe.wav", 'rb')
			elif song_name =='Love':
				song = wave.open("lovestory.wav", 'rb')

		n = 1024 # bucket frame length
		framerate = song.getframerate()
		timestep = 1./framerate
		freqs = np.fft.rfftfreq(n, d=timestep)
		
		LOW_STATIC_RANGE = 1
		
		# filter below 20 Hz
		below_20 = np.asarray([1 if f > 20 else 0 for f in freqs])
		above_20000 = np.asarray([1 if f < 17000 else 0 for f in freqs])
		audio_band = above_20000

		# Low Frequency Band
		low_pass = np.asarray([1 if (LOW_STATIC_RANGE < f and f < 300) else 0 for f in freqs]) / 100
		low_pass_inv = np.asarray([0 if (LOW_STATIC_RANGE < f and f < 300) else 1 for f in freqs]) 

		# Mid Frequency Band
		mid_pass = np.asarray([1 if (300 <= f and f <= 4000) else 0 for f in freqs]) / 100
		mid_pass_inv = np.asarray([0 if (300 <= f and f <= 4000) else 1 for f in freqs])

		# High Frequency Band
		high_pass = np.asarray([1 if f > 4000 else 0 for f in freqs]) / 100
		high_pass_inv = np.asarray([0 if f > 4000 else 1 for f in freqs])
		
		# Run modulation
		def modulate(low_percent, mid_percent, high_percent):
			return (low_percent * low_pass + low_pass_inv) * (mid_percent * mid_pass + mid_pass_inv) * (high_percent * high_pass + high_pass_inv)
		
		# Unpack Frames	
		def unpack(frame):
			res = int.from_bytes(frame, 'little', signed = True)
			return res
		
		# Chunk Frames	
		def chunk_frames(frame_array, length):
			return [frame_array[i:i+length] for i in range(0, len(frame_array),length)]
		
		# Perform FFT	
		def process_fft(chunk):
			return fft.rfftn(chunk)
		
		# Make Song Buckets	
		def make_buckets(song):
			song_bytes = song.readframes(song.getnframes())
			frame_list = [unpack(song_bytes[i:i+2]) for i in range(0, len(song_bytes),2)]
			buckets = [process_fft(chunk) for chunk in chunk_frames(frame_list, n)]
			return buckets[:-1]

		# Change Volume
		def change_volume(bucket, percent):
			return bucket * (percent / 100)
		
		# Proess Audio
		def process(bucket):
			return fft.irfft(bucket) + 2048
		
		back_flag = False
		
		# Set up SPI
		spi = spidev.SpiDev()
		spi.open(1,0)
		spi.max_speed_hz = 3000000
		buckets = make_buckets(song)
		print("Starting...")
		p.put('Ready')
		for i, bucket in enumerate(buckets): # Collect User Variables from Queue
			if not q.empty():
				get = q.get()
				# ~ print(get)
				if get == 'back':
					back_flag = True
					break
				elif get == 'Quit':
					sys.exit()
				elif get[0] == 'v':
					v = int(get[1:])
				elif get[0] == 'b':
					b = int(get[1:])
				elif get[0] == 'm':
					m = int(get[1:])
				elif get[0] == 't':
					t = int(get[1:])
			processed = process(change_volume(bucket * modulate(b,m,t), v))
			for frame in processed: 	# Output Bucket
				# ~ print("Writing...")
				output = 0x3000 | (int(frame) >> 4)
				output_bytes = (output).to_bytes(2, 'big', signed=True)
				spi.writebytes(output_bytes)
		song.close()
		
		print(back_flag)
		while not back_flag: # Wait for Back button after song ends
			get = q.get()
			if get == 'back':
				print(get =='back')
				back_flag = True
		spi.close()
		main(q,p) # Re-enter the loop
	except KeyboardInterrupt:
		song.close()
		spi.close()

if __name__ == '__main__':
    main(q,p)
	

