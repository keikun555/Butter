"""
Kei Imada
20170802
Filter for the EQ
"""
__all__ = ["EQFilter"]
__version__ = "1.0"
__author__ = "Kei Imada"

from butter import *
import pyaudio as pa
import numpy as np
import threading
import Queue
import wave


class EQFilter(object):
    # TODO Privitize variables
    def __init__(self, channels=1, rate=44100, chunk=256):
        """Constructor for the filter object used in KEQ
        @params channels int number of channels for the audio (1 for mono, 2 for stereo)
        @params rate int the sampling frequency rate in Hz
        @params chunk int the number of frames per buffer
        """
        self.__pyaudio = pa.PyAudio()
        self.__stream_format = (pa.paInt16, np.int16)
        self.__stream_channels = channels
        self.__stream_rate = rate
        self.__stream_chunk = chunk
        self.delete_filter()
        self.__audio_stream_in = self.__pyaudio.open(format=self.__stream_format[0],
                                                     channels=self.__stream_channels,
                                                     rate=self.__stream_rate, input=True,
                                                     frames_per_buffer=self.__stream_chunk
                                                     )
        self.__audio_stream_out = self.__pyaudio.open(format=self.__stream_format[0],
                                                      channels=self.__stream_channels,
                                                      rate=self.__stream_rate, output=True,
                                                      frames_per_buffer=self.__stream_chunk)
        self.__filter = None
        self.__filter_copy = None
        self.__filter_check = False
        self.__record_check = False
        self.__play_check = False
        self.__filter_queue = Queue.Queue()
        self.__play_queue = Queue.Queue(maxsize=10)
        self.__raw_queue = Queue.Queue()
        self.__filter_thread = threading.Thread(
            target=self.__filter_play_link, args=(self.__filter_queue, self.__play_queue,))
        self.__play_thread = threading.Thread(
            target=self.__play_process, args=(self.__play_queue, self.__filter_queue, self.__raw_queue))
        self.__record_thread = threading.Thread(
            target=self.__record_process, args=(self.__raw_queue,))

    def reset(self):
        """Resets the whole filter object"""
        self.play(False)
        self.record(False)
        if self.__filter != None:
            self.reload_filter()
        while not self.__raw_queue.empty():
            self.__raw_queue.get_nowait()

    def reload_filter(self, btype=None, cutoff=None,
                      cutoff1=None, cutoff2=None,
                      rolloff=None, sampling=None):
        """Reloads filter with the desired constants"""
        if btype != None:
            self.__btype = btype
        if cutoff != None:
            self.__cutoff = cutoff
        if cutoff1 != None:
            self.__cutoff1 = cutoff1
        if cutoff2 != None:
            self.__cutoff2 = cutoff2
        if rolloff != None:
            self.__rolloff = rolloff
        if sampling != None:
            self.__sampling = sampling
        try:
            self.__filter = Butter(self.__btype, self.__cutoff,
                                   self.__cutoff1, self.__cutoff2,
                                   self.__rolloff, self.__sampling)
            self.__filter_copy = Butter(self.__btype, self.__cutoff,
                                        self.__cutoff1, self.__cutoff2,
                                        self.__rolloff, self.__sampling)
        except Exception as e:
            self.__filter = None
            self.__filter_copy = None

    def reload_streams(self, channels=None, rate=None, chunk=None):
        """Reloads streams with desired constants"""
        if channels != None:
            self.__stream_channels = channels
        if rate != None:
            self.__stream_rate = rate
        if chunk != None:
            self.__stream_chunk = chunk
        try:
            self.__reload_audio_streams(self)
        except Exception as e:
            pass


    def delete_filter(self):
        """Resets the filter to None"""
        self.__filter = None
        self.__filter_copy = None
        self.__btype = None
        self.__cutoff = None
        self.__cutoff1 = None
        self.__cutoff2 = None
        self.__rolloff = None
        self.__sampling = None

    def open(self, fin):
        """Opens .wav file designated by user
        @params fin the filepath to the file
        """
        self.reset()
        self.__record_check = False
        file_ = wave.open(fin, "r")
        (nchannels, sampwidth, framerate, nframes,
         comptype, compname) = file_.getparams()
        self.__stream_channels = nchannels
        self.__stream_rate = framerate
        if sampwidth == 1:
            self.__stream_format = (pa.paInt8, np.int8)
        else:
            self.__stream_format = (pa.paInt16, np.int16)
        self.reload_filter(sampling=framerate)
        self.__reload_audio_streams()

        def open_thread(file_):
            while True:
                chunk = file_.readframes(self.__stream_chunk)
                if chunk == "":
                    break
                self.__raw_queue.put_nowait(chunk)

        thread = threading.Thread(target=open_thread, args=(file_,))
        thread.start()

    def record(self, boolean):
        """Enable/disables recording of data
        @params boolean True if enable, False if disable
        """
        self.__record_check = boolean
        if boolean:
            if not self.__record_thread.isAlive():
                self.reset()
                self.__reload_audio_streams()
                self.__record_thread.start()
        elif not boolean:
            if self.__record_thread.isAlive():
                self.__record_thread.join()
            self.__record_thread = threading.Thread(
                target=self.__record_process, args=(self.__raw_queue,))

    def filter_(self, boolean):
        """Enable/disables filtering on data
        @params boolean True if enable, False if disable
        """
        self.__filter_check = boolean

    def play(self, boolean):
        """Enable/disables playing audio
        @params boolean True if enable, False if disable
        """
        self.__play_check = boolean
        if boolean:
            if not self.__filter_thread.isAlive():
                self.__filter_thread.start()
            if not self.__play_thread.isAlive():
                self.__play_thread.start()
        elif not boolean:
            if self.__filter_thread.isAlive():
                self.__filter_thread.join()
            if self.__play_thread.isAlive():
                self.__play_thread.join()
            self.__filter_thread = threading.Thread(
                target=self.__filter_play_link, args=(self.__filter_queue, self.__play_queue,))
            self.__play_thread = threading.Thread(
                target=self.__play_process, args=(self.__play_queue, self.__filter_queue, self.__raw_queue))

    def __record_process(self, rawQ):
        """The process used to record audio
        @params rawQ the Queue to put the data in
        """
        while self.__record_check:
            rawQ.put_nowait(self.__audio_stream_in.read(self.__stream_chunk))

    def __filter_play_link(self, filterQ, playQ):
        """The process used to filter audio
        @params filterQ the Queue to read the data from
        @params playQ the Queue to write the filtered data to
        """
        while self.__play_check:
            if not filterQ.empty():
                chunk = filterQ.get_nowait()
                if self.__filter != None:
                    chunkL = np.fromstring(
                        chunk, dtype=self.__stream_format[1]).tolist()
                    if self.__stream_channels == 1:
                        filteredChunk = self.__filter.send(chunkL)
                        playQ.put(
                            (np.array(filteredChunk).astype(self.__stream_format[1])).tostring())
                    elif self.__stream_channels == 2:
                        chunkLL = chunkL[::2]
                        chunkLR = chunkL[1::2]
                        chunkLLF = self.__filter.send(chunkLL)
                        chunkLRF = self.__filter_copy.send(chunkLR)
                        chunkF = [None for i in range(
                            len(chunkLLF) + len(chunkLRF))]
                        chunkF[::2] = chunkLLF
                        chunkF[1::2] = chunkLRF
                        playQ.put(chunkF)
                else:
                    playQ.put(chunk)

    def __play_process(self, playQ, filterQ, rawQ):
        """The process used to play audio
        @params playQ the Queue to read data from to play audio
        @params filterQ the Queue to write the data to if filtering audio
        @params rawQ the Queue to read the data from to write to playQ or filterQ
        """
        while self.__play_check:
            while not playQ.empty():
                self.__audio_stream_out.write(playQ.get_nowait())
            if not rawQ.empty():
                chunk = rawQ.get_nowait()
                if self.__filter_check:
                    filterQ.put_nowait(chunk)
                else:
                    playQ.put(chunk)
                rawQ.put_nowait(chunk)

    def __reload_audio_streams(self):
        """Reloads audio streams with the desired constants"""
        self.__audio_stream_in.close()
        self.__audio_stream_in = self.__pyaudio.open(format=self.__stream_format[0],
                                                     channels=self.__stream_channels,
                                                     rate=self.__stream_rate, input=True,
                                                     frames_per_buffer=self.__stream_chunk
                                                     )
        self.__audio_stream_out.close()
        self.__audio_stream_out = self.__pyaudio.open(format=self.__stream_format[0],
                                                      channels=self.__stream_channels,
                                                      rate=self.__stream_rate, output=True,
                                                      frames_per_buffer=self.__stream_chunk)
