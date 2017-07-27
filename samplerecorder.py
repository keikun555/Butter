import pyaudio
import wave
import numpy as np
from filters.butterbase2 import Butter

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 64
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "file.wav"

T = "lowpass"
butter = Butter(cutoff=10000, cutoff1=0, cutoff2=1000, rolloff=48, sampling=RATE, btype="%s" % T)

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True, output=True,
                frames_per_buffer=CHUNK)
print "recording..."
frames = []
d = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
    fil = butter.send(np.fromstring(data, dtype=np.int16).tolist())
    # d += np.fromstring(data, dtype=np.int16).tolist()
    fil = (np.array(fil).astype(np.int16)).tostring()
    stream.write(fil)
print "finished recording"
# for i in range(100):
#     print d[i]

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

# waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
# waveFile.setnchannels(CHANNELS)
# waveFile.setsampwidth(audio.get_sample_size(FORMAT))
# waveFile.setframerate(RATE)
# waveFile.writeframes(b''.join(frames))
# waveFile.close()
