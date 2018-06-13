from threadpulsesensor import ThreadPulse
import time
import threading

t = ThreadPulse()

class WriteThread:
    def __init__(self):
        self.text_to_append=''
        self.cnt = 1
        self.Rate = 0

    def write_loop(self):
        #time.sleep(10)
        self.clean_text_file()
        t.start_thread()
        while not self.thread.stopped: 
            text_file = open("/home/pi/Desktop/DP_final/ProjectDesign/database/rawheartbeat.txt", 'a')
            text_file.write('{},{}\n'.format(str(self.cnt), str(t.Raw)))
            text_file.close()
            self.cnt = self.cnt + 1
            self.Rate = str(int(t.PulseRate))
            time.sleep(1)
        t.stop_thread()

    def start_thread_write(self):
        self.thread = threading.Thread(target=self.write_loop)
        self.thread.stopped = False
        self.thread.start()
        return

    def stop_thread_write(self):
        self.thread.stopped = True
        return

    def clean_text_file(self):
        mytext = open("/home/pi/Desktop/DP_final/ProjectDesign/database/rawheartbeat.txt", 'w')
        mytext.write('')
        mytext.close()
        





