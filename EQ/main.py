"""
Kei Imada
User Interface for EQ App
"""


from Tkinter import Tk, StringVar, Scale, VERTICAL
from ttk import Frame, Label, Entry, Button, OptionMenu

class KEQ(object):

    def __init__(self, master):
        self.master = master
        self.initUI()


    def initUI(self):
        self.master.title("KEQ")
        fileio  = Frame(self.master)
        control = Frame(self.master)
        record  = Frame(self.master)
        dfilter = Frame(self.master)
        rolloff = Frame(self.master)
        cutoff  = Frame(self.master)
        lcutoff = Frame(self.master)
        hcutoff = Frame(self.master)

        fileio.grid(row=0,column=0, columnspan=2)
        control.grid(row=0,column=2, columnspan=2)
        record.grid(row=1,column=0, columnspan=2)
        dfilter.grid(row=1,column=2, columnspan=2)
        rolloff.grid(row=2,column=0)
        cutoff.grid(row=2,column=1)
        lcutoff.grid(row=2,column=2)
        hcutoff.grid(row=2,column=3)

        #fileio
        openButton = Button(fileio, text="Open")
        filepathEntry = Entry(fileio)
        clearButton = Button(fileio, text="Clear")
        openButton.grid(row=0,column=0)
        filepathEntry.grid(row=0,column=1, columnspan=2)
        clearButton.grid(row=0,column=3)

        #control
        playButton = Button(control, text="Play")
        stopButton = Button(control, text="Stop")
        playButton.grid(row=0, column=0)
        stopButton.grid(row=0, column=1)

        #record
        rl1 = Label(record, text="OR ")
        recordButton = Button(record, text="record")
        rl2 = Label(record, text=" with sampling ")
        samplingEntry = Entry(record)
        rl3 = Label(record, text=" Hz")
        rl1.grid(row=0, column=0)
        recordButton.grid(row=0, column=1)
        rl2.grid(row=0, column=2)
        samplingEntry.grid(row=0, column=3)
        rl3.grid(row=0, column=4)

        #dfilter
        filterOptions = ["Filter type", "Lowpass", "Highpass", "Bandpass", "Bandstop", "Notch"]
        var = StringVar(dfilter)
        var.set(filterOptions[0])

        dropdown = apply(OptionMenu, (dfilter, var) + tuple(filterOptions))
        dropdown.pack()

        #rolloff
        self.initSlider(rolloff,"rolloff",0,100)

        #cutoff
        self.initSlider(cutoff,"cutoff",0,100)

        #lcutoff
        self.initSlider(lcutoff,"lcutoff",0,100)

        #hcutoff
        self.initSlider(hcutoff,"hcutoff",0,100)

    def initSlider(self, master, text, mini, maxi):
        slider = Scale(master, from_=maxi, to=mini, orient=VERTICAL)
        slider.configure(command=lambda val: self.logScale(slider, val))
        entry = Entry(master)
        label = Label(master, text=text)
        slider.grid(row=0, column=0)
        entry.grid(row=1, column=0)
        label.grid(row=2, column=0)

    def logScale(self, scale, val):
        scale.configure(label=str(10**(int(val))))
        print scale.number


def main():

    root = Tk()
    # root.geometry("250x150+300+300")
    app = KEQ(master=root)
    root.mainloop()


if __name__ == '__main__':
    main()
