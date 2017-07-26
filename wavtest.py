"""
Kei Imada
20170725
Testing the WAVfilter package
"""


import WAVfilter as wav

def main():
    inf = wav.open("test2.wav")
    inf.set_filter(btype="lowpass", cutoff=300, cutoff1=None, cutoff2=None, rolloff=48)
    inf.write("test2_filtered.wav")

main()
