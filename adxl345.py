import smbus2 as smbus

class Acceloremeter:
    def __init__(self):
        self.init_device()
        
        self.bus.write_byte_data(self.ADXL345_ADDRESS, self.POWER_CTL, 0x08)
        self.bus.write_byte_data(self.ADXL345_ADDRESS, self.DATA_FORMAT, 0x08)


    def init_device(self):
        self.ADXL345_ADDRESS = 0x53
        self.POWER_CTL = 0x2D
        self.DATA_FORMAT = 0x31
        self.DATAX0 = 0x32
        self.bus = smbus.SMBus(1)

    def read_axis_data(self, register):
        low = self.bus.read_byte_data(self.ADXL345_ADDRESS, register)
        high = self.bus.read_byte_data(self.ADXL345_ADDRESS, register + 1)
        value = (high << 8) | low
        if value & (1 << 15):
            value = value - (1 << 16)
        return value
    
    def read_acceleration(self):   
        x = self.read_axis_data(self.DATAX0)
        y = self.read_axis_data(self.DATAX0 + 2)
        z = self.read_axis_data(self.DATAX0 + 4)
        factor = 0.0039  # 3.9 mg/LSB (theo datasheet)
        ax = x * factor
        ay = y * factor
        az = z * factor
        total = (ax**2 + ay**2 + az**2)**0.5
        print(total)
        return total
    
    def get_acceleration(self):
        return self.read_acceleration()