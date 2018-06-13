import pyttsx3

def read_text(msg):
	engine = pyttsx3.init()
	voices = engine.getProperty('voices')
	engine.setProperty('rate',110)
	engine.setProperty('volume',1)
	engine.setProperty('voice', 'english-us')
	engine.say(msg)
	engine.runAndWait()

read_text("Hello Hello")