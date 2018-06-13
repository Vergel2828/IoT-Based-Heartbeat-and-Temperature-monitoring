import threading
import temperatureRead
import time
import datetime
import RPi.GPIO as GPIO
import os
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6, GPIO.OUT)
GPIO.output(6, 1)

class TempThread:
        def __init__(self):
                self.temp_serial = self.sensor()
                while self.temp_serial == '' or self.temp_serial != '28-000009318819':
                        self.temp_serial = self.sensor()
                        print ("loop")
                        time.sleep(1)
                print(self.temp_serial)
                self.temperature_reading = "0 °C"
                self.temperature_int_reading = 0

        def sensor(self):
                ds18b20 = ''
                for i in os.listdir('/sys/bus/w1/devices'):
                        if i != 'w1_bus_master1':
                                ds18b20 = i
                return ds18b20

        def read(self, ds18b20):
                location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
                tfile = open(location)
                text = tfile.read()
                tfile.close()
                secondline = text.split("\n")[1]
                temperaturedata = secondline.split(" ")[9]
                temperature = float(temperaturedata[2:])
                celsius = temperature / 1000
                farenheit = (celsius * 1.8) + 32
                return celsius, farenheit

        def read_temperature(self):
                data = self.read(self.temp_serial)
                self.temperature_reading = ("%0.2f °C" % data[0])
                self.temperature_int_reading = data[0]

        def start_thread(self):
                self.thread = threading.Thread(target = self.read_temperature)
                self.thread.start()
                return

        def get_second_time_to_read(self, time_get):
                next_time = timer_get + datetime.timedelta(seconds = 3600)
                self.next_read_time = next_time.strftime("%Y-%m-%d %H:%M")
