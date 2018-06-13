#from TextToSpeech import TextToSpeech
#tts = TextToSpeech()
#msg = ["Hello there please kill me now! thank you"]
#tts.start_talk(msg)

from gtts import gTTS
import os
tts = gTTS(text='Good morning', lang='en')
tts.save('good.mp3')
os.system('mpg321 good.mp3')



