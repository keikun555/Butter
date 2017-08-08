"""
Kei Imada
User Interface for EQ App
"""


from Tkinter import Tk, StringVar, IntVar, DoubleVar, Scale, VERTICAL, END, CENTER, DISABLED, NORMAL
from ttk import Frame, Label, Entry, Button, OptionMenu, Style, Checkbutton
import tkFileDialog as filedialog
import tkMessageBox
import numpy as np
import os
from Filter import *


class KEQ(object):

    def __init__(self, master):
        """The constructor for the KEQ app
        @params master the root parent for the KEQ app
        """
        self.master = master
        self.filter = EQFilter()
        self.initUI()

    def destructor(self):
        """Destructor for the KEQ app, closes open streams"""
        self.filter.reset()
        self.master.destroy()

    def initUI(self):
        """Initializes everything needed for the KEQ app"""

        self.master.title("KEQ")

        # Initialize frames
        fileio = Frame(self.master)
        control = Frame(self.master)
        record = Frame(self.master)
        dfilter = Frame(self.master)
        rolloff = Frame(self.master)
        cutoff = Frame(self.master)
        lcutoff = Frame(self.master)
        hcutoff = Frame(self.master)

        # Position frames
        fileio.grid(row=0, column=0, columnspan=2)
        control.grid(row=1, column=0, columnspan=2)
        record.grid(row=0, column=2, columnspan=2)
        dfilter.grid(row=1, column=2, columnspan=2)
        rolloff.grid(row=2, column=0)
        cutoff.grid(row=2, column=1)
        lcutoff.grid(row=2, column=2)
        hcutoff.grid(row=2, column=3)

        # Initialize fileio
        fileio.fileVar = StringVar(fileio)
        fileio.fileVar.set("")
        fileio.openButton = Button(fileio, text="Open")
        fileio.filepathEntry = Entry(fileio, textvariable=fileio.fileVar)
        fileio.clearButton = Button(fileio, text="Clear")
        fileio.openButton.grid(row=0, column=0)
        fileio.filepathEntry.grid(row=0, column=1, columnspan=2)
        fileio.clearButton.grid(row=0, column=3)

        # Initialize record
        self.recording = False
        record.rl1 = Label(record, text=" OR ")
        record.recordButton = Button(
            record, text="record")
        record.rl2 = Label(record, text=" with sampling freq ")
        record.samplingEntry = Entry(record)
        record.rl3 = Label(record, text=" Hz")
        record.rl1.grid(row=0, column=0)
        record.recordButton.grid(row=0, column=1)
        record.rl2.grid(row=0, column=2)
        record.samplingEntry.grid(row=0, column=3)
        record.rl3.grid(row=0, column=4)

        # Initialize control
        control.playButton = Button(
            control, text="Play", command=lambda *args: self.filter.play(True))
        control.stopButton = Button(
            control, text="Pause", command=lambda *args: self.filter.play(False))
        control.playButton.grid(row=0, column=0)
        control.stopButton.grid(row=0, column=1)

        # Initialize dfilter
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


        def initSlider(master, text, mini, maxi, log=False):
            """Used in initializing the slider frames"""
            master.value = DoubleVar()
            master.value.set(mini)
            if log:
                slider_mini = np.log10(mini)
                slider_maxi = np.log10(maxi)
            else:
                slider_mini = mini
                slider_maxi = maxi
            slider_value = DoubleVar()
            slider_value.set(slider_mini)
            master.mini = mini
            master.maxi = maxi
            master.slider_mini = slider_mini
            master.slider_maxi = slider_maxi
            slider = Scale(
                master, from_=slider_maxi, to=slider_mini, orient=VERTICAL,
                variable=slider_value, showvalue=False,
                resolution=.000000000000001, length=200)

            entry_value = StringVar()
            entry_value.set("%.2f" % mini)
            entry = Entry(master, width=8, justify=CENTER, textvariable=entry_value)
            label = Label(master, text=text)
            slider.grid(row=1, column=0)
            entry.grid(row=2, column=0)
            label.grid(row=0, column=0)

            def sliderTrace(*args):
                """Called when slider value changes"""
                val = slider_value.get()
                if log:
                    val = 10**val
                entry_value.set("%.2f" % val)
                master.value.set(val)
            slider_trace_var = slider_value.trace_variable("w", sliderTrace)

            def entryTrace(*args):
                """Called when entry value changes"""
                try:
                    val = float(entry_value.get())
                    master.value.set(val)
                    if log:
                        val = np.log10(val)
                    slider_value.set(val)
                except ValueError:
                    pass
            entry_trace_var = entry_value.trace_variable("w", entryTrace)

            def entryValidate(*args):
                """Called when validation is needed for entry values"""
                try:
                    float(entry_value.get())
                    return True
                except:
                    return False
            entry.configure(validate="key", validatecommand=entryValidate)

            def update_value(value):
                master.value.set(value)
                entry_value.set(str(value))
                if log:
                    value = np.log10(value)
                slider_value.set(value)

            master.entry = entry
            master.label = label
            master.scale = slider
            master.update_value = update_value

        # Initialize rolloff
        initSlider(rolloff, "rolloff", 1, 100)

        # Initialize cutoff
        initSlider(cutoff, "cutoff", 20, 20000, log=True)

        # Initialize lcutoff
        initSlider(lcutoff, "lcutoff", 20, 20000, log=True)

        # Initialize hcutoff
        initSlider(hcutoff, "hcutoff", 21, 20001, log=True)

        sliderFrames = [rolloff, cutoff, lcutoff, hcutoff]

        for frame in sliderFrames:
            frame.scale.configure(state=DISABLED)
            frame.entry.configure(state=DISABLED)



        # link open file/clear file button to entry and put validation in entry
        def openButtonClicked(*args):
            """Called when openButton is pressed"""
            fileio.filename = filedialog.askopenfilename(
                initialdir="~", title="Select file", filetypes=(("audio files", "*.wav"), ("all files", "*.*")))
            fileio.filepathEntry.delete(0, END)
            fileio.filepathEntry.insert(0, fileio.filename)
            try:
                self.filter.open(fileio.filename)
            except Exception as e:
                tkMessageBox.showerror("File Error", e)
        fileio.openButton.configure(command=openButtonClicked)

        def onFilePathChanged(*args):
            """Called when filepathEntry is changed"""
            try:
                self.filter.open(fileio.filename)
            except Exception as e:
                tkMessageBox.showerror("File Error", e)
        fileio.filepathEntry.configure(validate="focusout",
                                       validatecommand=onFilePathChanged)

        def onClearButtonClicked(*args):
            """Called when clearButton is pressed"""
            fileio.fileVar.set("")
            record.samplingEntry.configure(state=NORMAL)
            self.filter.reset()
        fileio.clearButton.configure(command=onClearButtonClicked)

        # defining callback for recordButton
        def onRecordButtonClicked(*args):
            """Called when recordButton is clicked"""
            self.recording = not self.recording
            if self.recording:
                record.recordButton.configure(text="stop")
                record.samplingEntry.configure(state=DISABLED)
            else:
                record.recordButton.configure(text="record")
                self.filter.record(self.recording)
                record.recordButton.configure(command=onRecordButtonClicked)

        # link filter type to sliders
        def onFilterSelection(*args):
            """Called when filterButton is pressed"""
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
                filter_rolloff = float(rolloff.entry.get())
                filter_cutoff = float(cutoff.entry.get())
                self.filter.reload_filter(
                btype=chosen.lower(), rolloff=filter_rolloff, cutoff=filter_cutoff)
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
                filter_rolloff = float(rolloff.entry.get())
                filter_lcutoff = float(lcutoff.entry.get())
                filter_hcutoff = float(hcutoff.entry.get())
                self.filter.reload_filter(
                btype=chosen.lower(), rolloff=filter_rolloff,
                cutoff1=filter_lcutoff, cutoff2=filter_hcutoff)
            else:
                for frame in sliderFrames:
                    frame.scale.configure(state=DISABLED)
                    frame.entry.configure(state=DISABLED)
                    self.filter.delete_filter()
                    dfilter.dvar.trace("w", onFilterSelection)

        # filter button
        def onFilterButtonChecked(*args):
            """Called when filterButton is changed"""
            filterFLAG = dfilter.filterCheck.get() == 1
            self.filter.filter_(filterFLAG)
        dfilter.filterButton.configure(command=onFilterButtonChecked)

        # linking slider modules to self.filter
        rolloff.value.trace(
            "w", lambda *args: self.filter.reload_filter(rolloff=rolloff.value.get()))
        cutoff.value.trace(
            "w", lambda *args: self.filter.reload_filter(cutoff=cutoff.value.get()))
        lcutoff.value.trace(
            "w", lambda *args: self.filter.reload_filter(cutoff1=lcutoff.value.get()))
        hcutoff.value.trace(
            "w", lambda *args: self.filter.reload_filter(cutoff2=hcutoff.value.get()))

        # disabling lcutoff >= hcutoff event
        def lcutoff_hcutoff_reaction(*args):
            if lcutoff.value.get() >= hcutoff.value.get():
                hcutoff.update_value(lcutoff.value.get() + 1)

        def hcutoff_lcutoff_reaction(*args):
            if lcutoff.value.get() >= hcutoff.value.get():
                lcutoff.update_value(hcutoff.value.get() - 1)

        hcutoff.value.trace("w", hcutoff_lcutoff_reaction)
        lcutoff.value.trace("w", lcutoff_hcutoff_reaction)


def main():
    root = Tk()
    root.style = Style()
    root.style.theme_use("clam")
    app = KEQ(master=root)
    root.protocol("WM_DELETE_WINDOW", app.destructor)
    root.mainloop()


if __name__ == '__main__':
    main()
