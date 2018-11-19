from smbus2 import SMBusWrapper
from enum import Enum
import sys, getopt

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

def writeConfig(config,lidarliteAddress):
	with SMBusWrapper(1) as bus:
		print(config.sigCountMax)
		print(config.acqConfigReg)
		print(config.refCountMax)
		print(config.thresholdBypass)
		
		bus.write_byte_data(lidarliteAddress,0x02,config.sigCountMax)
		bus.write_byte_data(lidarliteAddress,0x04,config.acqConfigReg)
		bus.write_byte_data(lidarliteAddress,0x12,config.refCountMax)
		bus.write_byte_data(lidarliteAddress,0x1c,config.thresholdBypass)

def configure(configuration,lidarliteAddress):
	if configuration == rangeConfiguration_T.DEFAULT_MODE:
		config = configurationBase()
		writeConfig(config,lidarliteAddress)
	elif configuration == rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED:
		config = configurationShortRangeHighSpeed()
		writeConfig(config,lidarliteAddress)
	elif configuration == rangeConfiguration_T.DEFAULT_RANGE_HIGHER_SPEED_SHORT_RANGE:
		config = configurationShortRangeHighSpeed()
		writeConfig(config,lidarliteAddress)
	elif configuration == rangeConfiguration_T.MAXIMUM_RANGE:
		config = configurationMaximumRange()
		writeConfig(config,lidarliteAddress)
	elif configuration == rangeConfiguration_T.HIGH_SENSIVITY:
		config = configurationHighSensivity()
		writeConfig(config,lidarliteAddress)
	elif configuration == rangeConfiguration_T.LOW_SENSIVITY:
		config = configurationLowSensivity()
		writeConfig(config,lidarliteAddress)
	elif configuration == rangeConfiguration_T.SHORT_RANGE_HIGH_SPEED_HIGHER_ERROR:
		config = configurationShortRangeHighSpeedHigherError()
		writeConfig(config,lidarliteAddress)

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
	try:
		opts, args = getopt.getopt(argv,"hm:s:",["mode=","setting="])
	except getopt.GetoptError:
		print 'test.py -m <mode> -s <setting>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -m <mode> -s <setting>'
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
	print 'mode is "', mode
	print 'Output file is "', setting		
	
	
	DEVICE_ADDRESS = 0x62
	
	
	configure(rangeConfiguration_T.HIGH_SENSIVITY, DEVICE_ADDRESS)
			
	with SMBusWrapper(1) as bus: # 1 = /dev/i2c-1

		
		DEVICE_READYFLAG = 0x01
		DEVICE_TAKEMES = 0x00

		busyflag = 1
		while busyflag == 1:
			byteBusyFlag = bus.read_byte_data(DEVICE_ADDRESS, 0x01) #read_i2c_block_data(80, 0, 16)
			busyflag = byteBusyFlag % 2
			print(busyflag)
		
		bus.write_byte_data(DEVICE_ADDRESS,0x00,0x01)
		
		busyflag = 1
		while busyflag == 1:
			byteBusyFlag = bus.read_byte_data(DEVICE_ADDRESS, 0x01) #read_i2c_block_data(80, 0, 16)
			busyflag = byteBusyFlag % 2
			print(busyflag)
		blockData = bus.read_i2c_block_data(DEVICE_ADDRESS, 0x0f, 2)
		distance = (int)(blockData[0] << 8) | blockData[1]
		print(blockData)
		print(distance)

if __name__ == "__main__":
   main(sys.argv[1:])
