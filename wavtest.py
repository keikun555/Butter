"""
Kei Imada
20170725
Testing the WAVfilter package
"""


import WAVfilter as wav

def main():
    inf = wav.open("test2.wav")
    inf.set_filter(btype="notch", cutoff=180, cutoff1=85, cutoff2=1000, rolloff=48)
    inf.write("test2_filtered.wav")

main()
