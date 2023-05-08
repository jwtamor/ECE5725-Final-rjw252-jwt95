import interface
from multiprocessing import Process, Queue, Value, Lock, Array

def process1(y, x):
	for i in range(0,10):
		x = x + 1
	y.value = x

def process0(y, x):
	for i in range(0,10):
		x = x + 1
	y.value = x

if __name__ == '__main__':
	sum0 = Value('i', 0)
	sum1 = Value('i', 0)
	
	p0 = Process(target=interface.main)
	# ~ p0 = Process(target=interface.main)
	# ~ p1 = Process(target=process1, args=(sum1,5))
	
	p0.start()
	# ~ p1.start()
	
	
	# ~ p1.join()
	
	p0.join()
	
	print("DONE")
	# ~ print(sum0.value)
	# ~ print(sum1.value)
	
	
