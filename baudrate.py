import os

def getBaudrate():
	try:
		f=open('baudrate.txt','r')
		baud = f.read()
		return baud
	except:
		pass