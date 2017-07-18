"""
Kei Imada
20170718
Testing the test data
"""

from butterbase import Butter
import numpy as np
from math import *


def main():
    btype = "lowpass"
    inp = "test/data01r.txt"
    oup = "test/result_%s.txt" % btype
    filt = Butter(btype=btype, cutoff=100, rolloff=10, sampling=3109)
    inf = open(inp, "r")
    data = []
    for line in inf:
        data.append(float(line.strip()))
    inf.close()
    filtered = filt.send(data)
    out = open(oup, "w")
    out.seek(0)
    out.truncate()
    out.write(btype + "\n")
    for point in filtered:
        out.write(str(point) + "\n")
    out.close()
    out = open("test/result_%s_fft.txt" % btype, "w")
    out.seek(0)
    out.truncate()
    ffto = np.fft.fft(data)
    fftf = np.fft.fft(filtered)
    freq = np.fft.fftfreq(len(ffto))
    for (original, filtered, f) in zip(ffto, fftf, freq):
        out.write("%s\t%s\t%s\n" % (str(f*33109), str(sqrt(original.real**2 + original.imag**2)), str(sqrt(filtered.real**2 + filtered.imag**2))))
    out.close()


main()
