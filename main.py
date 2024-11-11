from typing import List
from pump import Pump
from sensor import Sensor
from gpio_setup import GPIO_Setup
from util import *


if __name__ == '__main__':
    # create lists for pumps and sensors
    pump_list: List[Pump] = []
    sensor_list: List[Sensor] = []
    AMOUNT_OF_WATER: int = 50 # milliliter

    # configure I/O for pumps and sensors
    GPIO_Setup.configure(pump_list, sensor_list)

    while(True):
         check_all_sensors(pump_list, sensor_list, AMOUNT_OF_WATER) # check sensors and write to watering_log.csv
         # time.sleep(1800) # sleep for 30 minutes
         break
            
