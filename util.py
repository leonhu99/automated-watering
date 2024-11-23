import os, time, csv, random, yaml
#import RPi.GPIO as GPIO
from datetime import datetime
from typing import List, Tuple, Union
from sensor import Sensor
from pump import Pump


class CSVParser():
    """Class for creating a parser for .csv-files """
    def __init__(self, csv_file: str) -> None:
        self.csv_file = csv_file

    def parse_csv(self) -> List[str]:
        try:
            with open(self.csv_file, 'r') as f:
                data = f.readlines()
                return data
        except FileNotFoundError:
            pass
        return []


def get_configuration() -> List[Union[int, bool, str]]:
    """Function that fetches all settings from the config file located in config/config.yaml

    Returns
    -------
    A List containing every setting specified in 'general'-sector of the config file.
    """
    quantity: int = 0
    interval_time: int = 0
    use_webserver: bool = False
    server_ip: str = ""
    port: int = 0

    # open config file
    try:
        with open('config/config.yaml', 'r') as config_file:
            config_data = yaml.safe_load(config_file)
    except FileNotFoundError:
        print("Config file cannot found!")

    # extract general configuration data
    for data in config_data['general']:
        quantity = int(data['amount_of_water'])
        interval_time = int(data['interval_time'])
        use_webserver = bool(data['use_webserver'])
        server_ip = str(data['server_ip'])
        port = int(data['port'])

    return [quantity, interval_time, use_webserver, server_ip, port]


def check_all_sensors(pump_list: List[Pump], sensor_list: List[Sensor], AMOUNT_OF_WATER: int) -> None:
    """Function that iteratively checks every sensor for its value
    and activates the corresponding pump if the moisture [%] is below 25%.
    
    Parameters
    ----------
    pump_list : List[Pump]
        A list of Pump objects
    sensor_list : List[Sensor]
        A list of Sensor objects
    AMOUNT_OF_WATER : int
        The amount of water used to water a plant (configured in config/config.yaml)

    Returns
    -------
    None
    """
    
    for sensor in sensor_list:
        # fetch data from sensor pin
        # sensor.last_value = GPIO.input(sensor.pin)

        # only for simulation, delete when using real sensors and uncomment lines above
        value = random.randint(260, 521)
        sensor.last_value = value

        # calculate moisture percentage
        moisturePercentage: int = int((1-((sensor.last_value/sensor.wet_value) - 1)) * 100);
        
        # check if soil is very dry [0%-25%], activate pump if necessary
        if moisturePercentage >= 0 and moisturePercentage <= 25:
            for pump in pump_list:
                if pump.id[-1] == sensor.id[-1]:
                    # GPIO.output(pump.pin, GPIO.LOW)
                    time.sleep(AMOUNT_OF_WATER/(pump.pump_rate/60))
                    write_to_logfile(datetime.now(), sensor.id, round(AMOUNT_OF_WATER/(pump.pump_rate/60), 2), sensor.last_value)
                    # GPIO.output(pump.pin, GPIO.LOW)
                    sensor.last_value = 260
                    

def write_to_logfile(date_of_watering: datetime, sensor_id: str, duration: float, soil_value: int) -> None:
    """Function that saves all made changes in a logfile. 
    Location of logfile is /log/watering_log.csv
    
    Parameters
    ----------
    date_of_watering : datetime
        The time of watering process (format: YYYY-mm-dd HH:MM:SS)
    sensor_id : str
        Sensor and respectively the plant that has been watered
    duration : float
        Duration of the watering process (in [s])
    soil_value : int
        Absolute value measured by the sensor before watering process

    Returns
    -------
    None
    """
    
    file_exists: bool = False

    # check if watering_logfile.csv exists in /log/
    try:
        with open('log/watering_log.csv', 'r'):
            file_exists = True
    except FileNotFoundError:
        # Make new directory 'log'
        try:
            os.mkdir('log')
        except:
            pass

    with open('log/watering_log.csv', 'a', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile)

        # create new logfile with csv-header
        if not file_exists:
            writer.writerow(['Date', 'Sensor_ID', 'Duration', 'Soil Value'])
        
        # append new data
        writer.writerow([date_of_watering.strftime('%Y-%m-%d %H:%M:%S'), sensor_id, duration, soil_value])


def init_last_value(sensor_list: List[Sensor]) -> None:
    """Function that reads newest changes to each sensor from logfile
    and sets initial values based on those values for every sensor.
    
    Parameters
    ----------
    sensor_list : List[Sensor]
        A list of Sensor objects

    Returns
    -------
    None
    """
    data: List[str] = []
    parser = CSVParser('log/watering_log.csv')
    data = parser.parse_csv()
    if not data:
        # log file is empty => set last value to 0
        for sensor in sensor_list:
            sensor.last_value = 0
    else:
        for sensor in sensor_list:
            for entry in reversed(data):
                # Find newest value for every sensor by splitting entry
                split_entry: List[str] = entry.split(',')
                if split_entry[1] == sensor.id:
                    sensor.last_value = int(split_entry[3])
                    break


def get_last_values(sensor_list: List[Sensor]) -> List[Tuple[str, int]]:
    """Function for generating the correspondences between a sensor and its
    last measured value.
    
    Parameters
    ----------
    sensor_list : List[Sensor]
        A list of Sensor objects

    Returns
    -------
    last_values : List[Tuple[str, int]]
        A List containing a tuple for every sensor consisting of sensor.id and sensor.last_value 
    """
    last_values: List[str, int] = []

    for sensor in sensor_list:
        last_values.append([sensor.id, sensor.last_value])

    return last_values