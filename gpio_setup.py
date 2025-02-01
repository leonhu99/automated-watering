import yaml
import util
import RPi.GPIO as GPIO
from typing import List
from pump import *
from sensor import *


class GPIO_Setup:

    def _read_IO_data() -> any:
        """Function that reads the configuration from config/config.yaml

        Parameters
        ----------
        None

        Returns
        -------
        The data containing the configuration.
        """

        IO_DATA = ""
        try:
            with open('config/config.yaml', 'r') as config_file:
                IO_DATA = yaml.safe_load(config_file)
        except FileNotFoundError:
            print("Config file cannot be found!") 

        return IO_DATA
    

    def __instantiate_pumps(pump_data: any, pump_list: List[Pump]) -> None:
        """Function that instantiates the pumps.

        Parameters
        ----------
        pump_data : any
            The yaml_configuration read with __read_IO_data()
        pump_list : List[Pump]
            A list of Pump objects

        Returns
        -------
        None
        """
        
        for pump in pump_data['pumps']:
            # create temporary pumps from read data and add them to the pump list
            temp_pump = Pump(id = pump['id'], pin = pump['pin'], pump_rate = pump['pump_rate'])
            pump_list.append(temp_pump)

            # configure pin of pump as output and initially set to HIGH as pumps are LOW-active
            GPIO.setup(temp_pump.pin, GPIO.OUT, initial=GPIO.HIGH)


    def __instantiate_sensors(sensor_data: any, sensor_list: List[Sensor]) -> None:
        """Function that instantiates the sensors.

        Parameters
        ----------
        sensor_data : any
            The yaml_configuration read with __read_IO_data()
        sensor_list : List[Sensor]
            A list of Sensor objects

        Returns
        -------
        None
        """

        for sensor in sensor_data['sensors']:
            # create temporary sensors from read data and add them to the sensor list
            temp_sensor = Sensor(id = sensor['id'], description = sensor['description'], dry_value = sensor['dry_value'], wet_value = sensor['wet_value'], last_value = 0)
            sensor_list.append(temp_sensor)

        # initial values for "last_value"
        util.init_last_values(sensor_list)      


    def configure(board_mode: str, pump_list: List[Pump], sensor_list: List[Sensor]) -> None:
        """Function that configures the GPIO.

        Parameters
        ----------
        board_mode : str
            The desired board mode [BOARD | BCM]
        pump_list : List[Pump]
            A list of Sensor objects
        sensor_list : List[Sensor]
            A list of Pump objects

        Returns
        -------
        None
        """
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD) if board_mode == "BOARD" else GPIO.setmode(GPIO.BCM)

        IO_DATA = GPIO_Setup._read_IO_data()
        GPIO_Setup.__instantiate_pumps(IO_DATA, pump_list)
        GPIO_Setup.__instantiate_sensors(IO_DATA, sensor_list)