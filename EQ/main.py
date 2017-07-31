"""
Kei Imada
User Interface for EQ App
"""


from Tkinter import Tk, StringVar, Scale, VERTICAL, END, CENTER, DISABLED, NORMAL
from ttk import Frame, Label, Entry, Button, OptionMenu, Style
import tkFileDialog as filedialog
import tkMessageBox
import numpy as np
import os

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
        control.grid(row=1,column=0, columnspan=2)
        record.grid(row=0,column=2, columnspan=2)
        dfilter.grid(row=1,column=2, columnspan=2)
        rolloff.grid(row=2,column=0)
        cutoff.grid(row=2,column=1)
        lcutoff.grid(row=2,column=2)
        hcutoff.grid(row=2,column=3)

        #fileio
        fileVar = StringVar(fileio)
        fileVar.set("")
        openButton = Button(fileio, text="Open")
        filepathEntry = Entry(fileio, textvariable=fileVar)
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
        rl1 = Label(record, text=" OR ")
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
        dvar = StringVar(dfilter)
        dvar.set(filterOptions[0])

        dropdown = apply(OptionMenu, (dfilter, dvar) + tuple(filterOptions))
        filterButton = Button(dfilter, text="Filter")
        dropdown.grid(row=0, column=1)
        filterButton.grid(row=0, column=0)

        #used in initializing the slider frames
        def initSlider(master, text, mini, maxi, log=False):
            if log:
                mini = np.log10(mini)
                maxi = np.log10(maxi)
            slider = Scale(master, from_=maxi, to=mini, orient=VERTICAL, showvalue=False, resolution=.000000000000001, length=200)
            # slider.configure(command=lambda val: logScale(slider, val))
            slider.set(mini)
            entry = Entry(master, width = 8, justify=CENTER)
            label = Label(master, text=text)
            slider.grid(row=1, column=0)
            entry.grid(row=2, column=0)
            label.grid(row=0, column=0)
            def updateEntry(ent, val):
                ent.delete(0, END)
                ent.insert(0, val)
            def sliderInit(slider, entry, val):
                if log:
                    val = "%.2f" % 10**(float(val))
                else:
                    val = "%.2f" % float(val)
                updateEntry(entry, val)

            slider.configure(command=lambda val: sliderInit(slider, entry, val))

            def updateSlider(slider, val):
                val = float(val)
                if val < mini:
                    slider.set(mini)
                elif val > maxi:
                    slider.set(maxi)
                else:
                    slider.set(val)
            def entryInit(slider, entry, val):
                try:
                    val = float(val)
                    if log:
                        val = np.log10(val)
                    updateSlider(slider, val)
                    return True
                except:
                    return False
            # entrySV = StringVar()
            # entrySV.trace("w", lambda name, index, mode, sv=entrySV: entryInit(sv.get()))
            entry.configure(validate="focusout",
            validatecommand=lambda: entryInit(slider, entry, entry.get()))
            # entry.configure(textvariable=entrySV)

            master.entry = entry
            master.label = label
            master.scale = slider

        #rolloff
        initSlider(rolloff,"rolloff",0,100)

        #cutoff
        initSlider(cutoff,"cutoff",20,20000, log=True)

        #lcutoff
        initSlider(lcutoff,"lcutoff",20,20000, log=True)

        #hcutoff
        initSlider(hcutoff,"hcutoff",20,20000, log=True)

        sliderFrames = [rolloff, cutoff, lcutoff, hcutoff]

        for frame in sliderFrames:
            frame.scale.configure(state=DISABLED)
            frame.entry.configure(state=DISABLED)

        #link filter type to sliders
        def onFilterSelection(*args):
            chosen = dvar.get()
            cutoff1 = ["Lowpass", "Highpass", "Notch"]
            cutoff2 = ["Bandstop", "Bandpass"]
            if chosen in cutoff1:
                rolloff.scale.configure(state=NORMAL)
                rolloff.entry.configure(state=NORMAL)
                cutoff.scale.configure(state=NORMAL)
                cutoff.entry.configure(state=NORMAL)
                lcutoff.scale.configure(state=DISABLED)
                lcutoff.entry.configure(state=DISABLED)
                hcutoff.scale.configure(state=DISABLED)
                hcutoff.entry.configure(state=DISABLED)
            elif chosen in cutoff2:
                rolloff.scale.configure(state=NORMAL)
                rolloff.entry.configure(state=NORMAL)
                cutoff.scale.configure(state=DISABLED)
                cutoff.entry.configure(state=DISABLED)
                lcutoff.scale.configure(state=NORMAL)
                lcutoff.entry.configure(state=NORMAL)
                hcutoff.scale.configure(state=NORMAL)
                hcutoff.entry.configure(state=NORMAL)
            else:
                for frame in sliderFrames:
                    frame.scale.configure(state=DISABLED)
                    frame.entry.configure(state=DISABLED)
        dvar.trace("w", onFilterSelection)

        #link open file/clear file button to entry and put validation in entry
        def openButtonClicked(*args):
            filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("audio files","*.wav"),("all files","*.*")))
            filepathEntry.delete(0, END)
            filepathEntry.insert(0, filename)
        openButton.configure(command=openButtonClicked)
        def onFilePathChanged(*args):
            try:
                open(fileVar.get())
                return True
            except:
                return False
        filepathEntry.configure(validate="focusout", validatecommand=onFilePathChanged)
        def onClearButtonClicked(*args):
            fileVar.set("")
        clearButton.configure(command=onClearButtonClicked)




def main():
    root = Tk()
    root.style = Style()
    root.style.theme_use("clam")
    # root.geometry("250x150+300+300")
    app = KEQ(master=root)
    root.mainloop()


if __name__ == '__main__':
    main()
