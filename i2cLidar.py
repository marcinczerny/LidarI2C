#!/usr/bin/env python
from smbus2 import SMBusWrapper
from enum import Enum
import sys, getopt
import time
import rospy
from msgs.msg import distance


# Class For Debugging and monitoring script
class counter:
	iterator = 0


### Classes for configuration purposes
# Class For choosing work mode
class rangeType_T(Enum):
	RANGE_NONE = 0
	RANGE_SINGLE = 1
	RANGE_CONTINOUS = 2
	RANGE_TIMER = 3

#Class for choosing measure settings
class rangeConfiguration_T(Enum):
	DEFAULT_MODE = 0
	SHORT_RANGE_HIGH_SPEED = 1
	DEFAULT_RANGE_HIGHER_SPEED_SHORT_RANGE = 2
	MAXIMUM_RANGE = 3
	HIGH_SENSIVITY = 4
	LOW_SENSIVITY = 5
	SHORT_RANGE_HIGH_SPEED_HIGHER_ERROR = 6

#Base class for efault measure config
#sigCountMax -
#acqConfigReq -
#refCountMax -
#thresholdBypass -
class configurationBase:
	#default values
	sigCountMax = 0x80
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0x00
	a = 0.996619665834702
	b = 0.0319916768216451
	
class configurationShortRangeHighSpeed(configurationBase):
	sigCountMax = 0x1d
	acqConfigReg = 0x08
	refCountMax = 0x03
	thresholdBypass = 0x00
	a = 0.996059560501465
	b = -0.0320527416112777
	
class configurationDefaultRangeHigherSpeed(configurationBase):
	sigCountMax	= 0x80
	acqConfigReg = 0x00
	refCountMax = 0x03
	thresholdBypass = 0x00
	a = 0.997080778127185
	b = -0.0318613458613982
	
class configurationMaximumRange(configurationBase):
	sigCountMax = 0xff
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0x80
	a = 0.997461089815644
	b = -0.0329153375920736
	
class configurationHighSensivity(configurationBase):
	sigCountMax = 0x80
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0x80
	a = 0.996288921030751
	b = -0.03233669960454

class configurationLowSensivity(configurationBase):
	sigCountMax = 0x80
	acqConfigReg = 0x08
	refCountMax = 0x05
	thresholdBypass = 0xb0
	a = 0.996328067914677
	b =-0.0344698490779917

class configurationShortRangeHighSpeedHigherError(configurationBase):
	sigCountMax = 0x04
	acqConfigReg = 0x01
	refCountMax = 0x03
	thresholdBypass = 0x00
	a = 0.995443814170842
	b = -0.0637529480862986


###############
###I2C - Functions
###############
def writeConfig(bus,config,lidarliteAddress):
	
	#Uncomment folowing lines for debugging purposes
	#print(config.sigCountMax)
	#print(config.acqConfigReg)
	#print(config.refCountMax)
	#print(config.thresholdBypass)	
	
	#Send chosen measure configuration to Lidar		
	bus.write_byte_data(lidarliteAddress,0x02,config.sigCountMax)
	bus.write_byte_data(lidarliteAddress,0x04,config.acqConfigReg)
	bus.write_byte_data(lidarliteAddress,0x12,config.refCountMax)
	bus.write_byte_data(lidarliteAddress,0x1c,config.thresholdBypass)


#Fynction for choosing measurement configuration
def configure(bus,configuration,lidarliteAddress):
	config = getConfig(configuration)
	if config is None:
		sys.exit()
	
	writeConfig(bus,config,lidarliteAddress)
	
def getConfig(configuration):
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
		config = None
	return config
#Helper function for Lidar readiness status
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
def processDistance(distance,setting):
	distance = setting.a * distance + setting.b
	return distance
#####################################
### Lidar Working Modes Functions ###
#####################################

def singleMeasureMode(bus, setting):
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

	#Process distance
	distance = processDistance(distance, setting)
	print(distance)
	
def noneMeasureMode():
	distance = 0
	print(distance)

def continuousMeasureMode(bus,count, setting):
	DEVICE_ADDRESS = 0x62
	while not rospy.is_shutdown():

		# 1. Wait to indicate if device is idle. This must be
		#    done before triggering a range measurement.	
		waitForReadyState(bus,DEVICE_ADDRESS)
		
		# 2. Trigger range measurement.	
		takeMeasure(bus,DEVICE_ADDRESS)
		
		# 3. Read new distance data from device registers
		distance = readDistance(bus,DEVICE_ADDRESS)
		
		#4. Process distance
		distance = processDistance(distance, setting)
		#print(distance)
		now = rospy.get_rostime()
	
		msg.x = distance
	
		pub.publish(msg)
		# print(distance)
		
		#Do debugowania
		counter.iterator = counter.iterator+1
		
def timerMeasureMode(bus, timeInSeconds, setting):
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
		
		# 5. Process distance
		distance = processDistance(distance, setting)
		print(distance)

###############################
##### Main program ############
###############################
def main(argv):
	
	#Dictionaries for command line parameters handling
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
	
	#Default values
	mode = rangeType_T.RANGE_SINGLE
	setting = rangeConfiguration_T.DEFAULT_MODE
	timeInSeconds = 0.1
	
	##Get command line parameters
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
	
	#Uncomment following lines for debug purposes			
	#print 'mode is "', mode
	#print 'setting is "', setting
	#print 'time = ', timeInSeconds		
	
	### Lidar ####
			
	with SMBusWrapper(1) as bus: # 1 = /dev/i2c-1

		DEVICE_ADDRESS = 0x62
		DEVICE_READYFLAG = 0x01
		DEVICE_TAKEMES = 0x00

		configure(bus,setting, DEVICE_ADDRESS)
		config = getConfig(setting)
		if mode == rangeType_T.RANGE_NONE:
			noneMeasure()
		elif mode == rangeType_T.RANGE_SINGLE:
			singleMeasureMode(bus, config)
		elif mode == rangeType_T.RANGE_CONTINOUS:
			try:
				start = time.time()
				count = counter()
				continuousMeasureMode(bus, count, config)
			except (KeyboardInterrupt, SystemExit):
				end = time.time()
				#print('Duration: ' ,end-start)
				#print('Count: ', counter.iterator)
				sys.exit()
		elif mode == rangeType_T.RANGE_TIMER:
			try:
				timerMeasureMode(bus, timeInSeconds, config)
			except (KeyboardInterrupt, SystemExit):
				sys.exit()
		else:
			print('Error no mode given')
			sys.exit()


if __name__ == "__main__":
	
	rospy.init_node('lidar', anonymous=True)
	pub = rospy.Publisher('lidar', distance, queue_size=10)
	msg = distance()

	main(sys.argv[1:])
