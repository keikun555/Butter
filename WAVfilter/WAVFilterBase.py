"""
Kei Imada
20170725
Base code for WAVfilter
"""
__all__ = ["open"]

from butter import *
import wave
import numpy as np

import __builtin__


def open(f):
    return WAVFilter(f)


class WAVFilter(object):
    def __init__(self, f):
        """Constructor for the WAVfilter class
        @params f the filename to read in
        """
        self._file = wave.open(f, "r")
        self._fparams = self._file.getparams()
        if self._fparams[1] == 1:
            # nbytesframe
            self._tp = np.uint8
        else:
            self._tp = np.int16
        data = np.fromstring(self._file.readframes(
            self._file.getnframes()), dtype=self._tp).tolist()
        if self._fparams[0] == 1:
            self._stereo = False
            self._mono = data
        else:
            self._stereo = True
            self._left = data[::2]
            self._right = data[1::2]

        # init = self._amparray[0]
        # for i in range(100):
        #     print self._amparray[i] - init
        # print type(init)
        self._filterSet = False

    def __del__(self):
        self._file.close()

    def set_filter(self, btype="lowpass", cutoff=None, cutoff1=None, cutoff2=None, rolloff=48):
        """Sets the filter
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
        self._filter = Butter(btype=btype, cutoff=cutoff, cutoff1=cutoff1,
                              cutoff2=cutoff2, rolloff=rolloff, sampling=self._file.getframerate())
        if self._stereo:
            self._filter2 = Butter(btype=btype, cutoff=cutoff, cutoff1=cutoff1,
                                   cutoff2=cutoff2, rolloff=rolloff, sampling=self._file.getframerate())
        self._filterSet = True

    def write(self, f):
        """Filter data and write to file
        @params f filepath to write the file
        """
        if not self._filterSet:
            if self._stereo:
                output = [None for i in range(len(fleft) + len(fright))]
                output[::2] = self._left
                output[1::2] = self._right
            else:
                output = self._mono
        elif self._stereo:
            # TODO use multithreading to do concurrent filtering with fleft and fright
            fleft = self._filter.send(self._left)
            fright = self._filter2.send(self._right)
            output = [None for i in range(len(fleft) + len(fright))]
            output[::2] = fleft
            output[1::2] = fright
        else:
            output = self._filter.send(self._mono)
        # for (i, j) in zip(self._amparray, np.int16(data)):
        #     print i, j
        # data = self._filter.getOutput()
        out = wave.open(f, "w")
        out.setparams(self._fparams)
        # print np.int16(np.array(data))
        out.writeframes((np.array(output).astype(self._tp)).tostring())
