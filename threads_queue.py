import interface_queue, preprocessing_queue
import multiprocessing as mp
import sys
import time
from multiprocessing import Process, Queue, Value, Lock, Array

"""
Rosie Wildermuth (rjw252) and Jacob Tamor (jwt95)
Final Project: RPi DJ
04/11/2023
Thread code that runs both interface_queue and preprocessing_queue simultaneously
and instantiates their shared queues. Run this code to run the entire system.
"""

if __name__ == '__main__':
	
	# Create Queues
	ctx = mp.get_context('spawn')
	q = ctx.Queue()
	p = ctx.Queue()
	
	# Create Processes
	p0 = Process(target=interface_queue.main, args=(q,p))
	p1 = Process(target=preprocessing_queue.main, args=(q,p))
	
	# Start Processes
	p0.start()
	p1.start()
	
	# Join Processes
	p1.join()
	p0.join()

	sys.exit()	
