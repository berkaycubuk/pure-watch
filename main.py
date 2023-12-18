from machine import Pin, I2C, RTC, ADC
from ssd1306 import SSD1306_I2C
from max30102 import MAX30102
from imu import MPU6050
import time
import network
import socket
import ntptime

# global values
page_index = 0
rtc = RTC()
i2c = I2C(1,scl=Pin(27),sda=Pin(26),freq=200000)
display = SSD1306_I2C(128, 32, i2c)
wlan = network.WLAN(network.STA_IF)
mpu6050 = MPU6050(i2c)

# toggle switches
toggle_1 = Pin(16, Pin.IN, Pin.PULL_UP)
toggle_2 = Pin(20, Pin.IN, Pin.PULL_UP)
toggle_3 = Pin(17, Pin.IN, Pin.PULL_UP)

# network
ssid = ''
password = ''

def connect_to_wifi():
    # set the display
    display.fill(0)
    display.text('Connecting...', 0, 0)
    display.show()
    
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:
        print("Waiting for connection...")
        time.sleep(1)
    print(wlan.ifconfig())
    
    # set current time
    #ntptime.settime()
    
def display_page_0():
    timestamp = rtc.datetime()
    display.fill(0)
    display.text('{:02d}:{:02d}:{:02d}'.format(timestamp[4], timestamp[5], timestamp[6]), 0, 0)
    display.show()
    
# battery level
def display_page_1():
    max_voltage = 4.958535
    min_voltage = 3.2
    conversion_factor = 3 * 3.3 / 65535
    
    Pin(25, mode=Pin.OUT, pull=Pin.PULL_DOWN).high()
    Pin(29, Pin.IN)
    adc = ADC(29)
    battery_level = round(((adc.read_u16() * conversion_factor) - min_voltage) / (max_voltage - min_voltage) * 100)
    print(adc.read_u16() * conversion_factor)
    display.fill(0)
    display.text('Battery: {}%'.format(battery_level),0, 0)
    display.show()
    Pin(29, Pin.ALT, pull=Pin.PULL_DOWN, alt=7)
    
def display_page_2():
    display.fill(0)
    display.text('Wifi', 0, 0)
    if wlan.isconnected() == True:
        display.text('{}'.format(wlan.ifconfig()[0]), 0, 12)
    else:
        display.text('Disconnected', 0, 12) 
    display.show()
    
def display_page_3():
    display.fill(0)
    display.text('Gyro', 0, 0)
    display.text('x:{}'.format(gyro_x), 0, 12)
    display.show()
    
# connect_to_wifi()

# main program loop
while (True):
    if toggle_1.value() == False:
        display.fill(0)
        display.show()
        time.sleep(5)
        continue
    
    acceleration = mpu6050.accel
    gyroscope = mpu6050.gyro
    gyro_x = gyroscope.x
    gyro_y = gyroscope.y
    gyro_z = gyroscope.z
    
    if toggle_3.value() == False:
        if wlan.isconnected() == True:
            wlan.disconnect()
        
    if toggle_3.value() == True:
        if wlan.isconnected() == False:
            connect_to_wifi()
    
    if (page_index == 0):
        display_page_0()
        page_index = 1
    elif (page_index == 1):
        display_page_1()
        page_index = 2
    elif (page_index == 2):
        display_page_2()
        page_index = 3
    elif (page_index == 3):
        display_page_3()
        page_index = 0  

    time.sleep(5)

