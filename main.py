# main.py -- put your code here!
import pyb
import _thread
import time
import queue
import random
import struct
import baudrate

lock=_thread.allocate_lock()
MESSAGE = 0
COMMAND = 1
RESET = 0#配置波特率后重启变量
BAUDLEN = 7#波特率长度关系到9600时循环发送出现的错误

#获取波特率
def getBaudRate():
	try:
		global RESET
		if(RESET == 1):
			baud = baudrate.getBaudrate()
		return baud
		print(RESET)
	except:
		baud = 9600
		return baud

Baudrate = getBaudRate()
uart1 = pyb.UART(2)
uart2 = pyb.UART(3)#温湿度传感器
uart3 = pyb.UART(6)#串口转网口
uart3.init(115200, bits=8, parity=None, stop=1)
uart2.init(Baudrate, bits=8, parity=None, stop=1)
uart1.init(Baudrate, bits=8, parity=None, stop=1)
q = queue.Queue(1000)
q1 = queue.Queue(100)
IDq = queue.Queue(200)
qList = []
senddata1 = b'\x02\x03\x00\x00\x00\x02\xc4\x38'
senddata3 = '03 03 00 00 00 02 C5 E9'
senddata4 = '01 03 00 00 00 02 C4 0B'
senddata2 = '030300010001d428'
delayTime = random.randint(0,20)*100



#加密
def encrypt(st, key):
	try:
		#alphaDict ,numDict = createDict()
		st1 = str(st, 'utf-8')
		alphaDict = createDict()
		numDict = array()
		newStr = ""
		for i in st1:
			if i in alphaDict:
				newNum = (int(alphaDict[i]) + int(key)) % 66
				#j = get_key(numDict, newNum)
				j = numDict[newNum]
				newStr += j
			else:
				newStr += str(i)
		return newStr
	except:
		pass
#解密	
def decrypt(st, key):
	try:
		alphaDict= createDict()
		numDict = array()
		newStr = ""
		for i in st:
			if i in alphaDict:
				newNum = (int(alphaDict[i]) - int (key)) % 66
				#j = get_key(numDict, newNum)
				j = numDict[newNum]
				newStr += j
			else:
				newStr += str(i)
		st1 = bytes(newStr, 'utf-8')
		return st1
	except:
		pass
#加密解密字典	
def createDict():
	newdict = {'a' : 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23, 'y': 24, 'z':25,'A': 26, 'B': 27, 'C': 28, 'D': 29, 'E': 30, 'F': 31, 'G': 32, 'H': 33, 'I': 34, 'J': 35, 'K': 36, 'L': 37, 'M': 38, 'N': 39, 'O': 40, 'P': 41, 'Q': 42, 'R': 43, 'S': 44, 'T': 45, 'U': 46, 'V': 47, 'W': 48, 'X': 49, 'Y': 50, 'Z': 51, '0': 52, '1': 53, '2': 54, '3': 55, '4': 56, '5': 57, '6': 58, '7': 59, '8': 60, '9': 61, ' ': 62, ':': 63, '(': 64, ')': 65}
	return newdict
def array():
	array = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ', ':', '(', ')']
	return array
#CRC16校验
def CRC16(data):
	a = 0xFFFF
	b = 0xA001
	for byte in data:
		a ^= ord(byte)
		for i in range(8):
			last = a % 2
			a >>= 1
			if last == 1:
				a ^= b
	s = hex(a).upper()
	return s[4:6]+s[2:4]

def getqList(q):
	n = q.size()
	IDList = [1]*n
	for i in range(0,n):
		data = q.items[i]
		message = messageunPack(data)
		IDList[i] = message[0]
	return IDList

def getMessageID():
	ID = random.randint(1,1000)
	list = getqList(q)
	n = len(list)
	for i in range(0,n):
		if (ID == list[i]):
	#递归查询消息ID是否重复
			getMessageID()
		else:
			return ID
	return ID

#消息打包转换为二进制
def messagePack(MessageID ,MessageType, DataLength, Data, CRC):
	PackData = struct.pack("3i10s4s",MessageID ,MessageType, DataLength, Data, CRC)
	return PackData
	
#消息解包转换为元组
def messageunPack(PackData):
	try:
		message = struct.unpack("3i10s4s",PackData)
		return message
	except:
		pass

def wdsd(wd , sd):
	wdstr = str(wd)
	sdstr = str(sd)
	length = len(sdstr)+len(wdstr)
	newstr = ''
	if (length < 10):
		strm = ' '*(10-length)
		newstr = wdstr+strm+sdstr
	elif(length > 10):
		if(len(wdstr) <= 5):
			strw = '0'*(5-len(wdstr))
			wdstr = wdstr + strw
		elif(len(wdstr) > 5):
			wdstr = wdstr[0:5]
		if(len(sdstr) <= 5):
			strs = '0'*(5-len(sdstr))
			sdstr = sdstr + strs
		elif(len(sdstr) > 5):
			sdstr = sdstr[0:5]
		newstr = wdstr+sdstr
	else:
		newstr = wdstr+sdstr
	return newstr

#将波特率写入文件
def txtFile(name,text): 
	xxoo = name + '.txt'#在当前py文件所在路径下的new文件中创建txt
	file = open(xxoo,'w')
	file.write(text)#写入内容信息
	file.close()  
	#print ('ok')

#发送数据包	
def sendToLora(uart):
	#time.sleep_ms(delayTime)
	while not q.isEmpty():
		data = q.dequeue()
		data1 = encrypt(data,1020)
		#uart.write(data1)
		time.sleep_ms(delayTime)
		uart.write(data)
		#print(data)
		#print(data1)
		print("The data dequeue is :")
		print(data)
		print("encrypt the data send to lora:")
		print(data1)
		print("The encrypt data send to lora")
		pyb.LED(4).on()
		pyb.delay(100)
		pyb.LED(4).off()
	while not q1.isEmpty():
		global RESET
		data = q1.dequeue()
		data1 = encrypt(data,1020)
		#uart.write(data1)
		time.sleep_ms(delayTime)
		uart.write(data)
		#print(data)
		#print(data1)
		RESET = 1
		pyb.LED(4).on()
		pyb.delay(100)
		pyb.LED(4).off()

#发送数据包到网口	
def sendToNet(uart):
	while not q.isEmpty():
		data = q.dequeue()
		message = messageunPack(data)
		#print(message)
		ID = message[0]
		id = str(ID)
		Data = message[3]
		Data1 =str(Data)
		#print(Data1)
		#print(len(Data1))
		wd = id +' '+Data1[2:7]
		sd = Data1[7:12]
		#uart.write(id)
		print("The data dequeue is :")
		print(data)
		print("The data send to NET is :")
		print(wd+'C '+sd+'%')
		uart.write(wd+'C '+sd+'%\n')
		pyb.LED(4).on()
		pyb.delay(100)
		pyb.LED(4).off()
#命令数据Date处理
def dataProcess(st1):
	try:
		st = str(st1)
		length = len(st)
		if (length > 10):
			newstr = st[0:10]
		elif (length < 10):
			newstr = st + ' '*(10-length)
		else:
			newstr = st
		return newstr
	except:
		pass

#接收串口配置数据	
def getFromNet(uart):
	if(uart.any()>0):
		global BAUDLEN
		pyb.LED(3).on()
		pyb.delay(100)
		pyb.LED(3).off()
		data = uart.read()
		data1 = str(data)
		n = len(data1)
		data2 = data1[2:(n-1)]
		#print(data1)
		BAUDLEN = n
		txtFile('baudrate',data2)#将配置数据写入文件
		MessageID = random.randint(1,100)
		MessageType = COMMAND
		Data = dataProcess(data)
		print(Data)
		print(type(Data))
		DataLength = len(Data)
		CRC = CRC16(str(MessageID)+str(MessageType)+str(DataLength)+Data)
		message = messagePack(MessageID ,MessageType, DataLength, Data, CRC)
		message1 = encrypt(message, 1020)
		'''
		print(MessageID)
		print(Data)
		print(type(Data))
		print(CRC)
		print(DataLength)
		print(message)
		print(message1)
		'''
		q1.enqueue(message)
		pyb.LED(2).on()
		pyb.delay(100)
		pyb.LED(2).off()
		uart.deinit()
		uart.init(115200, bits=8, parity=None, stop=1)

#波特率数据处理
def baudProcess(data):
	try:
		global BAUDLEN
		n = BAUDLEN+2
		baudstr = data[2:(n-1)]
		print(n)
		print(baudstr)
		return baudstr
	except:
		pass

def getCRC(st, n):
	newstr = ''
	if(n < 4):
		newstr = st[0:n]
	else:
		newstr = st
	return newstr

#接收数据	
def getFromLora(uart):
	if(uart.any()>0):
		pyb.LED(3).on()
		pyb.delay(100)
		pyb.LED(3).off()
		data = uart.read()
		data1 = encrypt(data,1020)
		data2 = decrypt(data1,1020)
		#message = messageunPack(data1)
		message = messageunPack(data)
		try:
			MessageID = message[0]
			MessageType = message[1]
			DataLength = message[2]
			Data = message[3]
			DAta = str(Data)
			DATA = str(Data,'utf-8')
			CRC = message[4]
			CRC1 = str(CRC, 'utf-8')
			newCRC = CRC16(str(MessageID)+str(MessageType)+str(DataLength)+DAta[2:12])
			CRC11 = getCRC(CRC1,len(newCRC))
			print("The data from lora is :")
			print(data1)
			print("decrypt the data from lora:")
			print(data)
			print("Unpack the data from lora:")
			print(message)
			'''
			print(CRC)
			print(len(CRC))
			print(len(CRC1))
			print(CRC1)
			print(type(CRC1))
			print(newCRC)
			print(CRC11)
			print(type(newCRC))
			print(len(newCRC))
			'''
			if(CRC11 == newCRC):
				if(MessageType == MESSAGE):
					#print('MESSAGE')
					list = getqList(q)
					print("The message queue ID is:")
					print(list)
					n = len(list)
					if(n>0):
						for i in range(0,n):
							if (MessageID == list[i]):
								pass
							else:
								IDlist = IDq.getItems()
								if MessageID in IDlist:
									print("The data from lora has been received recently")
									pass
								else:
									q.enqueue(data)
									IDq.enqueue(MessageID)
									clearIDq(IDq)
									print("The data from lora enqueue")
					else:
						print("The message queue ID is NULL")
						q.enqueue(data)
						IDq.enqueue(MessageID)
						clearIDq(IDq)
						print("The data from lora enqueue1")
						'''IDlist = IDq.getItems()
						m = len(IDlist)
						if (m == 0):
							q.enqueue(data)
							IDq.enqueue(MessageID)
							clearIDq(IDq)
							print("The data from lora enqueue1")
						else:
							if MessageID in IDlist:
								print("The data from lora has been received recently")
								pass
							else:
								q.enqueue(data)
								IDq.enqueue(MessageID)
								clearIDq(IDq)
								print("The data from lora enqueue1")'''
				if(MessageType == COMMAND):
					#print('incommand')
					bauddata = baudProcess(DATA)#待解决
					#print('incommand1')
					txtFile('baudrate',bauddata)#将配置数据写入文件
					#print('outcommand')
					q1.enqueue(data)
					#print('out')
		except:
			pass
		pyb.LED(2).on()
		pyb.delay(100)
		pyb.LED(2).off()
		uart.deinit()
		uart.init(Baudrate, bits=8, parity=None, stop=1)

def sendCommand(uart):
	if lock.acquire():#锁住资源
		time.sleep(5)
		uart.write(senddata1)
		pyb.LED(4).on()
		pyb.delay(100)
		pyb.LED(4).off()
		lock.release()#打开锁 释放资源

def dataProcess1(data):
	try:
		length = len(data)
		list = [1]*length
		newstr = ''
		for i in range(1 , length):
			str1 = data[i-1:i]
			str2 = ord(str1)
			list[i-1] = str2
		return list
	except:
		pass


def clearIDq(IDq):
	print("The size of IDq is:"+str(IDq.size()))
	if(IDq.size() > 100):
		IDq.clearQueue()

#采集数据	
def getData(uart):
	if(uart.any()>0):
		pyb.LED(2).on()
		pyb.delay(200)
		pyb.LED(2).off()
		newdata = uart.read()
		data11 = dataProcess1(newdata)
		try:
			wd1 = str( (data11[5] * 256 + data11[6]) / 100.0)
			sd = str( (data11[3] * 256 + data11[4]) / 100.0)
			MessageID = getMessageID()
			MessageType = MESSAGE
			Data = wdsd(wd1,sd)
			print("The data from sensor is :")
			print(newdata)
			print("The data has been processed is :")
			print(data11)
			print("The temperature is:"+wd1+'C')
			print("The humidity is:"+sd+'%')
			DataLength = len(Data)
			CRC = CRC16(str(MessageID)+str(MessageType)+str(DataLength)+Data)
			message = messagePack(MessageID ,MessageType, DataLength, Data, CRC)
			message1 = encrypt(message, 1020)
			print("Pack the data from sensor:")
			print(message)
			'''
			print(MessageID)
			print(Data)
			print(type(Data))
			print(CRC)
			print(DataLength)
			print(message)
			print(message1)
			'''
			q.enqueue(message)
			print("The sensor data enqueue")
			IDq.enqueue(MessageID)
			clearIDq(IDq)
		except:
			pass
		
		pyb.LED(2).on()
		pyb.delay(200)
		pyb.LED(2).off()
		uart.deinit()
		uart.init(Baudrate, bits=8, parity=None, stop=1)



if __name__=='__main__':
	while True:
		try:
			_thread.start_new_thread( sendToLora, (uart1,))
			_thread.start_new_thread( getData, (uart2,))
			_thread.start_new_thread( getFromLora, (uart1,))
			#_thread.start_new_thread( getFromNet, (uart3,))
			#_thread.start_new_thread( sendToNet, (uart3,))
			
			_thread.start_new_thread( sendCommand, (uart2,))
		except:
			pass