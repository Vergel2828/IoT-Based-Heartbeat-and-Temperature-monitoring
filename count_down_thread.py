import time
import threading

class CounterThread:
    def __init__(self):
        self.is_done = False

    def count_seconds(self, num):
        loop = num
        while loop > 0:
            time.sleep(1)
            loop = loop - 1
            print (loop)
        self.is_done = True

    def start_cnt_thread(self, num):
        self.thread = threading.Thread(target=self.count_seconds, args=(num,))
        self.thread.start()
            
