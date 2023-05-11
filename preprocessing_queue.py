import wave
import numpy as np
from numpy import fft
import spidev
import struct
import time
import loading
import sys
import multiprocessing as mp

# ~ song = wave.open("closer.wav", 'rb')
# ~ n = 1024 # bucket frame length
# ~ framerate = song.getframerate()
# ~ timestep = 1./framerate
# ~ freqs = np.fft.rfftfreq(n, d=timestep)

# ~ LOW_STATIC_RANGE = 1

# ~ below_20 = np.asarray([1 if f > 20 else 0 for f in freqs])
# ~ above_20000 = np.asarray([1 if f < 17000 else 0 for f in freqs])
# ~ audio_band = above_20000

# ~ low_pass = np.asarray([1 if (LOW_STATIC_RANGE < f and f < 300) else 0 for f in freqs]) / 100
# ~ low_pass_inv = np.asarray([0 if (LOW_STATIC_RANGE < f and f < 300) else 1 for f in freqs]) 

# ~ mid_pass = np.asarray([1 if (300 <= f and f <= 4000) else 0 for f in freqs]) / 100
# ~ mid_pass_inv = np.asarray([0 if (300 <= f and f <= 4000) else 1 for f in freqs])

# ~ high_pass = np.asarray([1 if f > 4000 else 0 for f in freqs]) / 100
# ~ high_pass_inv = np.asarray([0 if f > 4000 else 1 for f in freqs])
	
# ~ def modulate(low_percent, mid_percent, high_percent):
	# ~ return (low_percent * low_pass + low_pass_inv) * (mid_percent * mid_pass + mid_pass_inv) * (high_percent * high_pass + high_pass_inv)

# ~ def unpack(frame):
	# ~ res = int.from_bytes(frame, 'little', signed = True) >> 4
	# ~ return res
	
# ~ def chunk_frames(frame_array, length):
	# ~ return [frame_array[i:i+length] for i in range(0, len(frame_array),length)]
	
# ~ def process_fft(chunk):
	# ~ return fft.rfftn(chunk) * audio_band
	
# ~ def make_buckets(song):
	# ~ song_bytes = song.readframes(song.getnframes())
	# ~ frame_list = [unpack(song_bytes[i:i+2]) for i in range(0, len(song_bytes),2)]
	# ~ buckets = [process_fft(chunk) for chunk in chunk_frames(frame_list, n)]
	# ~ return buckets

# ~ def change_volume(bucket, percent):
	# ~ return bucket * (percent / 100)

# ~ def process(bucket):
	# ~ return fft.irfft(bucket) + 2048
	
v = 50
b = 50
m = 50
t = 50
	
def main(q,p):
	global v, b, m, t
	while not q.empty():
		q.get()
	# ~ print(q.get())
	get = ''
	try:
		song_name = None
		while song_name is None:
			song_name = q.get()
		song = None
		while song is None:
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

		below_20 = np.asarray([1 if f > 20 else 0 for f in freqs])
		above_20000 = np.asarray([1 if f < 17000 else 0 for f in freqs])
		audio_band = above_20000

		low_pass = np.asarray([1 if (LOW_STATIC_RANGE < f and f < 300) else 0 for f in freqs]) / 100
		low_pass_inv = np.asarray([0 if (LOW_STATIC_RANGE < f and f < 300) else 1 for f in freqs]) 

		mid_pass = np.asarray([1 if (300 <= f and f <= 4000) else 0 for f in freqs]) / 100
		mid_pass_inv = np.asarray([0 if (300 <= f and f <= 4000) else 1 for f in freqs])

		high_pass = np.asarray([1 if f > 4000 else 0 for f in freqs]) / 100
		high_pass_inv = np.asarray([0 if f > 4000 else 1 for f in freqs])
		
		def modulate(low_percent, mid_percent, high_percent):
			return (low_percent * low_pass + low_pass_inv) * (mid_percent * mid_pass + mid_pass_inv) * (high_percent * high_pass + high_pass_inv)
			
		def unpack(frame):
			res = int.from_bytes(frame, 'little', signed = True) >> 4
			return res
			
		def chunk_frames(frame_array, length):
			return [frame_array[i:i+length] for i in range(0, len(frame_array),length)]
			
		def process_fft(chunk):
			return fft.rfftn(chunk)
			
		def make_buckets(song):
			song_bytes = song.readframes(song.getnframes())
			frame_list = [unpack(song_bytes[i:i+2]) for i in range(0, len(song_bytes),2)]
			buckets = [process_fft(chunk) for chunk in chunk_frames(frame_list, n)]
			return buckets[:-1]

		def change_volume(bucket, percent):
			return bucket * (percent / 100)

		def process(bucket):
			return fft.irfft(bucket) + 2048
		
		back_flag = False
		
		spi = spidev.SpiDev()
		spi.open(1,0)
		spi.max_speed_hz = 3000000
		buckets = make_buckets(song)
		print("Starting...")
		p.put('Ready')
		for i, bucket in enumerate(buckets):
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
			for frame in processed:
				# ~ print("Writing...")
				output = 0x3000 | int(frame)
				output_bytes = (output).to_bytes(2, 'big', signed=True)
				spi.writebytes(output_bytes)
		song.close()
		
		print(back_flag)
		while not back_flag:
			get = q.get()
			if get == 'back':
				print(get =='back')
				back_flag = True
		spi.close()
		main(q,p)
	except KeyboardInterrupt:
		song.close()
		spi.close()

if __name__ == '__main__':
    main(q,p)
	

