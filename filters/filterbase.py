"""
Kei Imada
20170602
Base filters for the filters package
"""
def notch(data, sampling, center, stopband=1.0):
    """
    Mutably performs a notch filter on data
    @param data     - list of floats, samples
    @param sampling - float, sampling frequency in seconds
    @param center   - list of floats, center frequencies used in notch filters
    @param stopband - float, stopband width in percentage
    """
    raise NotImplementedError("filters.filterbase.notch: not implemented")
