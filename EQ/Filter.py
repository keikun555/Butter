"""
Kei Imada
20170802
Filter for the EQ
"""
__all__ = ["EQFilter"]
__version__ = "1.0"
__author__ = "Kei Imada"

from butterbase import *
import pyaudio as pa
import numpy as np
import threading
import Queue
import wave

FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 256


class EQFilter(object):
    def __init__(self):
        self.delete_filter()
        audio = pa.PyAudio()
        self.audio_stream_in = audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, input=True,
                                          frames_per_buffer=CHUNK)
        self.audio_stream_out = audio.open(format=FORMAT, channels=CHANNELS,
                                           rate=RATE, output=True,
                                           frames_per_buffer=CHUNK)
        self.filter_check = False
        self.record_check = False
        self.play_check = False
        self.type_switch = False  # False for file, True for record
        self.filter_queue = Queue.Queue()
        self.play_queue = Queue.Queue(maxsize=10)
        self.raw_queue = Queue.Queue()
        self.filter_thread = threading.Thread(
            target=self.__filter_play_link, args=(self.filter_queue, self.play_queue,))
        self.play_thread = threading.Thread(
            target=self.__play_process, args=(self.play_queue, self.filter_queue, self.raw_queue))
        self.record_thread = threading.Thread(
            target=self.__record_process, args=(self.raw_queue,))

    def close(self):
        self.reset()

    def reload_filter(self, btype=None, cutoff=None,
                      cutoff1=None, cutoff2=None,
                      rolloff=None, sampling=None):
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
        try:
            self.filter = Butter(self.btype, self.cutoff,
                                 self.cutoff1, self.cutoff2,
                                 self.rolloff, self.sampling)
        except Exception as e:
            print e
            self.filter = None

    def delete_filter(self):
        self.filter = None
        self.btype = None
        self.cutoff = None
        self.cutoff1 = None
        self.cutoff2 = None
        self.rolloff = None
        self.sampling = None

    def filter_(self, boolean):
        self.filter_check = boolean

    def record(self, boolean):
        self.record_check = boolean
        if boolean and not self.record_thread.isAlive():
            self.reset()
            self.record_thread.start()
        elif not boolean and self.record_thread.isAlive():
            self.record_thread.join()
            self.record_thread = threading.Thread(
                target=self.__record_process, args=(self.raw_queue,))

    def switch_record_check(self):
        self.record(not self.record_check)

    def reset(self):
        self.play(False)
        self.record(False)
        if self.filter != None:
            self.reload_filter()
        while not self.raw_queue.empty():
            self.raw_queue.get_nowait()

    def open(self, fin):
        self.reset()
        self.record_check = False
        file_ = wave.open(fin, "r")
        (nchannels, sampwidth, framerate, nframes,
         comptype, compname) = file_.getparams()
        self.reload_filter(sampling=framerate)
        if sampwidth == 1:
            # nbytesframe
            print "uint8!?"
            tp = np.uint8
        else:
            tp = np.int16
        # data = np.fromstring(file_.readframes(file_.getnframes()), dtype=tp).tolist()

        def open_thread(file_):
            while True:
                chunk = file_.readframes(CHUNK)
                if chunk == "":
                    break
                self.raw_queue.put_nowait(chunk)

        if nchannels == 1:
            thread = threading.Thread(target=open_thread, args=(file_,))
            thread.start()
        else:
            raise NotImplementedError("Stereo not implemented yet sorry :p")

    def play(self, boolean):
        self.play_check = boolean
        if boolean and not self.filter_thread.isAlive():
            self.filter_thread.start()
        elif not boolean and self.filter_thread.isAlive():
            self.filter_thread.join()
            self.filter_thread = threading.Thread(
                target=self.__filter_play_link, args=(self.filter_queue, self.play_queue,))
        if boolean and not self.play_thread.isAlive():
            self.play_thread.start()
        elif not boolean and self.play_thread.isAlive():
            self.play_thread.join()
            self.play_thread = threading.Thread(
                target=self.__play_process, args=(self.play_queue, self.filter_queue, self.raw_queue))

    def __record_process(self, rawQ):
        while self.record_check:
            rawQ.put_nowait(self.audio_stream_in.read(CHUNK))

    def __filter_play_link(self, filterQ, playQ):
        while self.play_check:
            if not filterQ.empty():
                chunk = filterQ.get_nowait()
                if self.filter != None:
                    chunkL = np.fromstring(chunk, dtype=np.int16).tolist()
                    filteredChunk = self.filter.send(chunkL)
                    playQ.put(
                        (np.array(filteredChunk).astype(np.int16)).tostring())
                else:
                    playQ.put(chunk)

    def __play_process(self, playQ, filterQ, rawQ):
        while self.play_check:
            while not playQ.empty():
                self.audio_stream_out.write(playQ.get_nowait())
            if not rawQ.empty():
                chunk = rawQ.get_nowait()
                if self.filter_check:
                    filterQ.put_nowait(chunk)
                else:
                    playQ.put(chunk)
                rawQ.put_nowait(chunk)
