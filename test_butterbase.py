"""
Kei Imada
20170608
Test file for filters/butterbase.py
"""

from filters.butterbase2 import *
import matplotlib.pyplot as plt
from numpy import fft
import cmath
import math

def main():
    T = "bandpass"
    inf = open("test/data01r.txt", "r")
    L = map(lambda k: float(k), inf.readlines())
    pre = map(lambda k: math.sqrt(k.real**2 + k.imag**2), fft.rfft(L))
    b = Butter(cutoff=180, cutoff1=200, cutoff2=600, rolloff=48, sampling=3109, btype="%s" % T)
    filtered = b.send(L)
    # filtered = b.getOutput()
    post = map(lambda k: math.sqrt(k.real**2 + k.imag**2), fft.rfft(filtered))
    out = open("test/data01r_%s_fft.txt" % T, "w")
    out.seek(0)
    out.truncate()
    out.writelines(map(lambda k: "%f\t%f\n" % (k[0], k[1]), zip(pre, post)))
    out.close()

    out = open("test/data01r_%s.txt" % T, "w")
    out.seek(0)
    out.truncate()
    out.writelines(map(lambda k: "%f\n" % (k), filtered))
    out.close()



main()
