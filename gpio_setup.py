from typing import List
from pump import *
from sensor import *
import yaml
# import RPi.GPIO as GPIO

class GPIO_Setup:
    def __instantiate_pumps(pump_list: List[Pump]) -> None:
        # load pump_data from config/pump_config.yaml
        with open('config/pump_config.yaml', 'r') as pump_file:
            pump_data = yaml.safe_load(pump_file)

        # create pumps from read data
        for pump in pump_data['pumps']:
            temp_pump = Pump(id = pump['id'], pin = pump['pin'], pump_rate = pump['pump_rate'], description = pump['description'])
            pump_list.append(temp_pump)

            # configure pin of pump as output 
            # GPIO.setup(temp_pump.pin, GPIO.OUT)

            # initially set to HIGH due to pumps being LOW-active
            # GPIO.output(temp_pump.pin, GPIO.HIGH) 


    def __instantiate_sensors(sensor_list: List[Sensor]) -> None:
        # load sensor_data from config/sensor_config.yaml
        with open('config/sensor_config.yaml', 'r') as sensor_file:
            sensor_data = yaml.safe_load(sensor_file)

        # create sensors from read data
        for sensor in sensor_data['sensors']:
            temp_sensor = Sensor(id = sensor['id'], pin = sensor['pin'], description = sensor['description'], dry_value = sensor['dry_value'], wet_value = sensor['wet_value'])
            sensor_list.append(temp_sensor)

            # configure pin of sensor as input  with Pull-Down (not sure if that is correct!)
            # GPIO.setup(temp_sensor.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


    def configure(pump_list: List[Pump], sensor_list: List[Sensor]) -> None:
        # use BOARD-mode
        # GPIO.setmode(GPIO.BOARD)
        GPIO_Setup.__instantiate_pumps(pump_list)
        GPIO_Setup.__instantiate_sensors(sensor_list)