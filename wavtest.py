"""
Kei Imada
20170725
Testing the WAVfilter package
"""


import WAVfilter as wav

def main():
    inf = wav.open("test3.wav")
    inf.set_filter(btype="lowpass", cutoff=4000, cutoff1=85, cutoff2=180, rolloff=48)
    inf.write("test3_filtered.wav")

main()
