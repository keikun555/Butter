"""
Kei Imada
20170725
Base code for WAVfilter
"""
from filters.butterbase2 import Butter
import wave
import numpy as np

import __builtin__

__all__ = ["open"]

def open(f):
    return WAVfilter(f)

class WAVfilter(object):
    def __init__(self, f):
        self._file = wave.open(f, "r")
        data = np.fromstring(self._file.readframes(self._file.getnframes()), dtype=np.int16)
        self._amparray = data.tolist()
        print len(self._amparray)
        # init = self._amparray[0]
        # for i in range(100):
        #     print self._amparray[i] - init
        # print type(init)
        self._fparams = self._file.getparams()
        self._filterSet = False
    def __del__(self):
        self._file.close()
    def set_filter(self, btype="lowpass", cutoff=None, cutoff1=None, cutoff2=None, rolloff=48):
        """
        @param btype string type of filter, default lowpass
            lowpass
            highpass
            bandpass
            notch
            bandstop
        filter required arguments
            @param rolloff float measured in dB/Oct, default 48Hz
            @param sampling float measured in Hz
        lowpass filter required arguments
            @param cutoff float measured in Hz
        highpass filter required arguments
            @param cutoff float measured in Hz
        bandpass filter required arguments
            @param cutoff1 float measured in Hz
            @param cutoff2 float measured in Hz
            cutoff1 =< cutoff2
        notch filter required arguments
            @param cutoff float measured in Hz
        bandstop filter required arguments
            @param cutoff1 float measured in Hz
            @param cutoff2 float measured in Hz
            cutoff1 =< cutoff2
        """
        self._filter = Butter(btype=btype, cutoff=cutoff, cutoff1=cutoff1, cutoff2=cutoff2, rolloff=rolloff, sampling=self._file.getframerate())
        self._filterSet = True
    def write(self, f):
        if not self._filterSet:
            raise Exception("WAVfilter.write you must use set_filter to set your filter")
        data = self._filter.send(self._amparray)
        for (i, j) in zip(self._amparray, np.int16(data)):
            print i, j
        # data = self._filter.getOutput()
        out = wave.open(f, "w")
        out.setparams(self._fparams)
        # print np.int16(np.array(data))
        out.writeframes(np.int16(np.array(data)).tostring())

        exit(0)
        raise NotImplementedError("write")
