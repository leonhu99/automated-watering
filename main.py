import requests
import time
import spidev
from typing import List
from pump import Pump
from sensor import Sensor
from gpio_setup import GPIO_Setup
from util import *


def generate_sensor_data(sensor_list: List[Sensor]) -> any:
    """Function that generates the sensor data for the webserver.

    Parameters
    ----------
    sensor_list : List[Sensor]
        A list of Sensor objects

    Returns
    -------
    The generated data in the typical format (json string).
    """
    
    data = []
    for sensor in sensor_list:
        data.append({
            "sensor_id": sensor.id, 
            "last_value": sensor.last_value,
            "dry_value": sensor.dry_value,
            "wet_value": sensor.wet_value,
            "interval_size": sensor.interval_size
        })
    
    return data


def send_sensor_data(data: any, SERVER_URL: str) -> None:
    """Function that sends the sensor data to the webserver.

    Parameters
    ----------
    data : any
        json string containing the sensor data
    SERVER_URL : str
        A string contianign the url of the server including ip address, port and route.

    Returns
    -------
    None
    """
    
    try:
        requests.post(SERVER_URL, json = data)
    except Exception as e:
        print("Error while sending data! ", {e})


def run() -> None:
    
    print("Starting automated watering system...")

    # create lists for pumps and sensors
    pump_list: List[Pump] = []
    sensor_list: List[Sensor] = []

    # load general configuration
    config = get_configuration()
    AMOUNT_OF_WATER = config[0]
    INTERVAL_TIME = config[1]
    USE_WEBSERVER = config[2]
    SERVER_URL = f'http://{config[3]}:{config[4]}/api/sensors'
    BOARD_MODE = config[5] 

    # SPI configuration
    SPI1 = spidev.SpiDev(0, 0) # CE0 for MCP3008#1 (sensors 1-6)
    SPI2 = spidev.SpiDev(0, 1) # CE1 for MCP3008#2 (sensors 7-11)
    SPI1.max_speed_hz = 1350000 # max frequency 1.35 MHz
    SPI1.mode = 0 # SPI mode 0
    SPI2.max_speed_hz = 1350000
    SPI2.mode = 0  

    # configure I/O and set values for pumps and sensors
    GPIO_Setup.configure(BOARD_MODE, pump_list, sensor_list)
    if USE_WEBSERVER:
        # send sensor data to server
        data = generate_sensor_data(sensor_list)
        send_sensor_data(data, SERVER_URL)

    while(True):
        read_analog_sensors(sensor_list, SPI1, SPI2)
        water_plants(pump_list, sensor_list, AMOUNT_OF_WATER)

        if USE_WEBSERVER:
            # send sensor data to server
            data = generate_sensor_data(sensor_list)
            send_sensor_data(data, SERVER_URL)

        print(f'Sleeping.. Next measuring will be in {INTERVAL_TIME} seconds!')
        time.sleep(INTERVAL_TIME)


if __name__ == '__main__':
    run()
