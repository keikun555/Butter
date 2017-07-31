import pyaudio
import wave
import numpy as np
from filters.butterbase2 import Butter
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "file.wav"

T = "lowpass"
butter = Butter(cutoff=10000, cutoff1=0, cutoff2=1000, rolloff=48, sampling=RATE, btype="%s" % T)

audio = pyaudio.PyAudio()

# start Recording
streamIN = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
streamOUT= audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, output=True,
                frames_per_buffer=CHUNK)
print "recording..."
frames = []
d = []
threads = []

def filterOutStream(data):
    # print streamOUT.get_write_available()
    fil = butter.send(np.fromstring(data, dtype=np.int16).tolist())
    # d += np.fromstring(data, dtype=np.int16).tolist()
    fil = (np.array(fil).astype(np.int16)).tostring()
    streamOUT.write(fil)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = streamIN.read(CHUNK)
    frames.append(data)
    t = threading.Thread(target=filterOutStream, args=(data,))
    t.start()
    threads.append(t)


print "finished recording"
# for i in range(100):
#     print d[i]

for t in threads:
    t.join()

# stop Recording
streamIN.stop_stream()
streamIN.close()
streamOUT.stop_stream()
streamOUT.close()
audio.terminate()

# waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(audio.get_sample_size(FORMAT))
# waveFile.setframerate(RATE)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()
