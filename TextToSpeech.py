from gtts import gTTS
import os
import pyttsx3
import threading
import time
try:
    import httplib
except:
    import http.client as httplib

class TextToSpeech:
    def __init__(self):
        self.alarms_list_done = []

    def have_internet(self):
        conn = httplib.HTTPConnection("www.google.com", timeout=5)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return True
        except:
            conn.close()
            return False

    def girl_voice(self, msg):
        tts = gTTS(text = msg, lang = 'en')
        tts.save("msg.mp3")
        os.system("mpg321 msg.mp3")

    def robot_voice(self, msg):
        engine = pyttsx3.init()
        engine.say(msg)
        engine.setProperty('rate',100)  #120 words per minute
        engine.setProperty('volume',0.9) 
        engine.runAndWait()

    def msg_process(self, msg):
        for x in range(len(msg)):
            if self.have_internet():
                self.girl_voice(msg[x])
            else:
                self.robot_voice(msg[x])
            time.sleep(5)

    def start_talk(self, msg):
        self.thread = threading.Thread(target=self.msg_process, args=(msg,))
        self.thread.start()
        return


