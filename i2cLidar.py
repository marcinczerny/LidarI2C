from smbus2 import SMBusWrapper

with SMBusWrapper(1) as bus: # 1 = /dev/i2c-1

	DEVICE_ADDRESS = 0x62
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
