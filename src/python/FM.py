import aximem
import numpy as np
import threading
from ctypes import *
import time

class FM:
	def __init__(self,l=1024):
		self.l = l
		self.aximem = None
		self.rx_en = 0
		self.rx_stop = 1
		self.f = np.zeros(self.l)
		self.thread = threading.Thread(target = self.recv, name = 'fm')
	def config(self,c):
		self.aximem = aximem.aximem(c)

	def demod(self):
		d = np.frombuffer(string_at(self.aximem.dma.inp.data,self.l*4), dtype=np.int16, count=self.l*2, offset=0)
		iq = complex(1.,0.)*d[::2]+complex(0.,1.)*d[1::2]
		f = np.fft.fft(iq)
		f = np.fft.fftshift(f)
		self.f += 0.001*(np.abs(f)-self.f)

	def recv(self):
		while(True):
			if self.rx_en==0:
				time.sleep(0.1)
			else:
				start = self.aximem.dma.inp.end
				r = self.aximem.get(start,self.l*4)
				if r<0:
					self.aximem.reset("inp")
				elif r==0:
					time.sleep(0.01)
				else:
					self.demod()
			if self.rx_stop==1:
				break

	def stop(self):
		self.rx_stop = 1
		time.sleep(0.1)
	
	def en(self):
		self.rx_stop = 0
		self.rx_en = 1
		
	def exit(self):
		self.stop()
		

	def run(self):
		if self.aximem == None:
			return
		self.stop()
		self.en()
		self.thread.start()
		
	def dump(self):
		r = self.f.tolist()
		return r

			