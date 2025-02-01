import spidev, time
import RPi.GPIO as GPIO
from typing import List
from pump import *
from util import *
from gpio_setup import *


def calibrate_sensors(channels1: int, channels2: int):
    spi1 = spidev.SpiDev(0, 0)
    spi2 = spidev.SpiDev(0, 1) 

    def setup_spi(spi):
        spi.max_speed_hz = 1350000
        spi.mode = 0

    setup_spi(spi1)
    setup_spi(spi2)

    def read_channel(spi, channel):
        if channel < 0 or channel > 7:
            raise ValueError("Channel must be in interval [0-7].")

        command = [1, (8 + channel) << 4, 0]
        response = spi.xfer2(command)

        result = ((response[1] & 3) << 8) | response[2]
        return result


    print("Please put all sensors on a dry surface.")
    ready = input("Ready? Y/y")
    if(ready == "Y" or ready == "y"): 
        for i in range(channels1):
            sensor_value = read_channel(spi1, i)
            print("DRY value of Sensor " + str(i+1) + " (MCP3008 \#1): " + str(sensor_value))

        for i in range(channels2):  
            sensor_value = read_channel(spi2, i)
            print("DRY value of Sensor " + str(i+channels1) + " (MCP3008 \#2): " + str(sensor_value))

    print("Please put all sensors in a glass of water.")
    ready = input("Ready? Y/y")
    if(ready == "Y" or ready == "y"): 
        for i in range(channels1):
            sensor_value = read_channel(spi1, i)
            print("WET value of Sensor " + str(i+1) + " (MCP3008 \#1): " + str(sensor_value))

        for i in range(channels2):  
            sensor_value = read_channel(spi2, i)
            print("WET value of Sensor " + str(i+channels1) + " (MCP3008 \#2): " + str(sensor_value))
            

def calibrate_pumps():
    config = get_configuration()
    BOARD_MODE = config[5] 
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD) if BOARD_MODE == "BOARD" else GPIO.setmode(GPIO.BCM)

    pump_data = GPIO_Setup._read_IO_data()
    pump_list: List[Pump] = []
    GPIO_Setup.__instantiate_pumps(pump_data, pump_list)

    for pump in pump_list:
        GPIO.output(pump.pin, GPIO.LOW)
        time.sleep(60)
        GPIO.output(pump.pin, GPIO.HIGH)
        print(f'Please note the measured amount for {pump.id}.')
        input("Continue? Please press a button.")


if __name__ == '__main__':
    print("This script allows you to calibrate your sensors and pumps.\nWe will start with the sensors.\n")
    print("|------------------------|")
    print("|   Sensor Calibration   |")
    print("|------------------------|")
    while True:
        print("Make sure to connect everything properly. (Sensors to the Analog/Digital converter, VCC and GND. A/D to RaspberryPi")
        print("Calibration starting..")
        ready = input("Is everything connected properly? Y/y")
        if(ready == "Y" or ready == "y"):
            channels1 = int(input("How many channels are used on A/D converter #1 ?"))
            channels2 = int(input("How many channels are used on A/D converter #2 ?"))
            calibrate_sensors(channels1, channels2)

        break


    print("|------------------------|")
    print("|    Pump Calibration    |")
    print("|------------------------|")
    while True:
        print("Make sure to connect everything properly.")
        print("Every pump specified in the config.yaml will run for exactly one minute. Please measure the amount of water pumped and note it.")
        print("Calibration starting..")
        ready = input("Is everything connected properly? Y/y")
        if(ready == "Y" or ready == "y"):
            calibrate_pumps()

        break
