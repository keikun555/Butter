"""
Kei Imada
20170604
Base code for butterworth filter
"""

import math
import array


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
        self.frequencylist = [[0 for i in range(5)] for j in range(self.N / 2 + 1)]

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
        #     print("A%d: %.4f\ta1%d: %.4f\ta2%d: %.4f\ta3%d: %.4f\ta4%d: %.4f" % (i, self.filter["A"](i), i, self.filter["a1"](i), i, self.filter["a2"](i), i, self.filter["a3"](i), i, self.filter["a4"](i)))
        # for i in range(1,9,1):
        #     print("b1%d: %.4f\tb2%d: %.4f\tb3%d: %.4f\tb4%d: %.4f" % (i, self.filter["b1"](i), i, self.filter["b2"](i), i, self.filter["b3"](i), i, self.filter["b4"](i)))
        # exit(0)

    def getOutput(self):
        """
        Returns accumulated output values
        @return list of float/int accumulated output values, filtered through forward-backward filtering
        """
        tempfrequencylist = [[0 for i in range(5)] for j in range(self.N / 2 + 1)]
        data = self.output[:]
        data.reverse()
        output = []
        for amplitude in data:
            output.append(self._filterHelper4(amplitude, tempfrequencylist))
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
        for amplitude in data:
            output.append(self._filterHelper4(amplitude, self.frequencylist))
        self.output += output
        return output

    def _filterHelper(self, stacklist, m=0):
        """
        Helper for the butterworth filter
        @params stacklist list of Stacks containing necessary variables
        @params m int counter
        @return output of filter for the specific input
        """
        # setup
        k = m + 1
        xn = []
        for i in range(5):
            if stacklist[m].empty():
                xn.append(0)
            else:
                xn.append(stacklist[m].get_nowait())
        yn = []
        for i in range(5):
            if stacklist[k].empty():
                yn.append(0)
            else:
                yn.append(stacklist[k].get_nowait())
        # calculation
        newyn = self.filter["A"](k) * (
            xn[0] +
            self.filter["a1"](k) * xn[1] +
            self.filter["a2"](k) * xn[2] +
            self.filter["a3"](k) * xn[3] +
            self.filter["a4"](k) * xn[4]
        ) - (
            self.filter["b1"](k) * yn[0] +
            self.filter["b2"](k) * yn[1] +
            self.filter["b3"](k) * yn[2] +
            self.filter["b4"](k) * yn[3]
        )
        # setup for next iteration
        for i in range(3, -1, -1):
            stacklist[m].put_nowait(xn[i])
        for i in range(2, -1, -1):
            stacklist[k].put_nowait(yn[i])
        stacklist[k].put_nowait(newyn)
        # print m, newyn
        # base case
        if k >= self.N / 2:
            # return if k==self.N/2
            # raw_input()
            return newyn
        # recurse if not at end
        return self._filterHelper(stacklist, m=m + 1)

    def _filterHelper2(self, x, w, m=0):
        """
        Helper2 for the butterworth filter
        @params x amplitude
        @params w list to store calculated frequencies
        @params m int counter
        @return output of filter for the specific input
        """
        k = m + 1
        # for i in range(5):
        #     print("w[%d]=%f" % (i, w[i]))
        w[4] = self.filter["A"](k) * x - (
            self.filter["b1"](k) * w[3] +
            self.filter["b2"](k) * w[2] +
            self.filter["b3"](k) * w[1] +
            self.filter["b4"](k) * w[0]
        )
        y = w[4] + (
            self.filter["a1"](k) * w[3] +
            self.filter["a2"](k) * w[2] +
            self.filter["a3"](k) * w[1] +
            self.filter["a4"](k) * w[0]
        )
        for i in range(4):
            w[i] = w[i+1]

        if k >= self.N/2:
            # return if k==self.N
            # print y
            # raw_input()
            return y
        # recurse if not at end
        return self._filterHelper2(y, w, m=m + 1)

    def _filterHelper3(self, x, w, m=0):
        """
        Helper 3 for the butterworth filter
        @params x amplitude
        @params w list to store calculated frequencies
        @params m counter
        @return output of filter for the specific input
        """
        k = m + 1
        # for i in range(5):
        #     print("w[%d]=%f" % (i, w[i]))
        w[4] = self.filter["A"](k) * x - (
            self.filter["b1"](k) * w[3] +
            self.filter["b2"](k) * w[2] +
            self.filter["b3"](k) * w[1] +
            self.filter["b4"](k) * w[0]
        )
        y = w[4] + (
            self.filter["a1"](k) * w[3] +
            self.filter["a2"](k) * w[2] +
            self.filter["a3"](k) * w[1] +
            self.filter["a4"](k) * w[0]
        )
        for i in range(4):
            w[i] = w[i+1]

        return y

    def _filterHelper4(self, x, w, m=0):
        """
        Helper 4 for the butterworth filter
        @params x amplitude
        @params w list to store calculated frequencies
        @params m counter
        @return output of filter for the specific input
        """
        k = m + 1

        previousx = w[m]
        previousy = w[k]

        previousx[4] = x

        ym = self.filter["A"](k) * (
            x +
            self.filter["a1"](k) * previousx[3] +
            self.filter["a2"](k) * previousx[2] +
            self.filter["a3"](k) * previousx[1] +
            self.filter["a4"](k) * previousx[0]
        ) - (
            self.filter["b1"](k) * previousy[3] +
            self.filter["b2"](k) * previousy[2] +
            self.filter["b3"](k) * previousy[1] +
            self.filter["b4"](k) * previousy[0]
        )

        previousy[4] = ym

        for i in range(len(previousx) - 1):
            previousx[i] = previousx[i+1]

        if k < self.N / 2:
            return self._filterHelper4(ym, w, m=m+1)
        else:
            for i in range(len(previousy) - 1):
                previousy[i] = previousy[i+1]
            return ym

    def getTransform(self, btype):
        """
        @param btype string type of filter
            lowpass
            highpass
            bandpass
            notch
            bandstop
        return lambda z analog filter function
        """
        if btype not in ["lowpass", "highpass", "bandpass", "notch"]:
            raise ValueError("ButterBase.getFilter: invalid btype %s" % btype)
        var = {
            "lowpass": _lowpassFilterVariables,
            "highpass": _highpassFilterVariables,
            "bandpass": _bandpassFilterVariables,
            "notch": _notchFilterVariables,
            "bandstop": _bandstopFilterVariables
        }[btype]()

        def transform(z):
            """
            This will be the filter function to return
            """
            factors = map(
                lambda k: var["A"](k) * (1 + var["a1"](k) * (z**(-1)) + var["a2"](k) * (z**(-2)) + var["a3"](k) * (z**(-3)) + var["a4"](k) * (z**(-4))) / (1 + var["b1"](k) * (z**(-1)) + var["b2"](k) * (z**(-2)) + var["b3"](k) * (z**(-3)) + var["b4"](k) * (z**(-4))), [i for i in range(1, self.N / 2 + 1)])
            return reduce(lambda x, y: x * y, factors)
        return transform

    def _basicFilterVariables(self):
        """
        returns basic filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = {}
        basic["a"] = lambda k: self.wc * \
            math.sin((float(2.0 * k - 1) / (2.0 * self.N)) * math.pi)
        basic["B"] = lambda k: 1 + basic["a"](k) + ((self.wc**2) / 4.0)
        basic["A"] = lambda k: (self.wc**2) / (4.0 * basic["B"](k))
        basic["a1"] = lambda k: 2
        basic["a2"] = lambda k: 1
        basic["a3"] = lambda k: 0
        basic["a4"] = lambda k: 0
        basic["b1"] = lambda k: 2 * ((self.wc**2 / (4.0)) - 1) / (basic["B"](k))
        basic["b2"] = lambda k: (
            1 - basic["a"](k) + (self.wc**2 / (4.0))) / (basic["B"](k))
        basic["b3"] = lambda k: 0
        basic["b4"] = lambda k: 0
        return basic

    def _lowpassFilterVariables(self):
        """
        returns lowpass filter variables
        @return dictionary key:string variable value: lambda k
        """
        basic = self._basicFilterVariables()
        # for i in range(1,9,1):
        #     print("A%d: %.4f\tb1%d: %.4f\tb2%d: %.4f" % (i, basic["A"](i), i, basic["b1"](i), i, basic["b2"](i)))

        Op = 2 * (math.pi * self.fc / self.fs)
        vp = 2 * math.atan(self.wc / 2.0)

        alpha = math.sin((vp - Op) / 2.0) / \
            math.sin((vp + Op) / 2.0)
        # print math.sin((vp - Op) / 2.0), math.sin((vp + Op) / 2.0)
        #
        # print "Op=%f\tvp=%f" % (Op, vp)
        # print "alpha=%f" % alpha

        def C(k): return 1 - basic["b1"](k) * \
            alpha + basic["b2"](k) * (alpha**2)
        lowpass = {}
        lowpass["A"] = lambda k: ((1 - alpha)**2) * basic["A"](k) / C(k)
        lowpass["B"] = basic["B"]
        lowpass["a1"] = basic["a1"]
        lowpass["a2"] = basic["a2"]
        lowpass["a3"] = basic["a3"]
        lowpass["a4"] = basic["a4"]
        lowpass["b1"] = lambda k: (
            (1 + alpha**2) * basic["b1"](k) - 2 * alpha * (1 + basic["b2"](k))) / C(k)
        lowpass["b2"] = lambda k: (
            alpha**2 - basic["b1"](k) * alpha + basic["b2"](k)) / C(k)
        lowpass["b3"] = basic["b3"]
        lowpass["b4"] = basic["b4"]
        # print "Op: %.3f" % Op
        # print "vp: %.3f" % vp
        # print "alpha: %.4f" % alpha(1)
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

        def C(k): return 1 - basic["b1"](k) * \
            alpha + basic["b2"](k) * (alpha**2)
        highpass = {}
        highpass["A"] = lambda k: ((1 - alpha)**2) * basic["A"](k) / C(k)
        highpass["B"] = basic["B"]
        highpass["a1"] = lambda k: -basic["a1"](k)
        highpass["a2"] = basic["a2"]
        highpass["a3"] = basic["a3"]
        highpass["a4"] = basic["a4"]
        highpass["b1"] = lambda k: (
            -(1.0 + alpha**2) * basic["b1"](k) + 2 * alpha * (1 + basic["b2"](k))) / C(k)
        highpass["b2"] = lambda k: (
            float(alpha**2) - basic["b1"](k) * alpha + basic["b2"](k)) / C(k)
        highpass["b3"] = basic["b3"]
        highpass["b4"] = basic["b4"]
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
        # print(Op1, Op2, self.wc, alpha, k, A, B)
        # raw_input()
        # a = math.sin((vp - Op2) / 2.0) / \
        #     math.sin((vp + Op2) / 2.0)
        # b = -(math.cos((vp + Op1) / (2.0))) / \
        #     (math.cos((vp - Op1) / c(2.0)))
        # A = a - b
        # B = -a * b


        def C(k): return 1 - basic["b1"](k) * B + basic["b2"](k) * (B**2)
        bandpass = {}
        bandpass["A"] = lambda k: basic["A"](k) * ((1 - B)**2) / C(k)
        bandpass["B"] = basic["B"]
        bandpass["a1"] = lambda k: 0#-basic["a1"](k)
        bandpass["a2"] = lambda k: -basic["a1"](k)
        bandpass["a3"] = lambda k: 0#basic["a3"](k)
        bandpass["a4"] = lambda k: basic["a2"](k)#basic["a4"](k)
        bandpass["b1"] = lambda k: (A / C(k)) * (B * (basic["b1"](k) - 2 * basic["b2"](k)) + (basic["b1"](k) - 2))
        bandpass["b2"] = lambda k: (1 / C(k)) * ((A**2) * (1 - basic["b1"](k) + basic["b2"](k)) + 2 * B * (1 + basic["b2"](k)) - basic["b1"](k) * (B**2) - basic["b1"](k))
        bandpass["b3"] = lambda k: (A / C(k)) * (B * (basic["b1"](k) - 2) + (basic["b1"](k) - 2 * basic["b2"](k)))
        bandpass["b4"] = lambda k: (1 / C(k)) * ((B**2) - basic["b1"](k) * B + basic["b2"](k))
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

        def C(k): return 1 + basic["b1"](k) * \
            B + basic["b2"](k) * (B**2)
        notch = {}
        notch["A"] = lambda k: basic["A"](k) * ((1 + B)**2) / C(k)
        notch["B"] = basic["B"]
        notch["a1"] = lambda k: -4.0 * A / (B + 1)
        notch["a2"] = lambda k: 2.0 * ((2 * (A**2))/((B + 1)**2) + 1)
        notch["a3"] = lambda k: -4.0 * A / (B + 1)
        notch["a4"] = lambda k: 1
        notch["b1"] = lambda k: -(A / C(k)) * \
            (B * (basic["b1"](k) + 2 * basic["b2"](k)) +
             (2 + basic["b1"](k)))
        notch["b2"] = lambda k: (1 / C(k)) * \
            ((A**2) * (1 + basic["b1"](k) + basic["b2"](k)) +
             2 * B * (1 + basic["b2"](k)) +
             basic["b1"](k) * (B**2) +
             basic["b1"](k))
        notch["b3"] = lambda k: -(A / C(k)) * \
            (B * (basic["b1"](k) + 2) +
             (basic["b1"](k) + 2 * basic["b2"](k)))
        notch["b4"] = lambda k: (1 / C(k)) * \
            ((B**2) +
             basic["b1"](k) * B +
             basic["b2"](k))
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

        def C(k): return 1 + basic["b1"](k) * \
            B + basic["b2"](k) * (B**2)
        bandstop = {}
        bandstop["A"] = lambda k: basic["A"](k) * ((1 + B)**2) / C(k)
        bandstop["B"] = basic["B"]
        bandstop["a1"] = lambda k: -4.0 * A / (B + 1)
        bandstop["a2"] = lambda k: 2.0 * ((2 * (A**2))/((B + 1)**2) + 1)
        bandstop["a3"] = lambda k: -4.0 * A / (B + 1)
        bandstop["a4"] = lambda k: 1
        bandstop["b1"] = lambda k: -(A / C(k)) * \
            (B * (basic["b1"](k) + 2 * basic["b2"](k)) +
             (2 + basic["b1"](k)))
        bandstop["b2"] = lambda k: (1 / C(k)) * \
            ((A**2) * (1 + basic["b1"](k) + basic["b2"](k)) +
             2 * B * (1 + basic["b2"](k)) +
             basic["b1"](k) * (B**2) +
             basic["b1"](k))
        bandstop["b3"] = lambda k: -(A / C(k)) * \
            (B * (basic["b1"](k) + 2) +
             (basic["b1"](k) + 2 * basic["b2"](k)))
        bandstop["b4"] = lambda k: (1 / C(k)) * \
            ((B**2) +
             basic["b1"](k) * B +
             basic["b2"](k))
        return bandstop
