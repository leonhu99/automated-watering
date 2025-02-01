import os, time, csv, random, yaml
import RPi.GPIO as GPIO
import spidev
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
    board_mode: str = ""

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
        board_mode = str(data['board_mode'])
        
    return [quantity, interval_time, use_webserver, server_ip, port, board_mode]


def water_plants(pump_list: List[Pump], sensor_list: List[Sensor], AMOUNT_OF_WATER: int) -> None:
    """Function that iteratively checks every sensor for its value
    and activates the corresponding pump if the moisture is below 25%.
    
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
        # calculate moisture percentage
        moisture_percentage: int = int((1-((sensor.last_value/sensor.wet_value) - 1)) * 100);
        
        # check if soil is very dry [0%-25%], activate pump if necessary
        if moisture_percentage >= 0 and moisture_percentage <= 25:
            for pump in pump_list:
                if pump.id[-1] == sensor.id[-1]:
                    # activate corresponding pump (LOW-active)
                    GPIO.output(pump.pin, GPIO.LOW)
                    time.sleep(AMOUNT_OF_WATER/(pump.pump_rate/60))

                    # save watering event in logfile
                    write_to_logfile(datetime.now(), sensor.id, round(AMOUNT_OF_WATER/(pump.pump_rate/60), 2), sensor.last_value)
                    
                    # deactivate pump
                    GPIO.output(pump.pin, GPIO.HIGH)


def read_analog_sensors(sensor_list: List[Sensor], spi1: spidev.SpiDev, spi2: spidev.SpiDev) -> None:
    """Function that reads the analog values from the MCP3008 ADC and
    stores the value in the corresponding sensor object.
    
    Parameters
    ----------
    sensor_list : List[Sensor]
        List of all sensors
    spi1 : spidev.SpiDev
        The first MCP3008 AD converter
    spi2 : spidev.SpiDev
        The second MCp3008 AD converter

    Returns
    -------
    None
    """
    for sensor in sensor_list:
        counter = sensor[-1]

        # read sensors 1-6
        if (counter <= 6):
            # use MCP3008#1 and substract 1 from ID to get corresponding channel
            sensor.last_value = read_channel(spi1, counter-1)
        # read sensors 7-11
        else:
            # use MCP3008#2 and subtract 8 from ID to get corresponding channel
            sensor.last_value = read_channel(spi2, counter-8)


def read_channel(spi: spidev.SpiDev, channel: int) -> int:
    """ Auxiliary function to read the analog data of the sensors of a MCP3008 (Analog/Digital Converter)

    Parameters
    ----------
    spi : spiDev.SpiDev
        The SPI object (= A/D converter)

    Returns
    -------
    An Integer representing the value read from the sensor.
    """
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be between 0-7!")

    # Send 3 Byte message: Startbit, Mode (Single/Diff), Channel
    command = [1, (8 + channel) << 4, 0]
    response = spi.xfer2(command)

    # Evaluate response
    result = ((response[1] & 3) << 8) | response[2]

    return result


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


def init_last_values(sensor_list: List[Sensor]) -> None:
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
        
    if data:
        # log contains values for (some) sensors
        for sensor in sensor_list:
            for entry in reversed(data):
                # Find newest value for every sensor by splitting entry
                split_entry: List[str] = entry.split(',')
                if split_entry[1] == sensor.id:
                    sensor.last_value = int(split_entry[3])
                    break