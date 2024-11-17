import requests
from typing import List
from pump import Pump
from sensor import Sensor
from gpio_setup import GPIO_Setup
from util import *


def generate_sensor_data(sensor_list: List[Sensor]):
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


def send_sensor_data(data, SERVER_URL: str) -> None:
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

    # configure I/O and set values for pumps and sensors
    GPIO_Setup.configure(pump_list, sensor_list)
    if USE_WEBSERVER:
        # send sensor data to server
        data = generate_sensor_data(sensor_list)
        send_sensor_data(data, SERVER_URL)

    while(True):
        check_all_sensors(pump_list, sensor_list, AMOUNT_OF_WATER)
        if USE_WEBSERVER:
            # send sensor data to server
            data = generate_sensor_data(sensor_list)
            send_sensor_data(data, SERVER_URL)

        print(f'Sleeping.. Next measuring will be in {INTERVAL_TIME} seconds!')
        time.sleep(INTERVAL_TIME)


if __name__ == '__main__':
    run()
