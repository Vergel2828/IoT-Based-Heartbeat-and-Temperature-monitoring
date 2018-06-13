from pulsesensor import Pulsesensor
import time
import threading
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

p = Pulsesensor()

class ThreadPulse:
        def __init__(self):
                self.Raw = 0
                self.PulseRate = 0

        def pulse_loop(self):
                p.startAsyncBPM()
                while not self.thread.stopped:
                        self.PulseRate = p.BPM
                        self.Raw = p.RAW_DATA
                        #print(self.Raw)
                        time.sleep(1)
                p.stopAsyncBPM()
                        
        def start_thread(self):
                self.thread = threading.Thread(target=self.pulse_loop)
                self.thread.stopped = False            
                GPIO.output(13, 1)
                GPIO.output(12, 1)
                GPIO.output(26, 1)
                self.thread.start()
                return

        def stop_thread(self):
                self.thread.stopped = True
                self.Raw = 0
                GPIO.output(13, 0)
                GPIO.output(12, 0)
                GPIO.output(26, 0)
                return


