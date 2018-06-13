import time
import threading

class WriteReadingPulse:
    def __init__(self):
        self.user_database_txtname = ''
        
    def process_txtname(self, txt):
        txt_file_name = '/home/pi/Desktop/DP_final/ProjectDesign/database/heartbeat/'
        for data in range(len(txt)-4):
            txt_file_name = txt_file_name + txt[data]
        return txt_file_name + ".txt"

    def save_to_database(self, txt, data, data1):
        file_name = self.process_txtname(txt)
        self.user_database_txtname = file_name
        text_file = open(self.user_database_txtname, 'a')
        text_file.write('{},{}\n'.format(str(data), str(data1)))
        text_file.close()
        time.sleep(1)

    def save_thread(self, txtfile, data, data1):
        self.thread = threading.Thread(target=self.save_to_database, args=(txtfile, data, data1,))
        self.thread.start()
