from smbus2 import SMBusWrapper
from enum import Enum
import sys, getopt
import time

class rangeType_T(Enum):
	RANGE_NONE = 0
	RANGE_SINGLE = 1
	RANGE_CONTINOUS = 2
	RANGE_TIMER = 3

class rangeConfiguration_T(Enum):
	DEFAULT_MODE = 0
	SHORT_RANGE_HIGH_SPEED = 1
	DEFAULT_RANGE_HIGHER_SPEED_SHORT_RANGE = 2
	MAXIMUM_RANGE = 3
	HIGH_SENSIVITY = 4
	LOW_SENSIVITY = 5
	SHORT_RANGE_HIGH_SPEED_HIGHER_ERROR = 6
	
class configurationBase:
	#default values
	sigCountMax = 0x80
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0x00
	
class configurationShortRangeHighSpeed(configurationBase):
	sigCountMax = 0x1d
	acqConfigReg = 0x08
	refCountMax = 0x03
	thresholdBypass = 0x00
	
class configurationDefaultRangeHigherSpeed(configurationBase):
	sigCountMax	= 0x80
	acqConfigReg = 0x00
	refCountMax = 0x03
	thresholdBypass = 0x00
	
class configurationMaximumRange(configurationBase):
	sigCountMax = 0xff
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0x80
	
class configurationHighSensivity(configurationBase):
	sigCountMax = 0x80
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0x80

class configurationLowSensivity(configurationBase):
	sigCountMax = 0x80
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0xb0

class configurationShortRangeHighSpeedHigherError(configurationBase):
	sigCountMax = 0x04
	acqConfigReg = 0x01
	refCountMax = 0x03
	thresholdBypass = 0x00

def writeConfig(bus,config,lidarliteAddress):
	print(config.sigCountMax)
	print(config.acqConfigReg)
	print(config.refCountMax)
	print(config.thresholdBypass)	
		
	bus.write_byte_data(lidarliteAddress,0x02,config.sigCountMax)
	bus.write_byte_data(lidarliteAddress,0x04,config.acqConfigReg)
	bus.write_byte_data(lidarliteAddress,0x12,config.refCountMax)
	bus.write_byte_data(lidarliteAddress,0x1c,config.thresholdBypass)

def configure(bus,configuration,lidarliteAddress):
	if configuration == rangeConfiguration_T.DEFAULT_MODE:
		config = configurationBase()
	elif configuration == rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED:
		config = configurationShortRangeHighSpeed()
	elif configuration == rangeConfiguration_T.DEFAULT_RANGE_HIGHER_SPEED_SHORT_RANGE:
		config = configurationShortRangeHighSpeed()
	elif configuration == rangeConfiguration_T.MAXIMUM_RANGE:
		config = configurationMaximumRange()
	elif configuration == rangeConfiguration_T.HIGH_SENSIVITY:
		config = configurationHighSensivity()
	elif configuration == rangeConfiguration_T.LOW_SENSIVITY:
		config = configurationLowSensivity()
	elif configuration == rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED_HIGHER_ERROR:
		config = configurationShortRangeHighSpeedHigherError()
	else:
		sys.exit()
	
	writeConfig(bus,config,lidarliteAddress)
	

def getReadyFlag(bus,devAddress):
	#device is ready when the LSB of DEVICE_ADDRESS register is 0
	byteBusyFlag = bus.read_byte_data(devAddress, 0x01) #read_i2c_block_data
	busyflag = byteBusyFlag % 2
	if busyflag == 0:
		return True
	else:
		return False

def waitForReadyState(bus, devAddress):
	i = 0
	while getReadyFlag(bus,devAddress) == False:
		i = i + 1
		if i > 9999:
			print('No response that device is in ready state')
			sys.exit()
			
def takeMeasure(bus,devAddress):
	bus.write_byte_data(devAddress,0x00,0x01)
	
def readDistance(bus,devAddress):
	blockData = bus.read_i2c_block_data(devAddress, 0x0f, 2)
	distance = (int)(blockData[0] << 8) | blockData[1]
	return distance


### Lidar Working Modes Functions ###
def singleMeasureMode(bus):
	DEVICE_ADDRESS = 0x62
	DEVICE_READYFLAG = 0x01
	DEVICE_TAKEMES = 0x00
	
	# 1. Wait to indicate if device is idle. This must be
    #    done before triggering a range measurement.	
	waitForReadyState(bus,DEVICE_ADDRESS)
		
	# 2. Trigger range measurement.	
	takeMeasure(bus,DEVICE_ADDRESS)
	
	# 3. Wait to indicate if device is idle. This should be
    #    done before reading the distance data that was triggered above.	
	waitForReadyState(bus,DEVICE_ADDRESS)

	# 4. Read new distance data from device registers
	distance = readDistance(bus,DEVICE_ADDRESS)
	
	print(distance)
	
def noneMeasureMode():
	distance = 0
	print(distance)

def continuousMeasureMode(bus):
	DEVICE_ADDRESS = 0x62
	while(True):
		# 1. Wait to indicate if device is idle. This must be
		#    done before triggering a range measurement.	
		waitForReadyState(bus,DEVICE_ADDRESS)
		
		# 2. Trigger range measurement.	
		takeMeasure(bus,DEVICE_ADDRESS)
		
		# 3. Read new distance data from device registers
		distance = readDistance(bus,DEVICE_ADDRESS)
	
		print(distance)
		
def timerMeasureMode(bus, timeInSeconds):
	DEVICE_ADDRESS = 0x62
	while(True):
		# 1.  Wait Given Time
		time.sleep(timeInSeconds)
		
		# 2. Wait to indicate if device is idle. This must be
		#    done before triggering a range measurement.	
		waitForReadyState(bus,DEVICE_ADDRESS)
		
		# 3. Trigger range measurement.	
		takeMeasure(bus,DEVICE_ADDRESS)
		
		# 4. Read new distance data from device registers
		distance = readDistance(bus,DEVICE_ADDRESS)
	
		print(distance)
	
def main(argv):
	dictConfiguration = {
	"default" : rangeConfiguration_T.DEFAULT_MODE,
	"0" : rangeConfiguration_T.DEFAULT_MODE,
	"hspeedsrange" : rangeConfiguration_T.DEFAULT_RANGE_HIGHER_SPEED_SHORT_RANGE,
	"1" : rangeConfiguration_T.DEFAULT_RANGE_HIGHER_SPEED_SHORT_RANGE,
	"hsensivity" : rangeConfiguration_T.HIGH_SENSIVITY,
	"2" : rangeConfiguration_T.HIGH_SENSIVITY,
	"lsensivity" : rangeConfiguration_T.LOW_SENSIVITY,
	"3" : rangeConfiguration_T.LOW_SENSIVITY,
	"maxrange" : rangeConfiguration_T.MAXIMUM_RANGE,
	"4" : rangeConfiguration_T.MAXIMUM_RANGE,
	"srangehspeed": rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED,
	"5": rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED,
	"srangehspeedherror" : rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED_HIGHER_ERROR,
	"6" : rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED_HIGHER_ERROR}
	
	dictMode = {
	"single" : rangeType_T.RANGE_SINGLE,
	"0" : rangeType_T.RANGE_SINGLE,
	"continuous" : rangeType_T.RANGE_CONTINOUS,
	"1" : rangeType_T.RANGE_CONTINOUS,
	"none" : rangeType_T.RANGE_NONE,
	"2" : rangeType_T.RANGE_NONE,
	"timer" : rangeType_T.RANGE_TIMER,
	"0" : rangeType_T.RANGE_TIMER
	}
	mode = rangeType_T.RANGE_SINGLE
	setting = rangeConfiguration_T.DEFAULT_MODE
	timeInSeconds = 0.1
	try:
		opts, args = getopt.getopt(argv,"hm:s:t:",["mode=","setting=","time="])
	except getopt.GetoptError:
		print 'test.py -m <mode> -s <setting> -t <time>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -m <mode> -s <setting> -t <time>'
			sys.exit()
		elif opt in ("-m", "--mode"):
			if arg in dictMode:
				mode = dictMode[arg]
			else:
				print 'wrong mode parameter'
				sys.exit()
		elif opt in ("-s", "--setting"):
			if arg in dictConfiguration:
				setting = dictConfiguration[arg]
			else:
				print 'wrong setting parameter'
				sys.exit()
		elif opt in ("-t", "--time"):
			try:
				timeInSeconds = float(arg)
			except VALUE_ERROR:
				print('Time argument must be a number')
				sys.exit()
			if timeInSeconds <= 0:
				print('Time must be a positive value')
				sys.exit()
				
	print 'mode is "', mode
	print 'setting is "', setting
	print 'time = ', timeInSeconds		
			
	with SMBusWrapper(1) as bus: # 1 = /dev/i2c-1

		DEVICE_ADDRESS = 0x62
		DEVICE_READYFLAG = 0x01
		DEVICE_TAKEMES = 0x00

		configure(bus,setting, DEVICE_ADDRESS)
		
		if mode == rangeType_T.RANGE_NONE:
			noneMeasure()
		elif mode == rangeType_T.RANGE_SINGLE:
			singleMeasureMode(bus)
		elif mode == rangeType_T.RANGE_CONTINOUS:
			try:
				continuousMeasureMode(bus)
			except (KeyboardInterrupt, SystemExit):
				sys.exit()
		elif mode == rangeType_T.RANGE_TIMER:
			try:
				timerMeasureMode(bus, timeInSeconds)
			except (KeyboardInterrupt, SystemExit):
				sys.exit()
		else:
			print('Error no mode given')
			sys.exit()


if __name__ == "__main__":
   main(sys.argv[1:])
