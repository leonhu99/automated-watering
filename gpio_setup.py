import yaml
import util
import RPi.GPIO as GPIO
from typing import List
from pump import *
from sensor import *


class GPIO_Setup:

    def __instantiate_pumps(pump_data: any, pump_list: List[Pump]) -> None:
        # create pumps from read data
        for pump in pump_data['pumps']:
            temp_pump = Pump(id = pump['id'], pin = pump['pin'], pump_rate = pump['pump_rate'])
            pump_list.append(temp_pump)

            # configure pin of pump as output 
            GPIO.setup(temp_pump.pin, GPIO.OUT)

            # initially set to HIGH as pumps are LOW-active
            GPIO.output(temp_pump.pin, GPIO.HIGH) 


    def __instantiate_sensors(sensor_data: any, sensor_list: List[Sensor]) -> None:
        # create sensors from read data
        for sensor in sensor_data['sensors']:
            temp_sensor = Sensor(id = sensor['id'], description = sensor['description'], dry_value = sensor['dry_value'], wet_value = sensor['wet_value'], last_value = 0)
            sensor_list.append(temp_sensor)

        # initial values for "last_value"
        util.init_last_values(sensor_list)


    def __read_IO_data() -> None:
        IO_DATA = ""
        try:
            with open('config/config.yaml', 'r') as config_file:
                IO_DATA = yaml.safe_load(config_file)
        except FileNotFoundError:
            print("Config file cannot be found!") 

        return IO_DATA      


    def configure(board_mode: str, pump_list: List[Pump], sensor_list: List[Sensor]) -> None:
        GPIO.setmode(GPIO.BOARD) if board_mode == "BOARD" else GPIO.setmode(GPIO.BCM)

        IO_DATA = GPIO_Setup.__read_IO_data()
        GPIO_Setup.__instantiate_pumps(IO_DATA, pump_list)
        GPIO_Setup.__instantiate_sensors(IO_DATA, sensor_list)