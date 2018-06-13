import requests
import threading
try:
    import httplib
except:
    import http.client as httplib

class SendToDatabase:
    def __init__(self):
        self.access_url = 'http://vergel2828.pythonanywhere.com/health/heartpulse/'
        self.connections = 'Not Connected'

    def data_to_be_send(self, detail, heartbeat, heartbeat_time, temp, temp_time):
        if self.have_internet():
            self.connections = 'Connected'
            if len(detail) == 0:
                pass
            else:
                self.access_url = self.access_url + detail[0] + '/' + detail[1] + '/' + detail[2] + '/'
                self.access_url = self.access_url + heartbeat + '/' + heartbeat_time + '/'
                self.access_url = self.access_url + temp + '/' + temp_time
                #print ('\n -------------')
                #print (self.access_url)
                r = requests.get(self.access_url)
                #print(r.url)
                self.access_url = 'http://vergel2828.pythonanywhere.com/health/heartpulse/'
        else:
            self.connections = 'Not Connected'
        
    def send_thread(self, detail, heartbeat, heartbeat_time, temp, temp_time):
        self.thread = threading.Thread(target = self.data_to_be_send, args=(detail, heartbeat, heartbeat_time, temp, temp_time,))
        self.thread.start()


    def have_internet(self):
        conn = httplib.HTTPConnection("www.google.com", timeout=5)
        try:
            conn.request("Head", "/")
            conn.close()
            return True
        except:
            conn.close()
            return False
        
    
