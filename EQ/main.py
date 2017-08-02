"""
Kei Imada
User Interface for EQ App
"""


from Tkinter import Tk, StringVar, IntVar, Scale, VERTICAL, END, CENTER, DISABLED, NORMAL
from ttk import Frame, Label, Entry, Button, OptionMenu, Style, Checkbutton
import tkFileDialog as filedialog
import tkMessageBox
import numpy as np
import os
from Filter import *


class KEQ(object):

    def __init__(self, master):
        self.master = master
        self.filter = EQFilter()
        self.initUI()
        atexit.register()

    def initUI(self):
        self.master.title("KEQ")
        fileio = Frame(self.master)
        control = Frame(self.master)
        record = Frame(self.master)
        dfilter = Frame(self.master)
        rolloff = Frame(self.master)
        cutoff = Frame(self.master)
        lcutoff = Frame(self.master)
        hcutoff = Frame(self.master)

        fileio.grid(row=0, column=0, columnspan=2)
        control.grid(row=1, column=0, columnspan=2)
        record.grid(row=0, column=2, columnspan=2)
        dfilter.grid(row=1, column=2, columnspan=2)
        rolloff.grid(row=2, column=0)
        cutoff.grid(row=2, column=1)
        lcutoff.grid(row=2, column=2)
        hcutoff.grid(row=2, column=3)

        # fileio
        fileio.fileVar = StringVar(fileio)
        fileio.fileVar.set("")
        fileio.openButton = Button(fileio, text="Open")
        fileio.filepathEntry = Entry(fileio, textvariable=fileio.fileVar)
        fileio.clearButton = Button(fileio, text="Clear")
        fileio.openButton.grid(row=0, column=0)
        fileio.filepathEntry.grid(row=0, column=1, columnspan=2)
        fileio.clearButton.grid(row=0, column=3)

        # record
        record.rl1 = Label(record, text=" OR ")
        record.recordButton = Button(record, text="record")
        record.rl2 = Label(record, text=" with sampling ")
        record.samplingEntry = Entry(record)
        record.rl3 = Label(record, text=" Hz")
        record.rl1.grid(row=0, column=0)
        record.recordButton.grid(row=0, column=1)
        record.rl2.grid(row=0, column=2)
        record.samplingEntry.grid(row=0, column=3)
        record.rl3.grid(row=0, column=4)

        # control
        control.playButton = Button(control, text="Play")
        control.stopButton = Button(control, text="Stop")
        control.playButton.grid(row=0, column=0)
        control.stopButton.grid(row=0, column=1)

        # dfilter
        dfilter.filterOptions = ["Filter type", "None", "Lowpass",
                                 "Highpass", "Bandpass", "Bandstop", "Notch"]
        dfilter.dvar = StringVar(dfilter)
        dfilter.dvar.set(dfilter.filterOptions[0])

        dfilter.dropdown = apply(
            OptionMenu, (dfilter, dfilter.dvar) + tuple(dfilter.filterOptions))
        dfilter.filterCheck = IntVar()
        dfilter.filterButton = Checkbutton(
            dfilter, text="Filter", variable=dfilter.filterCheck)
        dfilter.dropdown.grid(row=0, column=0)
        dfilter.filterButton.grid(row=0, column=2)

        # used in initializing the slider frames
        def initSlider(master, text, mini, maxi, log=False):
            if log:
                mini = np.log10(mini)
                maxi = np.log10(maxi)
            slider = Scale(master, from_=maxi, to=mini, orient=VERTICAL,
                           showvalue=False, resolution=.000000000000001, length=200)
            # slider.configure(command=lambda val: logScale(slider, val))
            master.mini = mini
            master.maxi = maxi
            slider.set(mini)
            master.value = mini
            entry = Entry(master, width=8, justify=CENTER)
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
                master.value = val

            slider.configure(
                command=lambda val: sliderInit(slider, entry, val))

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
                    master.value = val
                    return True
                except:
                    return False
            # entrySV = StringVar()
            # entrySV.trace("w", lambda name, index, mode, sv=entrySV: entryInit(sv.get()))
            entry.configure(validate="focusout",
                            validatecommand=lambda: entryInit(slider, entry, entry.get()))
            # entry.configure(textvariable=entrySV)

            def update_value(value):
                master.value = value
                sliderInit(slider, entry, value)

            master.entry = entry
            master.label = label
            master.scale = slider
            master.update_value = update_value

        # rolloff
        initSlider(rolloff, "rolloff", 0, 100)

        # cutoff
        initSlider(cutoff, "cutoff", 20, 20000, log=True)

        # lcutoff
        initSlider(lcutoff, "lcutoff", 20, 20000, log=True)

        # hcutoff
        initSlider(hcutoff, "hcutoff", 20, 20000, log=True)

        sliderFrames = [rolloff, cutoff, lcutoff, hcutoff]

        for frame in sliderFrames:
            frame.scale.configure(state=DISABLED)
            frame.entry.configure(state=DISABLED)

        # link filter type to sliders
        def onFilterSelection(*args):
            chosen = dfilter.dvar.get()
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
                rolloff.update_value(rolloff.mini)
                cutoff.update_value(cutoff.mini)
            elif chosen in cutoff2:
                rolloff.scale.configure(state=NORMAL)
                rolloff.entry.configure(state=NORMAL)
                cutoff.scale.configure(state=DISABLED)
                cutoff.entry.configure(state=DISABLED)
                lcutoff.scale.configure(state=NORMAL)
                lcutoff.entry.configure(state=NORMAL)
                hcutoff.scale.configure(state=NORMAL)
                hcutoff.entry.configure(state=NORMAL)
                rolloff.update_value(rolloff.mini)
                lcutoff.update_value(cutoff.mini)
                hcutoff.update_value(cutoff.mini)
            else:
                for frame in sliderFrames:
                    frame.scale.configure(state=DISABLED)
                    frame.entry.configure(state=DISABLED)
        dfilter.dvar.trace("w", onFilterSelection)

        # link open file/clear file button to entry and put validation in entry
        def openButtonClicked(*args):
            fileio.filename = filedialog.askopenfilename(
                initialdir="/", title="Select file", filetypes=(("audio files", "*.wav"), ("all files", "*.*")))
            fileio.filepathEntry.delete(0, END)
            fileio.filepathEntry.insert(0, filename)
        fileio.openButton.configure(command=openButtonClicked)

        def onFilePathChanged(*args):
            try:
                open(fileio.fileVar.get())
                return True
            except:
                return False
        fileio.filepathEntry.configure(validate="focusout",
                                       validatecommand=onFilePathChanged)

        def onClearButtonClicked(*args):
            fileio.fileVar.set("")
        fileio.clearButton.configure(command=onClearButtonClicked)

        # filter button
        def onFilterButtonChecked(*args):
            self.filter.update_filter_check(dfilter.filterCheck.get() == 1)
        dfilter.filterButton.configure(command=onFilterButtonChecked)


def main():
    root = Tk()
    root.style = Style()
    root.style.theme_use("clam")
    # root.geometry("250x150+300+300")
    app = KEQ(master=root)
    root.mainloop()


if __name__ == '__main__':
    main()
