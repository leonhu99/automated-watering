import yaml
import util
import RPi.GPIO as GPIO
from typing import List, Union
from pump import *
from sensor import *


class GPIO_Setup:

    def __instantiate_pumps(pump_list: List[Pump]) -> None:
        # load pump_data from config/config.yaml
        try:
            with open('config/config.yaml', 'r') as config_file:
                pump_data = yaml.safe_load(config_file)
        except FileNotFoundError:
            print("Config file cannot be found!")

        # create pumps from read data
        for pump in pump_data['pumps']:
            temp_pump = Pump(id = pump['id'], pin = pump['pin'], pump_rate = pump['pump_rate'], description = pump['description'])
            pump_list.append(temp_pump)

            # configure pin of pump as output 
            GPIO.setup(temp_pump.pin, GPIO.OUT)

            # initially set to HIGH as pumps are LOW-active
            GPIO.output(temp_pump.pin, GPIO.HIGH) 


    def __instantiate_sensors(sensor_list: List[Sensor]) -> None:
        # load sensor_data from config/config.yaml
        try:
            with open('config/config.yaml', 'r') as config_file:
                sensor_data = yaml.safe_load(config_file)
        except FileNotFoundError:
            print("Config file cannot be found!")

        # create sensors from read data
        for sensor in sensor_data['sensors']:
            temp_sensor = Sensor(id = sensor['id'], description = sensor['description'], dry_value = sensor['dry_value'], wet_value = sensor['wet_value'], last_value = sensor['last_value'])
            sensor_list.append(temp_sensor)


    def configure(board_mode: str, pump_list: List[Pump], sensor_list: List[Sensor]) -> None:
        GPIO.setmode(GPIO.BOARD) if board_mode == "BOARD" else GPIO.setmode(GPIO.BCM)
        GPIO_Setup.__instantiate_pumps(pump_list)
        GPIO_Setup.__instantiate_sensors(sensor_list)