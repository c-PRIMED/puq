#!/usr/bin/env python

"""
Visualize and modify Parameters, PDFs and Response Functions

This file is part of PUQ
Copyright (c) 2013-2016 PUQ Authors
See LICENSE file for terms.
"""
from __future__ import absolute_import, division, print_function

import matplotlib
matplotlib.use('TkAgg', warn=False)
import scipy
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
try:
    from Tkinter import *
    from tkFont import Font
    import ttk
    import ScrolledText
    from urlparse import urlparse, urlunsplit
    import tkMessageBox as messagebox
    from tkFileDialog import asksaveasfilename
except ImportError:
    from tkinter import *
    from tkinter.font import Font
    from tkinter import ttk
    from tkinter.scrolledtext import ScrolledText
    from urllib.parse import urlparse, urlunsplit
    from tkinter import messagebox
    from tkinter.filedialog import asksaveasfilename

import sys, os, weakref, copy
import h5py
from puq import Parameter, PDF, ExperimentalPDF, options, pickle, unpickle, NetObj, SampledFunc
import math
import webbrowser, shutil, atexit, shelve
import logging
from logging import info, debug, exception, warning, critical
from optparse import OptionParser
from .cnote import CNote, sq_colors, sq_image
from .tooltip import ToolTip
from scipy.stats import gaussian_kde


class MyCombobox:
    def __init__(self, parent, txt, values, current, callback=None):
        self.var = StringVar()
        self.var.set(current)
        self.callback = callback
        self.cb = ttk.Combobox(parent, textvariable=self.var, values=values)
        self.cb.bind('<<ComboboxSelected>>', self.changed)
        self.cb.pack(side=TOP, padx=5, pady=5, anchor='w')

    def changed(self, event):
        #print "combobox changed to %s" % (self.var.get())
        if self.callback:
            self.callback(self.var.get())

    def state(self, st, path):
        self.cb.config(state=st)

class MyLabel:
    def __init__(self, parent, text, value, bg=''):
        self.frame = Frame(parent, background='black', bd=1)
        if bg:
            self.label = Label(self.frame, text=value, bg=bg)
        else:
            self.label = Label(self.frame, text=value)
        self.desc = Label(self.frame, text=text)
        self.desc.pack(side=LEFT, anchor='w')
        self.label.pack(side=LEFT, anchor='w')

    def update(self, val):
        self.label.config(text=val)

# radiobutton
class RB:
    RB_list= []
    def __init__(self, parent, values, val, callback=None):
        self.callback = callback
        RB.RB_list.append(weakref.proxy(self))
        self.var = StringVar()
        self.var.set(val)
        for txt in values:
            b = Radiobutton(parent, text=txt, variable=self.var, value=txt, command=self.changed)
            b.pack(side=TOP, padx=5, pady=5, anchor='w')

    def changed(self):
        #print "RB changed to %s" % (self.var.get())
        if self.callback:
            self.callback(self.var.get())
        else:
            MyApp.state_changed()

    def state(self, st):
        self.cb.config(state=st)

    @staticmethod
    def get(name):
        for n in RB.RB_list:
            if name == n.txt:
                return n.var.get()

class MyEntry:
    def __init__(self, parent, txt, var, val, callback=None):
        self.callback = callback
        self.var = var
        self.var.set(val)
        Label(parent, text=txt).pack(side=LEFT)
        self.entry = Entry(parent, textvariable=self.var, width=10)
        self.entry.bind('<Return>', self.changed)
        self.entry.pack(side=LEFT, padx=5, anchor='w')

    def changed(self, entry):
        #print "Entry changed to %s" % (self.var.get())
        if self.callback:
            self.callback(self.var.get())
        else:
            MyApp.state_changed()

    def state(self, st):
        self.cb.config(state=st)

    def update(self, val):
        self.var.set(val)

class MB:
    def __init__(self, parent, plotframe, dframe):
        menubar = Menu(parent)
        parent['menu'] = menubar

        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        #filemenu.add_command(label="Upload", command=ask_upload)
        #filemenu.add_separator()
        #filemenu.add_command(label="Preferences", command=preferences)
        #filemenu.add_separator()
        filemenu.add_command(label="Quit", command=root.quit)

        self.exportmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=self.exportmenu)
        if dframe == None:
            self.exportmenu.add_command(label="Copy PDF to Clipboard", state=DISABLED)
            self.exportmenu.add_command(label="Export PDF as JSON", state=DISABLED)
            self.exportmenu.add_command(label="Export PDF to CSV file", state=DISABLED)
        else:
            self.exportmenu.add_command(label="Copy PDF to Clipboard", command=dframe.copy_clip, state=NORMAL)
            self.exportmenu.add_command(label="Export PDF as JSON", command=lambda: dframe.export_pdf('json'), state=NORMAL)
            self.exportmenu.add_command(label="Export PDF to CSV file", command=lambda: dframe.export_pdf('csv'), state=NORMAL)
        self.exportplot = Menu(self.exportmenu, tearoff=0)
        self.exportmenu.add_cascade(label="Plot to", menu=self.exportplot)
        fig = plt.figure()
        sup = fig.canvas.get_supported_filetypes()
        keys = list(sup.keys())
        keys.sort()
        for key in keys:
            lab = '%s : %s' % (key.upper(), sup[key])
            self.exportplot.add_command(label=lab, command = lambda key=key: plotframe.plot(key))

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        helpmenu.add_command(label="Online Help", command=self.open_help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        parent.config(menu=menubar)

    def open_help(self):
        webbrowser.open('http://c-primed.github.io/puq/')

    def about(self):
        messagebox.showinfo(message=__doc__, title='ABOUT')

class ResponseFrame:
    def __init__(self, parent):
        self.tframe = Frame(parent)
        ResponseFrame.me = weakref.proxy(self)

    def cleanup(self):
        try:
            self.tframe.pack_forget()
            self.canvas._tkcanvas.pack_forget()
            del self.canvas
            del self.f
        except:
            pass

    def plot(self, ext):
        filename = asksaveasfilename(title="Plot to file...",
                                     initialfile='%s-response' % self.name,
                                     defaultextension='.%s' % ext,
                                     filetypes=[(ext.upper(), '*.%s' % ext)])
        if not filename:
            return
        self.canvas.print_figure(filename)

    def state(self, st, val, path):
        self.cleanup()
        if st != 'RESPONSE':
            return

        self.name = os.path.basename(path[:-9])
        self.f = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.f, master=self.tframe)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.tframe.pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        if len(val.params) > 2:
            ax = Axes3D(self.f, azim=30.0, elev=30.0)
            ax.text2D(0.5, 0.5,'Cannot plot response functions\nwith more than 2 parameters',
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform = ax.transAxes)
        elif len(val.params) == 2:
            labels = CB.get('Labels')
            ax = Axes3D(self.f, azim=30.0, elev=30.0)
            val.plot(ax=ax, fig=self.f, title=0, labels=labels)
        else:
            self.a = self.f.add_subplot(111)
            self.a.grid(True)
            val.plot(fig=self.a)

class PlotFrame:
    def __init__(self, parent):
        self.parent = parent
        # TOP FRAME - CANVAS
        self.f = plt.figure(figsize=(5, 5))
        self.a = self.f.add_subplot(111)
        self.a.grid(True)
        #self.a.set_xlabel(self.description)
        self.a.set_ylabel("Probability")
        self.canvas = FigureCanvasTkAgg(self.f, master=parent)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

    def update(self):
        self.canvas.draw()

    def get_plot(self):
        return self.a

    def plot(self, ext):
        name = 'puq-plot'
        filename = asksaveasfilename(title="Plot to file...",
                                     initialfile=name,
                                     defaultextension='.%s' % ext,
                                     filetypes=[(ext.upper(), '*.%s' % ext)])
        if not filename:
            return
        self.canvas.print_figure(filename)

def PdfFactory(frame, obj, plotframe, nb=None, color=None, desc=None):
    state = None
    if isinstance(obj, PDF):
        if hasattr(obj, 'data'):
            state = 'PDF'
        else:
            state = 'PDF2'
    elif isinstance(obj, Parameter):
        if hasattr(obj.pdf, 'data'):
            state = 'PDF'
        else:
            state = 'PDF2'

    if state == 'PDF':
        return PdfFrameComplex(frame, obj, plotframe, nb=nb, color=color, desc=desc)
    if state == 'PDF2':
        return PdfFrameSimple(frame, obj, plotframe, nb=nb, color=color, desc=desc)
    return None

class PdfFrame:

    def get_color(self, color):
        if color == None:
            color = 'blue'
        elif isinstance(color, int):
            color = sq_colors[color]
        return color

    def copy_clip(self):
        root.clipboard_clear()
        root.clipboard_append(pickle(self.pdf))

    def export_pdf(self, ext):
        # Dump pdf as csv, json, or python
        import csv
        if self.par:
            name = '%s-pdf' % self.par.name
        else:
            name = 'PDF'
        extension = '.'+ext
        filetypes = [(ext.upper(), '*.%s' % ext)]
        filename = asksaveasfilename(title="Save PDF to CSV file...",
                                     initialfile=name,
                                     defaultextension=extension,
                                     filetypes=filetypes)
        if not filename:
            return

        if ext == 'csv':
            with open(filename, 'w') as csvfile:
                spamwriter = csv.writer(csvfile)
                for x, prob in np.column_stack((self.pdf.x, self.pdf.y)):
                    spamwriter.writerow([x, prob])
            m = "Wrote %s pairs of (value, probability) data to '%s'.\n" % (len(self.pdf.x), filename)

            t = Toplevel(self.parent)
            t.title("Wrote CSV File")
            msg = Message(t, text=m, width=500)
            button = Button(t, text="OK", command=t.destroy)
            button.pack(side=BOTTOM)
            msg.pack(fill=BOTH, expand=1)
        elif ext == 'py':
            with open(filename, 'w') as pyfile:
                pyfile.write(repr(self.pdf))
        elif ext == 'json':
            with open(filename, 'w') as jfile:
                jfile.write(pickle(self.pdf))

    def min_changed(self, newmin):
        if newmin != '':
            newmin = float(newmin)
        if newmin != self.min:
            self.changed(min=newmin)

    def max_changed(self, newmax):
        if newmax != '':
            newmax = float(newmax)
        if newmax != self.max:
            self.changed(max=newmax)


class PdfFrameComplex(PdfFrame):

    def __init__(self, parent, obj, plotframe, nb=None, color=None, desc=None):
        #print "PdfFrameComplex Init"
        self.plotframe = plotframe
        self.a = plotframe.get_plot()

        self.nb = nb
        if nb:
            self.tnum = color
        color = self.get_color(color)

        bframe = Frame(parent)
        lframe = Frame(bframe)
        rframe = Frame(bframe)

        self.show = IntVar(value=1)
        self.bars = IntVar(value=0)
        cframe = LabelFrame(bframe)

        # add color selector and show to details
        if nb:
            if desc:
                tframe = Frame(bframe)
                Label(tframe, text=desc, font=Font(weight="bold")).pack(side=TOP, fill=BOTH, expand=1)
            c1 = Checkbutton(cframe, variable=self.show, command=self.cb, pady=5, text='Show')
            c1.pack(fill=BOTH, expand=1)
            ToolTip(c1, follow_mouse=1, text='Show Plot')

        img = sq_image(color)
        self.clab = Label(cframe, image=img)
        self.clab.photo = img
        self.clab.bind("<Button-1>", self.popup)
        self.clab.pack(fill=BOTH, expand=1)
        ToolTip(self.clab, follow_mouse=1, text='Select Plot Color')

        c2 = Checkbutton(cframe, variable=self.bars, command=self.cb, pady=5, text='Bars')
        c2.pack(fill=BOTH, expand=1)
        ToolTip(c2, follow_mouse=1, text='Show Histogram Bars')
        cp = ColorPop(self.clab, callback=self.color_changed)

        if isinstance(obj, PDF):
            self.par = None
            self.pdf = obj
        else:
            self.pdf = obj.pdf
            self.par = obj

        self.data = self.pdf.data
        self.fit = False

        kde = gaussian_kde(self.data)
        bw = kde.factor
        self.bw = None

        iqr = scipy.stats.scoreatpercentile(self.data, 75) - scipy.stats.scoreatpercentile(self.data, 25)
        if iqr == 0.0:
            self.nbins=50
        else:
            self.nbins = int((np.max(self.data) - np.min(self.data)) / (2*iqr/len(self.data)**(1.0/3)) + .5)
            self.nbins = max(2, self.nbins)

        self.min = None
        self.max = None

        pdf = self.pdf

        self.color = color

        if self.bars.get():
            self.line1 = self.a.hist(self.data, self.nbins, normed=1, facecolor=self.color, alpha=0.2)

        if self.show.get():
            self.line2, = self.a.plot(pdf.x, pdf.y, color=color, linewidth=3)

        # BOTTOM RIGHT - FIT FRAME
        fitframe = LabelFrame(rframe, text="FIT")
        RB(fitframe, ["Gaussian", "Linear"], val=self.fit, callback=self.fit_changed)

        # Bandwidth frame
        bwframe = LabelFrame(fitframe, text='Bandwidth', padx=5, pady=5)
        res = 10**round(math.log(bw/100.0, 10))
        r1 = round(bw / 10.0)
        if r1 == 0.0:
            r1 += res
        r2 = round(bw * 10.0)
        self.bwscale = Scale(bwframe, from_=r1, to=r2, orient=HORIZONTAL,
            resolution=res, showvalue=0, command=self.bw_changed)
        self.bwscale.set(bw)
        self.bwscale.config(command=self.bw_changed)
        self.bwe = Entry(bwframe, width=5)
        self.bwe.bind('<Return>', self.bw_changed)
        self.bwe.pack(side=LEFT)
        self.bwscale.set(bw)
        self.bwe.delete(0, END)
        self.bwe.insert(0, "%.3g" % bw)
        self.bwscale.pack(fill=BOTH, expand=True, side=LEFT)

        # Bin frame
        binframe = LabelFrame(fitframe, text='Bins', padx=5, pady=5)
        self.binscale = Scale(binframe, from_=2, to=100, orient=HORIZONTAL,
            resolution=1, showvalue=0)
        self.binscale.set(self.nbins)
        self.binscale.config(command=self.bins_changed)
        self.bine = Entry(binframe, width=5)
        self.bine.bind('<Return>', self.bins_changed)
        self.bine.pack(side=LEFT)
        self.bine.delete(0, END)
        self.bine.insert(0, str(self.nbins))
        self.binscale.pack(fill=BOTH, expand=True, side=LEFT)
        bwframe.pack(side=TOP, fill=BOTH, expand=True)
        binframe.pack(side=TOP, fill=BOTH, expand=True)

        self.bwscale.config(state='disabled')
        self.bwe.config(state='disabled')

        fitframe.pack(side=RIGHT, fill=BOTH, expand=1)

        # Bottom Left Frame
        fdata = LabelFrame(lframe, text='Raw Data', padx=5, pady=5)
        f1 = Frame(fdata)
        f2 = Frame(fdata)
        MyLabel(f1, "Mean", '%.3g' % np.mean(self.data)).frame.pack(side=LEFT, padx=5)
        MyLabel(f1, "Dev", '%.3g' % np.std(self.data)).frame.pack(side=LEFT, padx=5)
        MyLabel(f2, "Min", '%.3g' % np.min(self.data)).frame.pack(side=LEFT, padx=5)
        MyLabel(f2, "Max", '%.3g' % np.max(self.data)).frame.pack(side=LEFT, padx=5)
        fpdf = LabelFrame(lframe, text='Fitted PDF', padx=5, pady=5)
        f1.pack(side=TOP, pady = 5, padx = 10, fill=BOTH)
        f2.pack(side=TOP, pady = 5, padx = 10, fill=BOTH)

        f1 = Frame(fpdf)
        f2 = Frame(fpdf)
        self.entry_min = MyEntry(f2, "Min", StringVar(), '%.3g' % pdf.range[0], callback=self.min_changed)
        self.entry_max = MyEntry(f2, "Max", StringVar(), '%.3g' % pdf.range[1], callback=self.max_changed)
        self.label_mean = MyLabel(f1, "Mean", '%.3g' % pdf.mean)
        self.label_dev = MyLabel(f1, "Dev", '%.3g' % pdf.dev)
        self.label_mode = MyLabel(f1, "Mode", '%.3g' % pdf.mode)

        for lab in [self.label_mean, self.label_dev, self.label_mode]:
            lab.frame.pack(side=LEFT, padx=5)
        f1.pack(side=TOP, pady = 5, padx = 10, fill=BOTH)
        f2.pack(side=TOP, pady = 5, padx = 10, fill=BOTH)

        fdata.pack(side=TOP, fill=BOTH)
        fpdf.pack(side=TOP, fill=BOTH)

        if nb and desc:
            tframe.pack(side=TOP, fill=BOTH, expand=0)
        cframe.pack(side=LEFT, fill=BOTH, expand=0)

        lframe.pack(side=LEFT, fill=BOTH, expand=1)
        rframe.pack(side=RIGHT, fill=BOTH, expand=1)
        bframe.pack(side=TOP, fill=BOTH, expand=1)

    def changed(self, fit=None, min=None, max=None, nbins=None, bw=None):
        #print 'PDF CHANGED %s %s %s %s %s' % (fit, min, max, nbins, bw)
        if fit != None:
            self.fit = fit
            self.binscale.config(state='normal')
            self.bine.config(state='normal')
            if self.fit == 'Linear':
                state = 'disabled'
            else:
                state = 'normal'
            self.bwscale.config(state=state)
            self.bwe.config(state=state)

        if min != None:
            if min == '':
                self.min = None
            else:
                self.min = min

        if max != None:
            if max == '':
                self.max = None
            else:
                self.max = max

        if nbins != None:
            self.nbins = nbins

        if bw != None:
            self.bw = bw
        if fit != None or bw != None or (self.fit == 'Linear' and nbins != None):
            self.pdf = ExperimentalPDF(self.data, fit=self.fit, nbins=self.nbins, bw=self.bw, min=self.min, max=self.max, force=1)
        try:
            self.line2.remove()
        except:
            pass

        try:
            for patch in self.line1[2]:
                patch.remove()
        except:
            pass
        self.a.relim()
        if self.bars.get():
            self.line1 = self.a.hist(self.data, self.nbins, normed=1, facecolor=self.color, alpha=0.2)
        if self.show.get():
            self.line2, = self.a.plot(self.pdf.x, self.pdf.y, self.color, linewidth=3)
        self.plotframe.update()
        self.entry_min.update('%.3g' % self.pdf.range[0])
        self.entry_max.update('%.3g' % self.pdf.range[1])
        self.label_mean.update('%.3g' % self.pdf.mean)
        self.label_dev.update('%.3g' % self.pdf.dev)
        self.label_mode.update('%.3g' % self.pdf.mode)


    def bins_changed(self, val):
        if isinstance(val, Event):
            val = int(self.bine.get())
        else:
            val = int(val)
        if val != self.nbins:
            #print "bins_changed", val
            self.bine.delete(0, END)
            self.bine.insert(0, str(val))
            self.changed(nbins=val)

    def bw_changed(self, val):
        if isinstance(val, Event):
            val = self.bwe.get()
            try:
                val = float(val)
            except:
                if val != 'silverman':
                    val = None
                kde = gaussian_kde(self.data, bw_method=val)
                val = kde.factor

            self.bwscale.set(val)
        else:
            val = float(val)
        if val != self.bw:
            #print "BW changed from %s to %s" % (self.bw, val)
            if self.bw == None:
                self.bw = val
            else:
                self.bwe.delete(0, END)
                self.bwe.insert(0, "%.3g" % val)
                self.changed(bw=val)

    def fit_changed(self, val):
        if val != self.fit:
            self.changed(fit=val)

    def cb(self):
        self.changed()

    def color_changed(self, color):
        self.color = color
        self.changed()
        if self.nb:
            self.nb.tab(self.tnum,image=sq_image(color))
        self.clab.config(image=sq_image(color))

    def popup(self, event):
        self.menu.post(event.x_root, event.y_root)

class ColorPop:
    def __init__(self, parent, callback):
        self.callback = callback

        # create a popup menu
        self.aMenu = Menu(root, tearoff=0)
        for color in sq_colors:
            self.aMenu.add_command(image=sq_image(color), command=lambda c=color: self.callback(c))

        # attach popup to frame
        parent.bind("<Button-1>", self.popup)

    def popup(self, event):
        self.aMenu.post(event.x_root, event.y_root)

class PdfFrameSimple(PdfFrame):

    def __init__(self, parent, obj, plotframe, nb=None, color=None, desc=None):
        #print "PdfFrameSimple Init"
        self.plotframe = plotframe
        self.a = plotframe.get_plot()

        self.nb = nb
        if nb:
            self.tnum = color
        color = self.get_color(color)

        bframe = Frame(parent)
        lframe = Frame(bframe, bd=1)
        rframe = Frame(bframe)

        self.show = IntVar(value=1)
        if nb:
            if desc:
                tframe = Frame(bframe)
                Label(tframe, text=desc, font=Font(weight="bold")).pack(fill=X, expand=1)
                tframe.pack(side=TOP, fill=X, expand=0)

            c = Checkbutton(lframe, variable=self.show, command=self.cb)
            c.pack()
            tool1 = ToolTip(c, follow_mouse=1, text='Show Plot')

        img = sq_image(color)
        self.clab = Label(lframe, text='  ', image=img)
        self.clab.photo = img
        self.clab.bind("<Button-1>", self.popup)
        cp = ColorPop(self.clab, callback=self.color_changed)
        tool2 = ToolTip(self.clab, follow_mouse=1, text='Select Plot Color')
        self.clab.pack(fill=X, expand=1)

        if isinstance(obj, PDF):
            self.par = None
            self.pdf = obj
        else:
            self.par = obj
            self.pdf = obj.pdf

        self.min = None
        self.max = None
        self.pdf_orig = self.pdf

        self.color = color
        self.line2, = self.a.plot(self.pdf.x, self.pdf.y, color=self.color, linewidth=3)

        # BOTTOM RIGHT
        frame3 = Frame(rframe)
        if self.par:
            frame1 = Frame(rframe)
            MyLabel(frame1, 'Type', self.par.__class__.__name__, bg='white').frame.pack(side=LEFT, padx=5)
        self.mean = MyLabel(frame3, "Mean", '%.3g' % self.pdf.mean)
        self.dev = MyLabel(frame3, "Dev", '%.3g' % self.pdf.dev)
        self.mode = MyLabel(frame3, "Mode", '%.3g' % self.pdf.mode)
        for lab in [self.mean, self.dev, self.mode]:
            lab.frame.pack(side=LEFT, padx=5)
        self.entry_min = MyEntry(frame3, "Min", StringVar(), '%.3g' % self.pdf.range[0], callback=self.min_changed)
        self.entry_max = MyEntry(frame3, "Max", StringVar(), '%.3g' % self.pdf.range[1], callback=self.max_changed)
        if self.par:
            frame1.pack(side=TOP, anchor='nw', fill=BOTH, expand=1)
        frame3.pack(side=BOTTOM, anchor='nw', fill=BOTH, expand=1)

        lframe.pack(side=LEFT, fill=X, expand=0)
        rframe.pack(side=RIGHT, fill=X, expand=1)
        bframe.pack(side=TOP, fill=X, expand=0)

    def cb(self):
        self.changed()

    def color_changed(self, color):
        self.color = color
        self.changed()
        if self.nb:
            self.nb.tab(self.tnum,image=sq_image(color))
        self.clab.config(image=sq_image(color))

    def popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def changed(self, min=None, max=None):
        #print 'Parameter Changed %s %s' % (min, max)
        if min != None:
            if min == '':
                self.min = None
                self.pdf = self.pdf_orig
            else:
                self.min = min
                nsamp = options['pdf']['numpart']
                x = np.linspace(min, self.pdf.range[1], nsamp)
                y = np.interp(x, self.pdf_orig.x, self.pdf_orig.y)
                self.pdf = PDF(x, y)
        if max != None:
            if max == '':
                self.max = None
                self.pdf = self.pdf_orig
            else:
                self.max = max
                nsamp = options['pdf']['numpart']
                x = np.linspace(self.pdf.range[0], max, nsamp)
                y = np.interp(x, self.pdf_orig.x, self.pdf_orig.y)
                self.pdf = PDF(x, y)

        self.mean.update('%.3g' % self.pdf.mean)
        self.dev.update('%.3g' % self.pdf.dev)
        self.mode.update('%.3g' % self.pdf.mode)
        self.entry_min.update('%.3g' % self.pdf.range[0])
        self.entry_max.update('%.3g' % self.pdf.range[1])
        try:
            self.line2.remove()
        except:
            pass
        self.a.relim()
        if self.show.get():
            self.line2, = self.a.plot(self.pdf.x, self.pdf.y, color=self.color, linewidth=3)
        self.plotframe.update()

class TimeFrame:
    def __init__(self, parent):
        self.tframe = Frame(parent)
        TimeFrame.me = weakref.proxy(self)

    def cleanup(self):
        try:
            self.tframe.pack_forget()
            self.canvas._tkcanvas.pack_forget()
            del self.canvas
            del self.f
        except:
            pass

    def plot(self, ext):
        filename = asksaveasfilename(title="Plot to file...",
                                     initialfile='%s-response' % self.name,
                                     defaultextension='.%s' % ext,
                                     filetypes=[(ext.upper(), '*.%s' % ext)])
        if not filename:
            return
        self.canvas.print_figure(filename)

    def state(self, st, val, path):
        self.cleanup()
        if st != 'RESPONSE':
            return

        self.name = os.path.basename(path[:-9])
        self.f = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.f, master=self.tframe)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.tframe.pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        if len(val.params) > 2:
            ax = Axes3D(self.f, azim=30.0, elev=30.0)
            ax.text2D(0.5, 0.5,'Cannot plot response functions\nwith more than 2 parameters',
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform = ax.transAxes)
        elif len(val.params) == 2:
            labels = CB.get('Labels')
            ax = Axes3D(self.f, azim=30.0, elev=30.0)
            val.plot(ax=ax, fig=self.f, title=0, labels=labels)
        else:
            self.a = self.f.add_subplot(111)
            self.a.grid(True)
            val.plot(fig=self.a)


class SurFrame:
    def __init__(self, parent):
        self.parent = parent

    def cleanup(self):
        try:
            self.surframe.pack_forget()
        except:
            pass
    def rbf_changed(self, rbfunc):
        global modified
        #print "rbf changed to ", rbfunc
        #print self.val.rbf
        self.val.rbf = rbfunc
        del h5[self.path]
        h5[self.path] = pickle(self.val)
        # invalidate the pdf
        pdfpath = self.path[:-len('response')] + 'pdf'
        samplepath = self.path[:-len('response')] + 'samples'
        varname = self.path.split('/')[-2]
        if pdfpath in h5:
            del h5[pdfpath]
        if samplepath in h5:
            del h5[samplepath]

        # change treeview pdf tag to 'generate'
        for child in MyApp.app.tree.get_children('psweep'):
            item = MyApp.app.tree.item(child)
            if item['text'] == varname:
                for ch in MyApp.app.tree.get_children(child):
                    item = MyApp.app.tree.item(ch)
                    if item['text'] == 'pdf':
                        MyApp.app.tree.item(ch, tags = ['generate'])

        modified = True
        MyApp.state_changed('RESPONSE', self.val, self.path)

    def state(self, st, val, path):
        self.cleanup()
        if st != 'RESPONSE':
            return

        if isinstance(val, SampledFunc):
            self.val = val
            self.surframe = LabelFrame(self.parent, text="Radial Basis Function")
            rbfvals = [
                   "multiquadric",
                   "linear",
                   "cubic",
                   "quintic",
                   "inverse",
                   "gaussian"
                   ]
            self.rbf = MyCombobox(self.surframe, 'RBF', rbfvals, current=val.rbf, callback=self.rbf_changed)
        else:
            self.surframe = LabelFrame(self.parent, text="Surface")

            # Surface Pane
            self.eqn = ScrolledText.ScrolledText(self.surframe, height=2, )
            self.eqn.insert(END, val.eqn)
            self.eqn.pack(side=TOP, expand=YES, fill=BOTH, padx=5, pady=5)

            # RMSE
            rmsep = val.rmse()[1]
            if rmsep > 10:
                bgcolor = 'red'
            elif rmsep > 5:
                bgcolor = 'orange'
            elif rmsep > 2:
                bgcolor = 'yellow'
            else:
                bgcolor = ''
            self.rmse = MyLabel(self.surframe, value='%.3g%%' % rmsep, text='RMSE', bg=bgcolor)
            self.rmse.frame.pack(side=TOP, anchor='w', padx=5, pady=5)
        self.surframe.pack(side=LEFT, fill=BOTH, expand=1)

class ParFrame:

    def __init__(self, parent):
        self.parent = parent

    def cleanup(self):
        try:
            self.parframe.pack_forget()
        except:
            pass

    def state(self, st, val, path):
        self.cleanup()

        if st != 'RESPONSE':
            return

        self.parframe = Frame(self.parent)
        self.parframe.pack(side=LEFT, fill=BOTH, expand=1)

        # Parameters Table with scrollbar
        scrollbar = Scrollbar(self.parframe)
        scrollbar.pack(side=RIGHT, fill=Y)
        t=ttk.Treeview(self.parframe, yscrollcommand=scrollbar.set, height=len(val.params))
        t["columns"]=("desc","pdf")
        t.column("#0", width=75)
        t.column("desc", width=100)
        t.column("pdf", width=400)
        t.heading("#0", text='Name')
        t.heading("#1", text='Description')
        t.heading("#2", text='PDF')
        for p in val.params:
            cname = p.__class__.__name__[:-9]
            pdf_str = '%s [%s - %s] mean=%s dev=%s mode=%s' % (cname, p.pdf.range[0], p.pdf.range[1], p.pdf.mean, p.pdf.dev, p.pdf.mode)
            t.insert("", "end", text=p.name, values=[p.description, pdf_str])
        t.tag_configure("ttk")
        scrollbar.config(command=t.yview)
        t.pack(side=TOP, fill=BOTH, expand=YES)

class MyApp:

    def __init__(self, parent, objlist):
        self.parent = parent
        parent.protocol('WM_DELETE_WINDOW', self.quit)

        # contains everything
        self.container = Frame(self.parent)
        self.container.pack(fill=BOTH, expand=YES)

        # top frame
        self.tframe = Frame(self.container)
        self.bframe = Frame(self.container)

        detailframe = None
        plotframe = PlotFrame(self.tframe)
        if isinstance(objlist, list):
            cnote = CNote(self.bframe)
            for cnum, obj in enumerate(objlist):
                f = Frame(cnote)
                PdfFactory(f, obj[0], plotframe, nb=cnote, color=cnum, desc=obj[2])
                cnote.add(f, color=cnum, text=obj[1], padding=3)
            cnote.pack(expand=1, fill=BOTH)
        else:
            detailframe = PdfFactory(self.bframe, objlist[0], plotframe)

        MB(parent, plotframe, detailframe)

        self.tframe.pack(side=TOP, fill=BOTH, expand=YES)
        self.bframe.pack(side=LEFT, fill=BOTH, expand=YES)

    def quit(self):
        global windows
        wdw = self.parent
        if wdw in windows:
            windows.remove(wdw)
        if not windows:
            wdw.quit()
        wdw.destroy()

def show_obj(objlist, compare=0):
    global root, windows

    root = Tk()
    root.withdraw()
    windows = []

    if compare:
        win = Toplevel()
        windows.append(win)
        win.title('PUQ Compare')
        MyApp(win, objlist)
    else:
        for i, obj in enumerate(objlist):
            win = Toplevel()
            windows.append(win)
            try:
                win.title(namelist[i])
            except:
                win.title(obj[2])
            MyApp(win, obj)
    root.mainloop()

# loads python file
# returns list [(obj, name, desc), (obj, name, desc), ...]
def python_load(fname):
    sys.path = [os.getcwd()] + sys.path
    module = os.path.splitext(os.path.split(fname)[1])[0]
    _temp = __import__(module, globals(), locals(), [], 0)

    pdflist = []
    for name, obj in _temp.__dict__.iteritems():
        if isinstance(obj, Parameter):
            desc = obj.description
            if desc == name:
                desc = ''
            pdflist.append((obj, name, "%s: %s (%s)" % (fname, name, desc)))
        elif isinstance(obj, PDF):
            pdflist.append((obj, name, "%s: %s" % (fname, name)))

    if 'run' in _temp.__dict__:
        def extract_params(uq,b,c):
            for pm in uq.params:
                if pm.description and pm.description != pm.name:
                    pdflist.append((pm, pm.name, ('%s: %s (%s)' % (fname, pm.name, pm.description))))
                else:
                    pdflist.append((pm, pm.name, ('%s: %s' % (fname, pm.name))))

        _temp.Sweep = extract_params
        _temp.run()

    if len(pdflist) == 0:
        print('Error: Found no PDFs or Parameters in %s' % fname)
        sys.exit(1)

    if len(pdflist) == 1:
        return pdflist

    while 1:
        print('\nList PDFs you want displayed, separated by commas.')
        print('\nFound the following PDFs:')
        for i, p in enumerate(pdflist):
            print("%d: %s" % (i, p[1]))
        num = raw_input("Which one(s) to display? (* for all) ")
        try:
            if num == '*':
                numlist = pdflist
            else:
                numlist = map(int, num.split(','))
                numlist = [pdflist[x] for x in numlist]
            break
        except:
            print('Invalid number. Try again.\n')

    return numlist


def get_name_desc(obj, loc):
    if isinstance(obj, Parameter):
        name = obj.name
        desc = obj.description
    else:
        name = os.path.splitext(loc)[0]
        desc = ''
    return name, desc

# returns list [(obj, name, desc), (obj, name, desc), ...]
def read_obj(loc):
    name = None
    desc = None
    if loc.startswith('http'):
        try:
            obj = NetObj(loc)
            name, desc = get_name_desc(obj, loc)
            return [(obj, name, desc)]
        except:
            print("Error accessing", loc)
            return []
    else:
        extension = loc.split('.')[-1]
        if extension == 'json':
            f = open(loc, 'r')
            obj = unpickle(f.read())
            f.close()
            name, desc = get_name_desc(obj, loc)
            return [(obj, name, desc)]
        elif extension == 'py':
            return python_load(loc)
    print("Don't know how to open %s." % loc)
    return []

def read(*args):
    opt, args = parse_args(list(args))
    objlist = []
    for arg in args:
        objs = read_obj(arg)
        objlist.extend(objs)
    if objlist:
        show_obj(objlist, compare=opt.c)

def parse_args(args):
    debug(args)
    usage = "Usage: puq read [options] [object] ...\n\
    where 'object' is a URI, python file, or JSON file\n\
Options:\n\
    -c  Compare. When two or more objects are given, display them in the same plot.\n\
"
    parser = OptionParser(usage)
    parser.add_option("-c", action="store_true", help="Compare plots.")
    (opt, ar) = parser.parse_args(args=args)
    return opt, ar

if __name__ == "__main__":
    read(*sys.argv[1:])
