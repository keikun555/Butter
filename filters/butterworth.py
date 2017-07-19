"""
Kei Imada
Started 20170531
Attempt at package building and the butterworth filter
"""
import sys as system
from numpy import *
from math import *
from cmath import *
from butterbase import *


def filter(data=[], sampling=1.0, type="lowpass", cutoff=None, rolloff=None, center=[]):
    """
    Based on type, does one of the following types of filters mutably on data:
        lowpass
        highpass
        bandpass
        notch
        bandstop
    @param data     - list of floats, samples
    @param sampling - float, sampling frequency in seconds
    @param type     - string, lowpass, highpass, or notch
    @param cutoff   - float, cutoff frequency used in lowpass/highpass filters
    @param rolloff  - float, rolloff frequency used in lowpass/highpass filters
    @param center   - list of floats, center frequencies used in notch filters
    """
    f = {
    "lowpass": lowpass,
    "highpass": highpass,
    "bandpass": bandpass,
    "notch": notch
    }.get(type, None)
    if f == None:
        # wrong type
        raise TypeError(
"""
\"%s\" is not supported in this package
supported filter types:
    \"lowpass\"
    \"highpass\"
    \"bandpass\"
    \"notch\"
    \"bandstop\"""" % type
        )
    if type == "lowpass" or type == "highpass" or type == "bandpass":
        # lowpass/highpass filter
        f(data, sampling, cutoff, rolloff)
    else:
        # notch filter
        f(data, sampling, center)
