"""
Kei Imada
20170604
Base code for butterworth filter, this time using arrays instead of disctionaries
"""

import math
import numpy as np
from numba import jit, autojit
import time


@jit(nopython=True, cache=True)
def _filterHelper(x, w, f, N):
    """
    x a float
    w an array of arrays of floats
    f an array of arrays of floats
    N an int
    """
    w[0][4] = x
    for m in range(N / 2):
        previousx = w[m]
        previousy = w[m + 1]
        # print previousx[4]

        ym = f[0][m] * (
            previousx[4] +
            f[1][m] * previousx[3] +
            f[2][m] * previousx[2] +
            f[3][m] * previousx[1] +
            f[4][m] * previousx[0]
        ) - (
            f[5][m] * previousy[3] +
            f[6][m] * previousy[2] +
            f[7][m] * previousy[1] +
            f[8][m] * previousy[0]
        )

        previousy[4] = ym

        for i in range(len(previousx) - 1):
            previousx[i] = previousx[i + 1]
    for i in range(len(previousy) - 1):
        previousy[i] = previousy[i + 1]
    # print w, ym
    return ym


class Butter(object):
    # TODO: finish commenting
    # TODO: tidy up class
    # TODO: clean up superfluous code
    def __init__(self, btype="lowpass", cutoff=None, cutoff1=None, cutoff2=None, rolloff=48, sampling=None):
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
        # input checking
        valid = map(lambda k: k[0], filter(lambda k: type(k[1]) in [int, float], zip(
            ["cutoff", "cutoff1", "cutoff2", "rolloff", "sampling"], [cutoff, cutoff1, cutoff2, rolloff, sampling])))
        if None in [rolloff, sampling]:
            raise ValueError(
                "Butter:rolloff and sampling required for %s filter" % btype)
        if "rolloff" not in valid:
            raise TypeError("Butter:invalid rolloff argument")
        if "sampling" not in valid:
            raise TypeError("Butter:invalid sampling argument")
        if btype in ["lowpass", "highpass", "notch"]:
            if None in [cutoff]:
                raise ValueError(
                    "Butter:cutoff required for %s filter" % btype)
            if "cutoff" not in valid:
                raise TypeError("Butter:invalid cutoff argument")
        elif btype in ["bandpass", "bandstop"]:
            if None in [cutoff1, cutoff2]:
                raise ValueError(
                    "Butter:cutoff1 and cutoff2 required for %s filter" % btype)
            if "cutoff1" not in valid:
                raise TypeError("Butter:invalid cutoff1 argument")
            if "cutoff2" not in valid:
                raise TypeError("Butter:invalid cutoff2 argument")
            if cutoff1 > cutoff2:
                raise ValueError(
                    "Butter:cutoff1 must be less than or equal to cutoff2")
        else:
            raise ValueError("Butter: invalid btype %s" % btype)
        self.btype = btype
        # initialize base filter variables
        A = float(rolloff)
        fs = float(sampling)
        Oc = cutoff
        f1 = cutoff1
        f2 = cutoff2
        B = 99.99
        wp = .3 * math.pi
        ws = 2 * wp
        d1 = B / 100.0
        d2 = 10**(math.log10(d1) - (A / 20.0))
        self.N = int(math.ceil((math.log10(((1 / (d1**2)) - 1) /
                                           ((1 / (d2**2)) - 1))) / (2 * math.log10(wp / ws))))
        if self.N % 2 == 1:
            self.N += 1
        self.wc = 10**(math.log10(wp) - (1.0 / (2 * self.N))
                       * math.log10((1 / (d1**2)) - 1))
        self.fs = fs
        self.fc = Oc
        self.f1 = f1
        self.f2 = f2

        # to store the filtered data
        self.output = []
        # to store passed in data
        self.data = []
        # list of frequencies used in calculation of filters
        self.frequencylist = np.zeros((self.N / 2 + 1, 5))

        # print "d1=%f\td2=%f" % (d1, d2)
        # print "N=%d" % self.N
        # print "wc=%fpi" % (self.wc/math.pi)

        # set variables for desired filter
        self.filter = {
            "lowpass": self._lowpassFilterVariables,
            "highpass": self._highpassFilterVariables,
            "bandpass": self._bandpassFilterVariables,
            "notch": self._notchFilterVariables,
            "bandstop": self._bandstopFilterVariables
        }[btype]()
        # for i in range(1,9,1):
        #     print("A%d: %.4f\ta1%d: %.4f\ta2%d: %.4f\ta3%d: %.4f\ta4%d: %.4f" % (i, self.filter[0](i), i, self.filter[1](i), i, self.filter[2](i), i, self.filter[3](i), i, self.filter[4](i)))
        # for i in range(1,9,1):
        #     print("b1%d: %.4f\tb2%d: %.4f\tb3%d: %.4f\tb4%d: %.4f" % (i, self.filter[5](i), i, self.filter[6](i), i, self.filter[7](i), i, self.filter[8](i)))
        # exit(0)

    def getOutput(self):
        """
        Returns accumulated output values
        @return list of float/int accumulated output values, filtered through forward-backward filtering
        """
        tempfrequencylist = [
            [0 for i in range(5)] for j in range(self.N / 2 + 1)]
        data = self.output[:]
        data.reverse()
        output = []
        for amplitude in data:
            output.append(self._filterHelper5(amplitude, tempfrequencylist))
        output.reverse()
        return output

    def send(self, data):
        """
        Send data to Butterworth filter
        @param data list of floats amplitude data to take in
        @return values from the filtered data, with forward filtering
        """
        if type(data) != list:
            raise TypeError(
                "Butter.send: type of data must be a list of floats")
        self.data += data
        output = []
        times = []
        np.set_printoptions(precision=4, suppress=True)
        for amplitude in data:
            t1 = time.time()
            # output.append(filterHelper(amplitude, self.frequencylist, self.newfilter, self.N))
            newamp = _filterHelper(
                amplitude, self.frequencylist, self.filter, self.N)
            output.append(newamp)
            # raw_input()
            # output.append(self._filterHelper5(amplitude, self.frequencylist))
            times.append(time.time() - t1)
        self.output += output
        print("fastest possible frequency for real-time filtering: %f" %
              (1.0 / (sum(times) / (len(times)))))
        return output

    # def _filterHelper(self, stacklist, m=0):
    #     """
    #     Helper for the butterworth filter
    #     @params stacklist list of Stacks containing necessary variables
    #     @params m int counter
    #     @return output of filter for the specific input
    #     """
    #     # setup
    #     k = m + 1
    #     xn = []
    #     for i in range(5):
    #         if stacklist[m].empty():
    #             xn.append(0)
    #         else:
    #             xn.append(stacklist[m].get_nowait())
    #     yn = []
    #     for i in range(5):
    #         if stacklist[k].empty():
    #             yn.append(0)
    #         else:
    #             yn.append(stacklist[k].get_nowait())
    #     # calculation
    #     newyn = self.filter[0][k] * (
    #         xn[0] +
    #         self.filter[1][k] * xn[1] +
    #         self.filter[2][k] * xn[2] +
    #         self.filter[3][k] * xn[3] +
    #         self.filter[4][k] * xn[4]
    #     ) - (
    #         self.filter[5][k] * yn[0] +
    #         self.filter[6][k] * yn[1] +
    #         self.filter[7][k] * yn[2] +
    #         self.filter[8][k] * yn[3]
    #     )
    #     # setup for next iteration
    #     for i in range(3, -1, -1):
    #         stacklist[m].put_nowait(xn[i])
    #     for i in range(2, -1, -1):
    #         stacklist[k].put_nowait(yn[i])
    #     stacklist[k].put_nowait(newyn)
    #     # print m, newyn
    #     # base case
    #     if k >= self.N / 2:
    #         # return if k==self.N/2
    #         # raw_input()
    #         return newyn
    #     # recurse if not at end
    #     return self._filterHelper(stacklist, m=m + 1)
    #
    # def _filterHelper2(self, x, w, m=0):
    #     """
    #     Helper2 for the butterworth filter
    #     @params x amplitude
    #     @params w list to store calculated frequencies
    #     @params m int counter
    #     @return output of filter for the specific input
    #     """
    #     k = m + 1
    #     # for i in range(5):
    #     #     print("w[%d]=%f" % (i, w[i]))
    #     w[4] = self.filter[0][k] * x - (
    #         self.filter[5][k] * w[3] +
    #         self.filter[6][k] * w[2] +
    #         self.filter[7][k] * w[1] +
    #         self.filter[8][k] * w[0]
    #     )
    #     y = w[4] + (
    #         self.filter[1][k] * w[3] +
    #         self.filter[2][k] * w[2] +
    #         self.filter[3][k] * w[1] +
    #         self.filter[4][k] * w[0]
    #     )
    #     for i in range(4):
    #         w[i] = w[i+1]
    #
    #     if k >= self.N/2:
    #         # return if k==self.N
    #         # print y
    #         # raw_input()
    #         return y
    #     # recurse if not at end
    #     return self._filterHelper2(y, w, m=m + 1)
    #
    # def _filterHelper3(self, x, w, m=0):
    #     """
    #     Helper 3 for the butterworth filter
    #     @params x amplitude
    #     @params w list to store calculated frequencies
    #     @params m counter
    #     @return output of filter for the specific input
    #     """
    #     k = m + 1
    #     # for i in range(5):
    #     #     print("w[%d]=%f" % (i, w[i]))
    #     w[4] = self.filter[0][k] * x - (
    #         self.filter[5][k] * w[3] +
    #         self.filter[6][k] * w[2] +
    #         self.filter[7][k] * w[1] +
    #         self.filter[8][k] * w[0]
    #     )
    #     y = w[4] + (
    #         self.filter[1][k] * w[3] +
    #         self.filter[2][k] * w[2] +
    #         self.filter[3][k] * w[1] +
    #         self.filter[4][k] * w[0]
    #     )
    #     for i in range(4):
    #         w[i] = w[i+1]
    #
    #     return y
    #
    # def _filterHelper4(self, x, w, m=0):
    #     """
    #     Helper 4 for the butterworth filter
    #     @params x amplitude
    #     @params w list to store calculated frequencies
    #     @params m counter
    #     @return output of filter for the specific input
    #     """
    #     k = m + 1
    #
    #     previousx = w[m]
    #     previousy = w[k]
    #
    #     previousx[4] = x
    #
    #     ym = self.filter[0][k] * (
    #         x +
    #         self.filter[1][k] * previousx[3] +
    #         self.filter[2][k] * previousx[2] +
    #         self.filter[3][k] * previousx[1] +
    #         self.filter[4][k] * previousx[0]
    #     ) - (
    #         self.filter[5][k] * previousy[3] +
    #         self.filter[6][k] * previousy[2] +
    #         self.filter[7][k] * previousy[1] +
    #         self.filter[8][k] * previousy[0]
    #     )
    #
    #     previousy[4] = ym
    #
    #     for i in range(len(previousx) - 1):
    #         previousx[i] = previousx[i+1]
    #
    #     if k < self.N / 2:
    #         return self._filterHelper4(ym, w, m=m+1)
    #     else:
    #         for i in range(len(previousy) - 1):
    #             previousy[i] = previousy[i+1]
    #         return ym
    #
    # def _filterHelper5(self, x, w):
    #     return filterHelper(x, np.array(w), self.newfilter, self.N)
    #
    # def _filterHelper6(self, x, w):
    #     """
    #     Helper 4 for the butterworth filter
    #     @params x amplitude
    #     @params w list to store calculated frequencies
    #     @params m counter
    #     @return output of filter for the specific input
    #     """
    #     previousx = w[0]
    #     previousy = w[1]
    #
    #     previousx[4] = x
    #     for m in range(self.N/2):
    #
    #         k=m+1
    #
    #         previousx = w[m]
    #         previousy = w[k]
    #
    #         ym = self.filter[0][k] * (
    #             previousx[4] +
    #             self.filter[1][k] * previousx[3] +
    #             self.filter[2][k] * previousx[2] +
    #             self.filter[3][k] * previousx[1] +
    #             self.filter[4][k] * previousx[0]
    #         ) - (
    #             self.filter[5][k] * previousy[3] +
    #             self.filter[6][k] * previousy[2] +
    #             self.filter[7][k] * previousy[1] +
    #             self.filter[8][k] * previousy[0]
    #         )
    #
    #         previousy[4] = ym
    #
    #         for i in range(len(previousx) - 1):
    #             previousx[i] = previousx[i+1]
    #
    #     for i in range(len(previousy) - 1):
    #         previousy[i] = previousy[i+1]
    #     return ym
    #
    # def getTransform(self, btype):
    #     """
    #     @param btype string type of filter
    #         lowpass
    #         highpass
    #         bandpass
    #         notch
    #         bandstop
    #     return lambda z analog filter function
    #     """
    #     if btype not in ["lowpass", "highpass", "bandpass", "notch"]:
    #         raise ValueError("ButterBase.getFilter: invalid btype %s" % btype)
    #     var = {
    #         "lowpass": _lowpassFilterVariables,
    #         "highpass": _highpassFilterVariables,
    #         "bandpass": _bandpassFilterVariables,
    #         "notch": _notchFilterVariables,
    #         "bandstop": _bandstopFilterVariables
    #     }[btype]()
    #
    #     def transform(z):
    #         """
    #         This will be the filter function to return
    #         """
    #         factors = map(
    #             var[0][k] * (1 + var[1][k] * (z**(-1)) + var[2][k] * (z**(-2)) + var[3][k] * (z**(-3)) + var[4][k] * (z**(-4))) / (1 + var[5][k] * (z**(-1)) + var[6][k] * (z**(-2)) + var[7][k] * (z**(-3)) + var[8][k] * (z**(-4))), [i for i in range(1, self.N / 2 + 1)])
    #         return reduce(lambda x, y: x * y, factors)
    #     return transform

    def _basicFilterVariables(self):
        """
        returns basic filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = np.zeros((9, (self.N / 2)))
        for k in range(self.N / 2):
            a = self.wc * \
                math.sin((float(2.0 * (k + 1) - 1) / (2.0 * self.N)) * math.pi)
            B = 1 + a + ((self.wc**2) / 4.0)
            basic[0][k] = (self.wc**2) / (4.0 * B)
            basic[1][k] = 2
            basic[2][k] = 1
            basic[3][k] = 0
            basic[4][k] = 0
            basic[5][k] = 2 * ((self.wc**2 / (4.0)) - 1) / (B)
            basic[6][k] = (
                1 - a + (self.wc**2 / (4.0))) / (B)
            basic[7][k] = 0
            basic[8][k] = 0

        return basic

    def _lowpassFilterVariables(self):
        """
        returns lowpass filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = self._basicFilterVariables()

        Op = 2 * (math.pi * self.fc / self.fs)
        vp = 2 * math.atan(self.wc / 2.0)

        alpha = math.sin((vp - Op) / 2.0) / \
            math.sin((vp + Op) / 2.0)

        lowpass = np.zeros((9, (self.N / 2)))
        for k in range(self.N / 2):
            C = 1 - basic[5][k] * \
                alpha + basic[6][k] * (alpha**2)
            a = self.wc * \
                math.sin((float(2.0 * (k + 1) - 1) / (2.0 * self.N)) * math.pi)
            B = 1 + a + ((self.wc**2) / 4.0)
            lowpass[0][k] = ((1 - alpha)**2) * basic[0][k] / C
            lowpass[1][k] = basic[1][k]
            lowpass[2][k] = basic[2][k]
            lowpass[3][k] = basic[3][k]
            lowpass[4][k] = basic[4][k]
            lowpass[5][k] = (
                (1 + alpha**2) * basic[5][k] - 2 * alpha * (1 + basic[6][k])) / C
            lowpass[6][k] = (
                alpha**2 - basic[5][k] * alpha + basic[6][k]) / C
            lowpass[7][k] = basic[7][k]
            lowpass[8][k] = basic[8][k]
        return lowpass

    def _highpassFilterVariables(self):
        """
        returns highpass filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = self._basicFilterVariables()
        Op = 2 * (math.pi * float(self.fc) / self.fs)
        vp = 2 * math.atan(self.wc / 2.0)

        alpha = -(math.cos((vp + Op) / (2.0))) / \
            (math.cos((vp - Op) / (2.0)))

        highpass = np.zeros((9, (self.N / 2)))
        for k in range(self.N / 2):
            C = 1 - basic[5][k] * \
                alpha + basic[6][k] * (alpha**2)
            highpass[0][k] = ((1 - alpha)**2) * basic[0][k] / C
            highpass[1][k] = -basic[1][k]
            highpass[2][k] = basic[2][k]
            highpass[3][k] = basic[3][k]
            highpass[4][k] = basic[4][k]
            highpass[5][k] = (
                -(1.0 + alpha**2) * basic[5][k] + 2 * alpha * (1 + basic[6][k])) / C
            highpass[6][k] = (
                float(alpha**2) - basic[5][k] * alpha + basic[6][k]) / C
            highpass[7][k] = basic[7][k]
            highpass[8][k] = basic[8][k]
        return highpass

    def _bandpassFilterVariables(self):
        """
        returns bandpass filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = self._basicFilterVariables()
        Op1 = 2 * (math.pi * (self.f1) / self.fs)
        Op2 = 2 * (math.pi * (self.f2) / self.fs)
        alpha = math.cos((Op2 + Op1) / 2.0) / math.cos((Op2 - Op1) / 2.0)
        k = (self.wc / 2.0) / math.tan((Op2 - Op1) / 2.0)
        A = 2 * alpha * k / (k + 1)
        B = (k - 1) / (k + 1)

        bandpass = np.zeros((9, (self.N / 2)))
        for k in range(self.N / 2):
            C = 1 - basic[5][k] * B + basic[6][k] * (B**2)

            bandpass[0][k] = basic[0][k] * ((1 - B)**2) / C
            bandpass[1][k] = 0  # -basic[1][k]
            bandpass[2][k] = -basic[1][k]
            bandpass[3][k] = 0  # basic[3][k]
            bandpass[4][k] = basic[2][k]  # basic[4][k]
            bandpass[5][k] = (A / C) * (B * (basic[5][k] -
                                             2 * basic[6][k]) + (basic[5][k] - 2))
            bandpass[6][k] = (1 / C) * ((A**2) * (1 - basic[5][k] + basic[6][k]) +
                                        2 * B * (1 + basic[6][k]) - basic[5][k] * (B**2) - basic[5][k])
            bandpass[7][k] = (A / C) * (B * (basic[5][k] - 2) +
                                        (basic[5][k] - 2 * basic[6][k]))
            bandpass[8][k] = (1 / C) * ((B**2) - basic[5][k] * B + basic[6][k])
        return bandpass

    def _notchFilterVariables(self):
        """
        returns notch filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = self._basicFilterVariables()
        x = 1.0
        f1 = (1.0 - (x / 100)) * self.fc
        f2 = (1.0 + (x / 100)) * self.fc
        Op1 = 2 * (math.pi * f1 / self.fs)
        Op2 = 2 * (math.pi * f2 / self.fs)
        alpha = math.cos((Op2 + Op1) / 2.0) / math.cos((Op2 - Op1) / 2.0)
        k = (self.wc / 2.0) * math.tan((Op2 - Op1) / 2.0)
        A = 2 * alpha / (k + 1)
        B = (1 - k) / (1 + k)

        notch = np.zeros((9, (self.N / 2)))
        for k in range(self.N / 2):
            C = 1 + basic[5][k] * \
                B + basic[6][k] * (B**2)
            notch[0][k] = basic[0][k] * ((1 + B)**2) / C
            notch[1][k] = -4.0 * A / (B + 1)
            notch[2][k] = 2.0 * ((2 * (A**2)) / ((B + 1)**2) + 1)
            notch[3][k] = -4.0 * A / (B + 1)
            notch[4][k] = 1
            notch[5][k] = -(A / C) * \
                (B * (basic[5][k] + 2 * basic[6][k]) +
                 (2 + basic[5][k]))
            notch[6][k] = (1 / C) * \
                ((A**2) * (1 + basic[5][k] + basic[6][k]) +
                 2 * B * (1 + basic[6][k]) +
                 basic[5][k] * (B**2) +
                 basic[5][k])
            notch[7][k] = -(A / C) * \
                (B * (basic[5][k] + 2) +
                 (basic[5][k] + 2 * basic[6][k]))
            notch[8][k] = (1 / C) * \
                ((B**2) +
                 basic[5][k] * B +
                 basic[6][k])
        return notch

    def _bandstopFilterVariables(self):
        """
        returns bandstop filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = self._basicFilterVariables()
        Op1 = 2 * (math.pi * self.f1 / self.fs)
        Op2 = 2 * (math.pi * self.f2 / self.fs)
        alpha = math.cos((Op2 + Op1) / 2.0) / math.cos((Op2 - Op1) / 2.0)
        k = (self.wc / 2.0) * math.tan((Op2 - Op1) / 2.0)
        A = 2 * alpha / (k + 1)
        B = (1 - k) / (1 + k)

        bandstop = np.zeros((9, (self.N / 2)))
        for k in range(self.N / 2):
            C = 1 + basic[5][k] * \
                B + basic[6][k] * (B**2)
            bandstop[0][k] = basic[0][k] * ((1 + B)**2) / C
            bandstop[1][k] = -4.0 * A / (B + 1)
            bandstop[2][k] = 2.0 * ((2 * (A**2)) / ((B + 1)**2) + 1)
            bandstop[3][k] = -4.0 * A / (B + 1)
            bandstop[4][k] = 1
            bandstop[5][k] = -(A / C) * \
                (B * (basic[5][k] + 2 * basic[6][k]) +
                 (2 + basic[5][k]))
            bandstop[6][k] = (1 / C) * \
                ((A**2) * (1 + basic[5][k] + basic[6][k]) +
                 2 * B * (1 + basic[6][k]) +
                 basic[5][k] * (B**2) +
                 basic[5][k])
            bandstop[7][k] = -(A / C) * \
                (B * (basic[5][k] + 2) +
                 (basic[5][k] + 2 * basic[6][k]))
            bandstop[8][k] = (1 / C) * \
                ((B**2) +
                 basic[5][k] * B +
                 basic[6][k])
        return bandstop


def main():
    Butter(btype="bandpass", cutoff=100, cutoff1=200,
           cutoff2=300, rolloff=48, sampling=3109)


if __name__ == "__main__":
    main()
