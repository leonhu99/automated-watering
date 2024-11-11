import os, time, csv
#import RPi.GPIO as GPIO
from datetime import datetime
from typing import List
from sensor import Sensor
from pump import Pump



def check_all_sensors(pump_list: List[Pump], sensor_list: List[Sensor], AMOUNT_OF_WATER: int) -> None:
    # check all sensors
        for sensor in sensor_list:
            #temp_value = GPIO.input(sensor.pin)
            temp_value = 500

            # check if soil is dry, activate pump if necessary
            if temp_value < sensor.dry_value and temp_value >= sensor.dry_value - sensor.interval_size:
                for pump in pump_list:
                    if pump.id[-1] == sensor.id[-1]:
                        # GPIO.output(pump.pin, GPIO.LOW)
                        time.sleep(AMOUNT_OF_WATER/(pump.pump_rate/60))
                        write_to_logfile(datetime.now(), sensor.id, round(AMOUNT_OF_WATER/(pump.pump_rate/60), 2))
                        # GPIO.output(pump.pin, GPIO.LOW)
                    break


def write_to_logfile(date_of_watering: datetime, sensor_id: str, time_for_watering: float) -> None:
    file_exists: bool = False

    # check if watering_logfile.csv exists in /log/
    try:
        with open('log/watering_log.csv', 'r'):
             file_exists = True
    except FileNotFoundError:
        try:
            os.mkdir('log')
        except:
            pass

    with open('log/watering_log.csv', 'a', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile)

        # create new logfile with csv-header
        if not file_exists:
            writer.writerow(['Date', 'Sensor_ID', 'Duration'])
        
        # append new data
        writer.writerow([date_of_watering.strftime('%Y-%m-%d %H:%M:%S'), sensor_id, time_for_watering])
