"""
Kei Imada
20170802
Filter for the EQ
"""
__all__ = ["EQFilter"]
__version__ = "1.0"
__author__ = "Kei Imada"

from butterbase import *
import Queue
import threading
import pyaudio as pa
import time
import atexit

FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 64


class EQFilter(object):
    def __init__(self):
        self.filter = None
        audio = pa.PyAudio()
        self.audio_stream_in = audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, input=True,
                                          frames_per_buffer=CHUNK)
        self.audio_stream_out = audio.open(format=FORMAT, channels=CHANNELS,
                                           rate=RATE, output=True,
                                           frames_per_buffer=CHUNK)
        self.on = True
        self.filter_check = False
        self.record_check = True
        self.filter_queue = Queue.Queue()
        self.play_queue = Queue.Queue()
        self.filter_thread = threading.Thread(
            target=self.__filter_play_link, args=(self.filter_queue, self.play_queue,))
        self.play_thread = threading.Thread(
            target=self.__play_process, args=(self.play_queue,))
        self.record_thread = threading.Thread(
            target=self.__record_process, args=(self.audio_stream_in, self.filter_queue, self.play_queue,))

        self.filter_thread.start()
        self.play_thread.start()
        self.record_thread.start()
        atexit.register(self._destructor)

    def _destructor(self):
        self.on = False
        self.filter_thread.join()
        self.play_thread.join()
        self.record_thread.join()

    def reload_filter(self, btype=None, cutoff=None,
                      cutoff1=None, cutoff2=None,
                      rolloff=None, sampling=None):
        if self.filter != None:
            self.filter = Butter(btype, cutoff,
                                 cutoff1, cutoff2,
                                 rolloff, sampling)
            return
        if btype != None:
            self.btype = btype
        if cutoff != None:
            self.cutoff = cutoff
        if cutoff1 != None:
            self.cutoff1 = cutoff1
        if cutoff2 != None:
            self.cutoff2 = cutoff2
        if rolloff != None:
            self.rolloff = rolloff
        if sampling != None:
            self.sampling = sampling
        del self.filter
        self.filter = Butter(self.btype, self.cutoff,
                             self.cutoff1, self.cutoff2,
                             self.rolloff, self.sampling)

    def update_filter_check(self, boolean):
        self.filter_check = boolean

    def __record_process(self, stream, filterQ, playQ):
        while self.on:
            if self.record_check:
                data = stream.read(CHUNK)
                if self.filter_check:
                    filterQ.put_nowait(data)
                else:
                    playQ.put_nowait(data)

    def __filter_play_link(self, filterQ, playQ):
        while self.on:
            if not filterQ.empty():
                data = np.fromstring(filterQ.get(), dtype=np.int16).tolist()
                filt = self.filter.send(data)
                playQ.put_nowait(
                    (np.array(output).astype(self._tp)).tostring())

    def __play_process(self, playQ):
        while self.on:
            self.audio_stream_out.write(playQ.get())
