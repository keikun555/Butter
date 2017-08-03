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
        self.record_check = False
        self.play_check = False
        self.type_switch = False #False for file, True for record
        self.filter_queue = Queue.Queue()
        self.play_queue = Queue.Queue()
        self.raw_queue = Queue.Queue()
        self.filter_thread = threading.Thread(
            target=self.__filter_play_link, args=(self.filter_queue, self.play_queue,))
        self.play_thread = threading.Thread(
            target=self.__play_process, args=(self.play_queue,))
        self.record_thread = threading.Thread(
            target=self.__record_process, args=(self.filter_queue, self.play_queue,))

        self.record_thread.start()
        self.filter_thread.start()
        self.play_thread.start()

    def close(self):
        self.on = False
        self.play_check = False
        self.record_thread.join()
        self.filter_thread.join()
        self.play_thread.join()

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
        except:
            self.filter = None

    def delete_filter(self):
        self.filter = None

    def update_filter_check(self, boolean):
        self.filter_check = boolean

    def switch_record_check(self):
        if not self.record_check:
            self.reset()
        self.record_check = not self.record_check

    def reset(self):
        self.play_check = False
        if self.filter != None:
            self.reload_filter()
        while not self.raw_queue.empty():
            self.raw_queue.get()

    def open(self, fin):
        self.reset()
        self.record_check = False
        file_ = wave.open(fin, "r")
        fparams = file_.getparams()
        if fparams[1] == 1:
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
                    return
                self.raw_queue.put_nowait(chunk)

        if fparams[0] == 1:
            thread = threading.Thread(target=open_thread, args=(file_,))
            thread.start()
        else:
            raise NotImplementedError("Stereo not implemented yet sorry :p")


    def play(self):
        self.play_check = True
        def play_thread():
            if self.filter_check and self.filter != None:
                queue = self.filter_queue
            else:
                queue = self.play_queue
            while not self.raw_queue.empty():
                frame = self.raw_queue.get_nowait()
                queue.put_nowait(frame)
                self.raw_queue.put_nowait(frame)
                if not self.play_check:
                    break
            return
        thread = threading.Thread(target=play_thread)
        thread.start()

    def stop(self):
        self.play_check = False

    def __record_process(self, filterQ, playQ):
        while self.on:
            if self.record_check:
                self.raw_queue.put_nowait(self.audio_stream_in.read(CHUNK))

    def __filter_play_link(self, filterQ, playQ):
        while self.on:
            if not filterQ.empty():
                print "filtering!"
                data = np.fromstring(filterQ.get(), dtype=np.int16).tolist()
                filt = self.filter.send(data)
                playQ.put_nowait(
                    (np.array(output).astype(self._tp)).tostring())

    def __play_process(self, playQ):
        while self.on:
            if not playQ.empty():
                self.audio_stream_out.write(playQ.get_nowait())
