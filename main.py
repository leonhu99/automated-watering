import time
import spidev
from typing import List
from pump import Pump
from sensor import Sensor
from gpio_setup import GPIO_Setup
from util import *


def run() -> None:
    
    print("Starting automated watering system...")

    # create lists for pumps and sensors
    pump_list: List[Pump] = []
    sensor_list: List[Sensor] = []

    # load general configuration
    config = get_configuration()
    AMOUNT_OF_WATER: float = config[0]
    INTERVAL_TIME: float = config[1]
    USE_WEBSERVER: bool = config[2]
    SERVER_URL: str = f'http://{config[3]}:{config[4]}/api/sensors'
    BOARD_MODE: str = config[5]
    MEASUREMENT_SAMPLES: int = config[6]
    USE_WATERING_SCHEDULE: bool = config[7]
    WATERING_WINDOW_START: datetime.time = config[8]
    WATERING_WINDOW_END: datetime.time = config[9]

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
        read_analog_sensors(sensor_list, SPI1, SPI2, MEASUREMENT_SAMPLES)

        if USE_WATERING_SCHEDULE:
            if WATERING_WINDOW_START <= datetime.now().time() <= WATERING_WINDOW_END:
                water_plants(pump_list, sensor_list, AMOUNT_OF_WATER)
            else:
                print(f'Not in watering window - skipping...')

        if USE_WEBSERVER:
            # send sensor data to server
            data = generate_sensor_data(sensor_list)
            send_sensor_data(data, SERVER_URL)

        if INTERVAL_TIME >= 86400:
            print(f'Sleeping.. Next measuring will be in {str(round(INTERVAL_TIME/86400, 2))} days!')
        elif INTERVAL_TIME >= 21600:
            print(f'Sleeping.. Next measuring will be in {str(round(INTERVAL_TIME/3600, 2))} hours!')
        elif INTERVAL_TIME >= 1800:
            print(f'Sleeping.. Next measuring will be in {str(round(INTERVAL_TIME/60, 2))} minutes!')
        else:
            print(f'Sleeping.. Next measuring will be in {str(INTERVAL_TIME)} seconds!')

        time.sleep(INTERVAL_TIME)


if __name__ == '__main__':
    run()
