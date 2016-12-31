#!/usr/bin/env python

"""
PUQ Analysis Tool

Martin Hunt
Purdue University

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
    from ScrolledText import ScrolledText
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

import os, weakref, re
import h5py
from puq import Parameter, PDF, ExperimentalPDF, pickle, unpickle, SampledFunc
import math
import webbrowser, shutil, atexit
from scipy.stats import gaussian_kde

DB_LIST = ["http://dash.prism.nanohub.org/prism/default/call/run/upload_service",
           "http://127.0.0.1:8000/prism/default/call/run/upload_service"
           ]
PUQPREFS = "~/.puq"


def upload_file(filename, rename=''):
    """
    from poster.encode import multipart_encode
    from poster.streaminghttp import register_openers
    import urllib2
    global DBADDR

    register_openers()
    datagen, headers = multipart_encode({"file": open(filename)})

    addr = "%s?rename=%s" % (DBADDR, rename)

    # Create the Request object
    request = urllib2.Request(addr, datagen, headers)

    # Actually do the request, and get the response
    return urllib2.urlopen(request).read()
    """


class Dialog(Toplevel):

    def __init__(self, parent, title=None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        #self.bind("<Return>", self.ok)
        #self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        return 1  # override

    def apply(self):
        pass  # override


class MyPrefs(Dialog):

    def __init__(self, parent, title=None, fname=''):
        self.fname = fname
        Dialog.__init__(self, parent, title)

    def body(self, master):
        uframe = LabelFrame(master, text="Upload URL")
        Label(uframe, text="New URL").grid(row=0, sticky=W, padx=10, pady=10)
        self.e2 = Entry(uframe, width=70)
        self.e2.bind('<Return>', self.changed)

        self.box_value = StringVar()
        self.box = ttk.Combobox(uframe, textvariable=self.box_value, state='readonly', width=70)
        self.box['values'] = DB_LIST
        self.box.current(DB_LIST.index(DBADDR))
        self.e2.grid(row=0, column=1, padx=10, pady=10)
        self.box.grid(row=1, column=0, columnspan=2, sticky=W, padx=10, pady=10)
        uframe.pack(side=RIGHT, fill=BOTH, expand=1)
        return self.box

    def changed(self, event):
        val = self.e2.get()
        if not val in DB_LIST:
            DB_LIST.append(val)
        self.box.configure(values=DB_LIST)
        self.e2.delete(0, END)
        self.box.current(DB_LIST.index(val))

    def apply(self):
        self.result = self.box_value.get()


def update_prefs(write=False):
    global PUQPREFS, DBADDR, DB_LIST
    shelf = {}

    if write:
        with open(os.path.expanduser(PUQPREFS), 'w') as f:
            shelf["DBADDR"] = DBADDR
            shelf["DB_LIST"] = DB_LIST
            f.write(pickle(shelf))
        return
    try:
        f = open(os.path.expanduser(PUQPREFS), 'r')
        shelf = unpickle(f.read())
    except:
        f = None

    if "DBADDR" in shelf:
        DBADDR = shelf["DBADDR"]
    else:
        DBADDR = DB_LIST[0]

    if "DB_LIST" in shelf:
        DB_LIST = shelf["DB_LIST"]

    if f is not None:
        f.close()


def preferences():
    global DBADDR
    m = MyPrefs(root, "Preferences", "myprefs")
    if m.result:
        DBADDR = m.result
        update_prefs(write=True)


def ask_upload():
    global h5, modified, filename, DBADDR
    MyApp.cleanup()

    # FIXME: Confirm upload destination.
    # exit on success.  Dialog on error.
    host = urlparse(DBADDR).netloc

    if not messagebox.askyesno("Upload", "Upload data from this file to %s" % host):
        return
    fname = filename

    # update = 0
    #d = MyDialog(root, "Uploading data to %s" % host, filename)
    #if d.result == None:
    #   return
    #fname, update = d.result

    psweep = h5.attrs['UQtype']
    dir = '/' + psweep
    for d in h5[dir]:
        if not 'pdf' in h5['%s/%s' % (dir, d)]:
            messagebox.showinfo("PDFs Needed", "All PDFs must be generated before uploading!", icon=messagebox.WARNING)
            return

    if not 'description' in h5.attrs or len(h5.attrs['description']) < 10:
        showinfo("No Description", "You must supply a detailed description before uploading this data file.", icon=messagebox.WARNING)
        MyApp.state_changed('D_INITIAL')
        return

    h5.close()

    try:
        res = upload_file(filename, rename=fname)
    except:
        res = ''

    if res != 'OK':
        if res == 'EXISTS':
            messagebox.showinfo("FAILED", "The upload failed because that file is already in the database.", icon=messagebox.WARNING)
        else:
            messagebox.showinfo("FAILED", "The upload failed for an unknown reason.", icon=messagebox.WARNING)
    root.quit()


def cleanup_and_exit(save):
    global h5, modified, fname_orig, filename
    try:
        h5.close()
        h5 = None
        if save and modified:
            print("Saving Changes")
            os.remove(fname_orig)
        else:
            os.remove(filename)
            os.rename(fname_orig, filename)
        root.quit()
    except:
        pass


def ask_quit():
    global modified
    #print 'ASK_QUIT'
    MyApp.cleanup()
    if modified:
        if messagebox.askyesno("Save Changes", "You have made changes. Save them to the HDF5 file?", icon=messagebox.WARNING):
            cleanup_and_exit(True)
    cleanup_and_exit(False)


class CB:
    # checkbutton
    CB_list = []

    def __init__(self, parent, txt, val=1, callback=None):
        self.callback = callback
        CB.CB_list.append(weakref.proxy(self))
        self.var = IntVar()
        self.var.set(val)
        self.txt = txt
        self.cb = Checkbutton(parent, text=txt, variable=self.var, command=self.changed)
        self.cb.pack(side=TOP, padx=5, pady=5, anchor='w')

    def changed(self):
        #print "CB changed to %s" % (self.var.get())
        if self.callback:
            self.callback(self.var.get())
        else:
            MyApp.state_changed()

    def state(self, st):
        self.cb.config(state=st)

    @staticmethod
    def get(name):
        for n in CB.CB_list:
            if name == n.txt:
                return n.var.get()


class RB:
    # radiobutton
    RB_list = []

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
        self.entry.pack(side=LEFT, padx=5, pady=5, anchor='w')

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


class PlotOption:
    def __init__(self, parent):
        self.frame = LabelFrame(parent, text="Plot Options")
        self.frame.pack(side=TOP, fill=BOTH)

    def state(self, state, val, path):
        return
        """
        if state == 'RESPONSE' or state == 'SAMPLED' or state == 'PDF':
            st = 'normal'
        else:
            st = 'disabled'
        """


class MB:
    def __init__(self, parent):
        menubar = Menu(parent)
        parent['menu'] = menubar
        self.st = 'D_INITIAL'

        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Upload", command=ask_upload)
        filemenu.add_separator()
        filemenu.add_command(label="Preferences", command=preferences)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=ask_quit)

        self.exportmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=self.exportmenu)
        self.exportmenu.add_command(label="Copy to Clipboard", command=self.copy_clip, state=DISABLED)
        self.exportmenu.add_command(label="Export as JSON", command=self.export_json, state=DISABLED)
        self.exportmenu.add_command(label="Export to CSV file", command=self.export_csv, state=DISABLED)
        self.exportplot = Menu(self.exportmenu, tearoff=0)
        self.exportmenu.add_cascade(label="Plot to", menu=self.exportplot)
        fig = plt.figure()
        sup = fig.canvas.get_supported_filetypes()
        keys = list(sup.keys())
        keys.sort()
        for key in keys:
            lab = '%s : %s' % (key.upper(), sup[key])
            self.exportplot.add_command(label=lab, command=lambda key=key: self.plot(key))

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        helpmenu.add_command(label="Online Help", command=self.open_help)
        menubar.add_cascade(label="Help", menu=helpmenu)
        parent.config(menu=menubar)

    def copy_clip(self):
        if self.st == 'RESPONSE':
            ResponseFrame.me.copy_clip()
        else:
            PdfFrame.me.copy_clip()

    def export_csv(self):
        PdfFrame.me.export_pdf('csv')

    def export_json(self):
        if self.st == 'RESPONSE':
            ResponseFrame.me.export_response()
        else:
            PdfFrame.me.export_pdf('json')

    def plot(self, ext):
        if self.st == 'PDF':
            PdfFrame.me.plot(ext)
        elif self.st == 'RESPONSE':
            ResponseFrame.me.plot(ext)
        elif self.st == 'PARAMETER':
            ParameterFrame.me.plot(ext)

    def open_help(self):
        webbrowser.open('http://c-primed.github.io/puq/')

    def about(self):
        messagebox.showinfo(message=__doc__, title='ABOUT')

    def state(self, st, val, path):
        # print "MB state %s" % st
        self.st = st
        s0, s1 = DISABLED, DISABLED
        if st == 'PDF' or st == 'PARAMETER':
            s0, s1 = NORMAL, NORMAL
        elif st == 'RESPONSE':
            s0, s1 = NORMAL, DISABLED

        self.exportmenu.entryconfig(0, state=s0)
        self.exportmenu.entryconfig(1, state=s0)
        self.exportmenu.entryconfig(2, state=s1)
        self.exportmenu.entryconfig(3, state=s0)


class InitFrame:
    def __init__(self, parent):
        global h5
        self.tframe = Frame(parent)

        attrs = {'Username': 'username',
                 'Hostname': 'hostname',
                 'Date': 'date',
                 'Type': 'UQtype'}
        for a in attrs:
            if attrs[a] in h5.attrs:
                val = h5.attrs[attrs[a]]
            else:
                val = ''
            MyLabel(self.tframe, a, val, bg='white').frame.pack(side=LEFT, padx=5)

        numjobs = len(h5['/output/jobs'])-1
        MyLabel(self.tframe, 'Jobs', numjobs, bg='white').frame.pack(side=LEFT, padx=5)

        self.paneframe = PanedWindow(parent, orient=VERTICAL)

        dframe = LabelFrame(self.paneframe, text="Description")
        self.desc = ScrolledText(dframe, height=5)
        if 'description' in h5.attrs:
            self.olddesc = h5.attrs['description']
        else:
            self.olddesc = ""
        if self.olddesc == "":
            self.olddesc = "<INSERT DESCRIPTION HERE>"
        self.desc.insert(1.0, self.olddesc)
        self.desc.bind("<KeyRelease>", self.update_desc)

        try:
            scriptpath = h5['/input/scriptname'].value
        except:
            scriptpath = 'N/A'
        sframe = LabelFrame(self.paneframe, text=scriptpath)
        script = ScrolledText(sframe)
        try:
            script.insert(1.0, h5['/input/script'].value)
        except:
            script.insert(1.0, 'Unavailable')
        script.config(state=DISABLED)
        self.desc.pack(fill=BOTH, side=TOP, expand=True)
        script.pack(fill=BOTH, side=TOP, expand=True)
        self.paneframe.add(dframe)
        self.paneframe.add(sframe)

    def update_desc(self, x):
        global modified
        modified = True
        h5.attrs['description'] = str(self.desc.get(1.0, END)).strip()

    def cleanup(self):
        self.tframe.pack_forget()
        self.paneframe.pack_forget()

    def state(self, st, val, path):
        if st == 'D_INITIAL':
            self.tframe.pack(fill=X, side=TOP, expand=0, padx=5, pady=5)
            self.paneframe.pack(fill=BOTH, expand=True)
        else:
            self.cleanup()


class BasicFrame:
    def __init__(self, parent):
        self.txt = ScrolledText(parent)

    def state(self, st, val, path):
        if st == 'DEV' or st == 'MEAN':
            self.txt.delete(1.0, END)
            self.txt.insert(1.0, val)
            self.txt.pack(fill=BOTH, side=LEFT, expand=True)
        else:
            self.txt.pack_forget()


class DataFrame:
    def __init__(self, parent):
        self.txt = ScrolledText(parent)

    def state(self, st, val, path):
        if st == 'D_DATA':
            val = "This section contains the raw output of every job."
            self.txt.delete(1.0, END)
            self.txt.insert(1.0, val)
            self.txt.pack(fill=BOTH, side=LEFT, expand=True)
        else:
            self.txt.pack_forget()


class StdoutFrame:
    def __init__(self, parent):
        self.txt = ScrolledText(parent)

    def state(self, st, val, path):
        if st == 'D_STDOUT':
            if not path:
                # directory
                errlist = val
                if errlist:
                    val = 'There were problems with %d jobs.\n\nTo see which jobs had errors, expand the stderr and stdout sections and look for red numbers.' % len(errlist)
                else:
                    val = 'All jobs completed successfully.'
            else:
                try:
                    val = h5[path].value
                except:
                    val = ''

            self.txt.delete(1.0, END)
            self.txt.insert(1.0, val)
            self.txt.pack(fill=BOTH, side=LEFT, expand=True)
        else:
            self.txt.pack_forget()


class TextFrame:
    def __init__(self, parent):
        self.parent = parent

    def state(self, st, val, path):
        try:
            self.stext.pack_forget()
        except:
            pass

        tval = ''
        if st == 'SENSITIVITY':
            if type(val) is str:
                # for backwards compatibility
                newval = []
                for g in re.findall("\(([^\\)]+)\)", val):
                    m = re.search("'([^']+)', \\{'std': ([^,]+), 'ustar': ([^\\}]+)\\}", g)
                    newval.append((m.group(1), {'std': float(m.group(2)), 'ustar': float(m.group(3))}))
                val = newval

            max_name_len = max(map(len, [p[0] for p in val]))
            tval = "SENSITIVITY:\n"
            tval += "Var%s     u*            dev\n" % (' '*(max_name_len))
            tval += '-'*(28+max_name_len) + '\n'
            for item in val:
                pad = ' '*(max_name_len - len(item[0]))
                tval += "%s%s    %.4e    %.4e\n" % (pad, item[0], item[1]['ustar'], item[1]['std'])
        elif st == 'D_PSWEEP':
            if path in h5:
                outvars = map(str, h5[path].keys())
                numjobs = len(h5['/output/jobs']) - 1
                tval = "%s Jobs\n\nOUTPUT VARIABLES:\n" % numjobs
                for var in outvars:
                    desc = h5['%s/%s' % (path, var)].attrs['description']
                    if desc:
                        tval += '   %s (%s)\n' % (var, desc)
                    else:
                        tval += '   %s\n' % var
            else:
                tval = "Analysis Failed. There is no data here. See the 'data' section."
        elif st == 'D_PSWEEP_VAR':
            tval = "OUTPUT VARIABLE %s " % os.path.basename(path)
            desc = h5[path].attrs['description']
            if desc:
                tval += ' (%s)' % desc
            tval += '\n'

        if not tval:
            return

        self.stext = ScrolledText(self.parent)
        self.stext.insert(END, tval)
        self.stext.config(state=DISABLED)
        self.stext.pack(fill=BOTH, side=TOP, expand=True)


class ProgressFrame:
    # might be a progressbar someday
    def __init__(self, parent):
        self.parent = parent

    def state(self, st, val, path):
        if st == 'PROGRESS':
            str = "Generating PDF for %s\n\nPlease Wait." % (val)
            self.txt = ScrolledText(self.parent)
            self.txt.insert(END, str)
            self.txt.pack(fill=BOTH, side=LEFT, expand=True)
        else:
            try:
                self.txt.pack_forget()
            except:
                pass


class PdfFrame:
    def __init__(self, parent):
        self.parent = parent
        PdfFrame.me = weakref.proxy(self)

    def cleanup(self):
        try:
            self.tframe.pack_forget()
            self.bframe.pack_forget()
            self.canvas._tkcanvas.pack_forget()
            del self.canvas
            del self.f
        except:
            pass

    def copy_clip(self):
        root.clipboard_clear()
        root.clipboard_append(pickle(self.pdf))

    def export_pdf(self, ext):
        # Dump pdf as csv, json, or python
        import csv
        if hasattr(self, 'par') and self.par:
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

    def state(self, st, pdf, path):
        global h5
        self.cleanup()
        if st != 'PDF':
            return

        self.tframe = Frame(self.parent)
        self.bframe = Frame(self.parent)
        self.lframe = Frame(self.bframe)
        self.rframe = Frame(self.bframe)

        self.pdf = pdf
        self.path = path
        self.name = os.path.basename(self.path[:-4])
        self.data = h5['%s/samples' % self.path[:-3]]

        if 'response' in h5[self.path[:-3]]:
            sdtext = 'Sampled Data from the Response Surface'
        else:
            sdtext = 'Sampled Data'

        try:
            self.fit = h5[path].attrs['fit']
            if self.fit is True or self.fit.lower() == 'gaussian':
                self.fit = 'Gaussian'
            else:
                self.fit = 'Linear'
        except:
            self.fit = False

        try:
            self.bw = h5[path].attrs['bw']
        except:
            kde = gaussian_kde(self.data)
            self.bw = kde.factor

        try:
            self.nbins = h5[path].attrs['nbins']
        except:
            iqr = scipy.stats.scoreatpercentile(self.data, 75) - scipy.stats.scoreatpercentile(self.data, 25)
            if iqr == 0.0:
                self.nbins = 50
            else:
                self.nbins = int((np.max(self.data) - np.min(self.data)) / (2*iqr/len(self.data)**(1.0/3)) + .5)

        if 'min' in h5[path].attrs:
            self.min = h5[path].attrs['min']
        else:
            self.min = None

        if 'max' in h5[path].attrs:
            self.max = h5[path].attrs['max']
        else:
            self.max = None

        pdf = ExperimentalPDF(self.data, fit=self.fit, nbins=self.nbins, bw=self.bw, min=self.min, max=self.max, force=1)

        # TOP FRAME - CANVAS
        self.f = plt.figure(figsize=(5, 5))
        self.a = self.f.add_subplot(111)
        self.a.grid(True)
        #self.a.set_xlabel(self.description)
        self.a.set_ylabel("Probability")

        self.line1 = self.a.hist(self.data, self.nbins, normed=1, facecolor='blue', alpha=0.3)
        self.line2, = self.a.plot(pdf.x, pdf.y, color='red', linewidth=3)

        self.canvas = FigureCanvasTkAgg(self.f, master=self.tframe)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        # BOTTOM RIGHT - FIT FRAME
        self.fitframe = LabelFrame(self.rframe, text="FIT")
        self.fitbutton = RB(self.fitframe, ["Gaussian", "Linear"], val=self.fit, callback=self.fit_changed)

        # Bandwidth frame
        bwframe = LabelFrame(self.fitframe, text='Bandwidth', padx=5, pady=5)
        res = 10**round(math.log(self.bw/100.0, 10))
        r1 = round(self.bw / 10.0)
        if r1 == 0.0:
            r1 += res
        r2 = round(self.bw * 10.0)
        self.bwscale = Scale(bwframe, from_=r1, to=r2, orient=HORIZONTAL,
                             resolution=res, showvalue=0, command=self.bw_changed)
        self.bwe = Entry(bwframe, width=5)
        self.bwe.bind('<Return>', self.bw_changed)
        self.bwe.pack(side=LEFT)
        self.bwscale.set(self.bw)
        self.bwe.delete(0, END)
        self.bwe.insert(0, "%.3g" % self.bw)
        self.bwscale.pack(fill=BOTH, expand=True, side=LEFT)
        if self.fit == 'Linear':
            self.bwscale.config(state='disabled')
            self.bwe.config(state='disabled')

        # Bin frame
        binframe = LabelFrame(self.fitframe, text='Bins', padx=5, pady=5)
        binscale = Scale(binframe, from_=2, to=100, orient=HORIZONTAL,
                         resolution=1, showvalue=0, command=self.bins_changed)
        binscale.set(self.nbins)
        self.bine = Entry(binframe, width=5)
        self.bine.bind('<Return>', self.bins_changed)
        self.bine.pack(side=LEFT)
        self.bine.delete(0, END)
        self.bine.insert(0, str(self.nbins))
        binscale.pack(fill=BOTH, expand=True, side=LEFT)
        bwframe.pack(side=TOP, fill=BOTH, expand=True)
        binframe.pack(side=TOP, fill=BOTH, expand=True)

        self.fitframe.pack(side=RIGHT, fill=BOTH, expand=1)

        # Bottom Left Frame
        fdata = LabelFrame(self.lframe, text=sdtext, padx=5, pady=5)
        f1 = Frame(fdata)
        f2 = Frame(fdata)
        MyLabel(f1, "Mean", '%.3g' % np.mean(self.data), bg='white').frame.pack(side=LEFT, padx=5)
        MyLabel(f1, "Dev", '%.3g' % np.std(self.data), bg='white').frame.pack(side=LEFT, padx=5)
        MyLabel(f2, "Min", '%.3g' % np.min(self.data), bg='white').frame.pack(side=LEFT, padx=5)
        MyLabel(f2, "Max", '%.3g' % np.max(self.data), bg='white').frame.pack(side=LEFT, padx=5)
        fpdf = LabelFrame(self.lframe, text='Fitted Data', padx=5, pady=5)
        f1.pack(side=TOP, pady=5, padx=10, fill=BOTH)
        f2.pack(side=TOP, pady=5, padx=10, fill=BOTH)

        f1 = Frame(fpdf)
        f2 = Frame(fpdf)
        self.entry_min = MyEntry(f2, "Min", StringVar(), '%.3g' % pdf.range[0], callback=self.min_changed)
        self.entry_max = MyEntry(f2, "Max", StringVar(), '%.3g' % pdf.range[1], callback=self.max_changed)
        self.label_mean = MyLabel(f1, "Mean", '%.3g' % pdf.mean, bg='white')
        self.label_dev = MyLabel(f1, "Dev", '%.3g' % pdf.dev, bg='white')
        self.label_mode = MyLabel(f1, "Mode", '%.3g' % pdf.mode, bg='white')

        for lab in [self.label_mean, self.label_dev, self.label_mode]:
            lab.frame.pack(side=LEFT, padx=5)
        f1.pack(side=TOP, pady=5, padx=10, fill=BOTH)
        f2.pack(side=TOP, pady=5, padx=10, fill=BOTH)

        fdata.pack(side=TOP, fill=BOTH)
        fpdf.pack(side=TOP, fill=BOTH)

        self.lframe.pack(side=LEFT, fill=BOTH, expand=0)
        self.rframe.pack(side=RIGHT, fill=BOTH, expand=1)
        self.tframe.pack(side=TOP, fill=BOTH, expand=1)
        self.bframe.pack(side=TOP, fill=BOTH, expand=0)

    def changed(self, fit=None, min=None, max=None, nbins=None, bw=None):
        global modified
        modified = True

        #print 'PDF CHANGED %s %s %s %s %s' % (fit, min, max, nbins, bw)
        if fit is not None:
            self.fit = fit
            if self.fit == 'Linear':
                state = 'disabled'
            else:
                state = 'normal'
            self.bwscale.config(state=state)
            self.bwe.config(state=state)

        if min is not None:
            if min == '':
                self.min = None
            else:
                self.min = min

        if max is not None:
            if max == '':
                self.max = None
            else:
                self.max = max

        if nbins is not None:
            self.nbins = nbins

        if bw is not None:
            self.bw = bw

        pdf = ExperimentalPDF(self.data, fit=self.fit, nbins=self.nbins, bw=self.bw, min=self.min, max=self.max, force=1)
        self.line2.remove()
        for patch in self.line1[2]:
            patch.remove()
        self.a.relim()
        self.line1 = self.a.hist(self.data, self.nbins, normed=1, facecolor='blue', alpha=0.3)
        self.line2, = self.a.plot(pdf.x, pdf.y, color='red', linewidth=3)
        self.canvas.draw()
        self.entry_min.update('%.3g' % pdf.range[0])
        self.entry_max.update('%.3g' % pdf.range[1])
        self.label_mean.update('%.3g' % pdf.mean)
        self.label_dev.update('%.3g' % pdf.dev)
        self.label_mode.update('%.3g' % pdf.mode)
        self.pdf = pdf

        del h5[self.path]
        h5[self.path] = pickle(pdf)
        h5[self.path].attrs['fit'] = self.fit
        if self.min is not None:
            h5[self.path].attrs['min'] = self.min
        if self.max is not None:
            h5[self.path].attrs['max'] = self.max
        h5[self.path].attrs['bw'] = self.bw
        h5[self.path].attrs['nbins'] = self.nbins

    def plot(self, ext):
        filename = asksaveasfilename(title="Plot to file...",
                                     initialfile='%s-pdf' % self.name,
                                     defaultextension='.%s' % ext,
                                     filetypes=[(ext.upper(), '*.%s' % ext)])
        if not filename:
            return
        self.canvas.print_figure(filename)

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
            #print "BW changed %s" % val
            self.bwe.delete(0, END)
            self.bwe.insert(0, "%.3g" % val)
            self.changed(bw=val)

    def fit_changed(self, val):
        if val != self.fit:
            self.changed(fit=val)

    def min_changed(self, newmin):
        if newmin == '':
            newmin = None
        else:
            newmin = float(newmin)
        if newmin != self.min:
            self.changed(min=newmin)

    def max_changed(self, newmax):
        if newmax == '':
            newmax = None
        else:
            newmax = float(newmax)
        if newmax != self.max:
            self.changed(max=newmax)


class ParameterFrame:
    def __init__(self, parent):
        self.parent = parent
        ParameterFrame.me = weakref.proxy(self)

    def cleanup(self):
        try:
            self.tframe.pack_forget()
            self.bframe.pack_forget()
            self.canvas._tkcanvas.pack_forget()
            del self.canvas
            del self.f
        except:
            pass

    def export_pdf(self):
        # Dump pdf data as csv
        import csv
        filename = asksaveasfilename(title="Save PDF to CSV file...",
                                     initialfile='%s-pdf' % self.par.name,
                                     defaultextension='.csv',
                                     filetypes=[('CSV', '*.csv')])
        if not filename:
            return

        with open(filename, 'wb') as csvfile:
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

    def plot(self, ext):
        filename = asksaveasfilename(title="Plot to file...",
                                     initialfile='%s-pdf' % self.par.name,
                                     defaultextension='.%s' % ext,
                                     filetypes=[(ext.upper(), '*.%s' % ext)])
        if not filename:
            return
        self.canvas.print_figure(filename)

    def state(self, st, par, path):
        global h5, cached_fit
        self.cleanup()
        if st != 'PARAMETER':
            return

        self.tframe = Frame(self.parent)
        self.bframe = Frame(self.parent)
        self.lframe = Frame(self.bframe)
        self.rframe = Frame(self.bframe)

        self.par = par
        self.pdf = par.pdf

        # TOP FRAME - CANVAS
        self.f = plt.figure(figsize=(5, 5))
        self.a = self.f.add_subplot(111)
        self.a.grid(True)
        self.a.set_ylabel("Probability")
        m = np.max(par.pdf.y)
        self.a.set_ylim(bottom=0, top=m*1.1)
        self.line2, = self.a.plot(par.pdf.x, par.pdf.y, color='red', linewidth=3)
        self.canvas = FigureCanvasTkAgg(self.f, master=self.tframe)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        # BOTTOM RIGHT
        """
        try:
            fit = cached_fit[self.path][0]
            if fit:
                fit = 'Gaussian'
            else:
                fit = 'Linear'
        except:
            fit = None
        self.fitframe = LabelFrame(self.rframe, text="FIT")
        self.fit = RB(self.fitframe, ["Gaussian", "Linear"], val=fit, callback=self.fit_changed)
        self.fitframe.pack(side=RIGHT, fill=BOTH, expand=1)
        """
        frame1 = Frame(self.lframe)
        frame2 = Frame(self.lframe)
        frame3 = Frame(self.lframe)
        MyLabel(frame1, 'Name', par.name, bg='white').frame.pack(side=LEFT, padx=5)
        MyLabel(frame1, 'Description', par.description, bg='white').frame.pack(side=LEFT, padx=5)
        MyLabel(frame2, 'Type', par.__class__.__name__, bg='white').frame.pack(side=LEFT, padx=5)
        self.entry_min = MyEntry(frame3, "Min", StringVar(), '%.3g' % par.pdf.range[0], callback=self.min_changed)
        self.entry_max = MyEntry(frame3, "Max", StringVar(), '%.3g' % par.pdf.range[1], callback=self.max_changed)
        MyLabel(frame3, "Mean", '%.3g' % par.pdf.mean, bg='white').frame.pack(side=LEFT, padx=5)
        MyLabel(frame3, "Dev", '%.3g' % par.pdf.dev, bg='white').frame.pack(side=LEFT, padx=5)
        frame1.pack(side=TOP, padx=5, pady=5, anchor='w')
        frame2.pack(side=TOP, padx=5, pady=5, anchor='w')
        frame3.pack(side=TOP, padx=5, pady=5, anchor='w')

        self.lframe.pack(side=LEFT, fill=BOTH, expand=1)
        self.rframe.pack(side=RIGHT, fill=BOTH, expand=1)
        self.tframe.pack(side=TOP, fill=BOTH, expand=1)
        self.bframe.pack(side=TOP, fill=BOTH, expand=0)

    def changed(self, fit=None, min=None, max=None):
        print('Parameter Changed %s %s %s' % (fit, min, max))
        # FIXME

    def fit_changed(self, val):
        if val == 'Gaussian':
            fit = True
        else:
            fit = False
        self.changed(fit=fit)

    def min_changed(self, newmin):
        if newmin != '':
            newmin = float(newmin)
        self.changed(min=newmin)

    def max_changed(self, newmax):
        if newmax != '':
            newmax = float(newmax)
        self.changed(max=newmax)


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
        if st != 'TIME':
            return
        self.name = os.path.basename(path[:-9])
        self.f = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.f, master=self.tframe)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.tframe.pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)
        self.a = self.f.add_subplot(111)
        self.a.grid(True)
        self.a.bar(np.arange(len(val)), val, align='center')
        plt.xlabel('Job')
        plt.ylabel('Seconds')


class ResponseFrame:
    def __init__(self, parent):
        self.tframe = Frame(parent)
        ResponseFrame.me = weakref.proxy(self)

    def cleanup(self):
        try:
            self.tframe.pack_forget()
            self.canvas._tkcanvas.pack_forget()
            plt.close(self.f)
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

    def copy_clip(self):
        root.clipboard_clear()
        root.clipboard_append(pickle(self.val))

    def export_response(self):
        name = '%s-response' % self.name
        filename = asksaveasfilename(title="Save Response to JSON file...",
                                     initialfile=name,
                                     defaultextension='.json',
                                     filetypes=[('JSON', '*.json')])
        if not filename:
            return

        with open(filename, 'w') as jfile:
            jfile.write(pickle(self.val))

    def state(self, st, val, path):
        # print "ResponseFrame state", st, val, path
        self.cleanup()
        if st != 'RESPONSE':
            return

        self.val = val
        self.name = os.path.basename(path[:-9])
        self.f = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.f, master=self.tframe)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.tframe.pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)

        if len(val.params) > 2:
            ax = Axes3D(self.f, azim=30.0, elev=30.0)
            ax.text2D(0.5, 0.5, 'Cannot plot response functions\nwith more than 2 parameters',
                      horizontalalignment='center',
                      verticalalignment='center',
                      transform=ax.transAxes)
        elif len(val.params) == 2:
            labels = CB.get('Labels')
            ax = Axes3D(self.f, azim=30.0, elev=30.0)
            val.plot(ax=ax, fig=self.f, title=0, labels=labels)
        else:
            self.a = self.f.add_subplot(111)
            self.a.grid(True)
            val.plot(fig=self.a)


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
        t = ttk.Treeview(self.parframe, yscrollcommand=scrollbar.set, height=len(val.params))
        t["columns"] = ("desc", "pdf")
        t.column("#0", width=75)
        t.column("desc", width=100)
        t.column("pdf", width=400)
        t.heading("#0", text='Name')
        t.heading("#1", text='Description')
        t.heading("#2", text='PDFXX')
        for p in val.params:
            cname = p.__class__.__name__[:-9]
            pdf_str = '%s [%s - %s] mean=%s dev=%s mode=%s' % (cname, p.pdf.range[0], p.pdf.range[1], p.pdf.mean, p.pdf.dev, p.pdf.mode)
            t.insert("", "end", text=p.name, values=[p.description, pdf_str])
        t.tag_configure("ttk")
        scrollbar.config(command=t.yview)
        t.pack(side=TOP, fill=BOTH, expand=YES)


class ParFrame2:
    def __init__(self, parent):
        self.parent = parent

    def cleanup(self):
        try:
            self.parframe.pack_forget()
        except:
            pass

    def state(self, st, val, path):
        self.cleanup()

        if st != 'D_PARLIST':
            return

        self.parframe = Frame(self.parent)
        self.parframe.pack(side=LEFT, fill=BOTH, expand=1)

        params = list(map(str, h5['/input/params'].keys()))

        # Parameters Table with scrollbar
        scrollbar = Scrollbar(self.parframe)
        scrollbar.pack(side=RIGHT, fill=Y)
        t = ttk.Treeview(self.parframe, yscrollcommand=scrollbar.set, height=len(params))
        t["columns"] = ("desc", "pdf")
        t.column("#0", width=75)
        t.column("desc", width=100)
        t.column("pdf", width=400)
        t.heading("#0", text='Name')
        t.heading("#1", text='Description')
        t.heading("#2", text='PDF')
        for pname in params:
            p = h5['/input/params/' + pname].value
            if type(p) == bytes and type(p) != str:
                p = p.decode('UTF-8')
            p = unpickle(p)
            cname = p.__class__.__name__[:-9]
            pdf_str = '%s [%s - %s] mean=%s dev=%s mode=%s' % (cname, p.pdf.range[0], p.pdf.range[1], p.pdf.mean, p.pdf.dev, p.pdf.mode)
            t.insert("", "end", text=p.name, values=[p.description, pdf_str])
        t.tag_configure("ttk")
        scrollbar.config(command=t.yview)
        t.pack(side=TOP, fill=BOTH, expand=YES)


class SurFrame:
    def __init__(self, parent):
        self.parent = parent

    def cleanup(self):
        try:
            self.surframe.pack_forget()
        except:
            pass

    def surf_changed(self, rbfunc=None):
        global modified
        #print "rbf changed to ", rbfunc
        #print self.val.rbf
        if rbfunc is not None:
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
                        MyApp.app.tree.item(ch, tags=['generate'])

        modified = True
        MyApp.state_changed('RESPONSE', self.val, self.path)

    def state(self, st, val, path):
        self.cleanup()
        if st != 'RESPONSE':
            return

        self.val = val
        self.path = path

        if isinstance(val, SampledFunc):
            self.surframe = LabelFrame(self.parent, text="Radial Basis Function")
            rbfvals = [
                "multiquadric",
                "linear",
                "cubic",
                "quintic",
                "inverse",
                "gaussian"
            ]
            self.rbf = MyCombobox(self.surframe, 'RBF', rbfvals, current=val.rbf, callback=self.surf_changed)
            if hasattr(self.val, 'eqn'):
                self.cbut = MyButton(self.surframe, text='Use Polynomials', cb=self.change)
                self.cbut.button.pack(side=RIGHT, anchor='e', padx=5, pady=5)
        else:
            self.surframe = LabelFrame(self.parent, text="Surface")

            # Surface Pane
            self.eqn = ScrolledText(self.surframe, height=2, )
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
            self.rmse.frame.pack(side=LEFT, anchor='w', padx=5, pady=5)
            self.cbut = MyButton(self.surframe, text='Use Radial Basis Functions', cb=self.change)
            self.cbut.button.pack(side=RIGHT, anchor='e', padx=5, pady=5)
        self.surframe.pack(side=LEFT, fill=BOTH, expand=1)

    def change(self):
        if isinstance(self.val, SampledFunc):
            self.val = self.val.to_response()
            self.cbut.update('Use Radial Basis Functions')
            self.surf_changed()
        else:
            self.val = self.val.to_sampled()
            self.cbut.update('Use Polynomials')
            self.surf_changed("multiquadric")


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
        #MyApp.state_changed()

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


class MyButton:
    def __init__(self, parent, text, cb):
        self.button = Button(parent, text=text, command=cb)

    def update(self, val):
        self.button['text'] = val


class MyApp:
    global root
    frames = []
    state = None
    val = None

    def __init__(self, parent, h5, errors):
        MyApp.app = weakref.proxy(self)
        self.parent = parent
        self.h5 = h5
        self.errors = errors
        parent.protocol('WM_DELETE_WINDOW', root.quit)

        tbar = Frame(parent)
        tbar.pack(side=TOP, anchor='w')

        # contains everything
        self.container = Frame(self.parent)
        self.container.pack(fill=BOTH, expand=YES)

        # top frame
        self.tframe = Frame(self.container)
        self.tframe.pack(side=TOP, fill=BOTH, expand=YES)

        # left frame. holds tree and plot options
        self.lframe = Frame(self.tframe, width=200, height=500)
        self.lframe.pack(side=LEFT, fill=BOTH)

        # right frame. holds plots or text descriptions
        self.rframe = Frame(self.tframe, width=500, height=500)
        self.rframe.pack(side=LEFT, fill=BOTH, expand=YES)

        # bottom frame. Holds parameters, etc
        self.bframe = Frame(self.container)

        # tree and scrollbar
        tframe = Frame(self.lframe)
        tframe.pack(side=TOP, fill=BOTH, expand=YES)
        scrollbar = Scrollbar(tframe)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree = ttk.Treeview(tframe, yscrollcommand=scrollbar.set)
        self.load_tree_widget()
        scrollbar.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self.tree_select)
        self.tree.pack(side=TOP, fill=BOTH, expand=YES)

        ### Frames which change based on state
        MyApp.frames = [
            PlotOption(self.lframe),
            InitFrame(self.rframe),
            BasicFrame(self.rframe),
            DataFrame(self.rframe),
            ResponseFrame(self.rframe),
            PdfFrame(self.rframe),
            ParameterFrame(self.rframe),
            ParFrame(self.bframe),
            ParFrame2(self.rframe),
            SurFrame(self.bframe),
            TextFrame(self.rframe),
            ProgressFrame(self.rframe),
            TimeFrame(self.rframe),
            StdoutFrame(self.rframe),
            MB(parent)
        ]
        MyApp.state_changed('D_INITIAL')

    def state_changed_method(self, st=None, val=None, path=None):
        if st != 'RESPONSE':
            try:
                self.bframe.pack_forget()
            except:
                pass
        else:
            self.bframe.pack(side=TOP, fill=BOTH, expand=NO)

    @staticmethod
    def cleanup():
        for f in MyApp.frames:
            try:
                f.cleanup()
            except:
                pass

    @staticmethod
    def state_changed(st=None, val=None, path=None):
        # Called when what is supposed to be displayed is changed.
        # val is the value of the object
        # path is a string with the hdf5 path of the object
        # print "MyApp state_changed %s - %s - %s" % (st, val, path)
        if st is None:
            st = MyApp.state
            val = MyApp.val
            path = MyApp.path
        else:
            MyApp.state = st
            MyApp.val = val
            MyApp.path = path
        for f in MyApp.frames:
            f.state(st, val, path)

    def analyze(self, job):
        h5 = self.h5
        p = re.compile('Command exited with non-zero status \d+')
        try:
            err = h5['output/jobs/%s/stderr' % job].value
        except:
            err = ''
        res = p.findall(err)
        if res:
            terr = 'error'
        else:
            terr = None

        results = False
        try:
            out = h5['output/jobs/%s/stdout' % job].value
        except:
            out = ''
        for line in out.split('\n'):
            if line.startswith('HDF5:{'):
                results = True
                break
        if results:
            tout = None
        else:
            tout = 'error'
        return tout, terr

    def load_tree_widget(self):
        t = self.tree
        h5 = self.h5

        t.tag_configure("generate", foreground='green')
        t.tag_configure("error", foreground='red')

        t.heading("#0", text='HDF5 Content')
        t.insert("", 0, iid='initial', text=h5.filename, values=['', 'D_INITIAL'])

        data_id = t.insert("", "end", iid='data', text='data', values=['', 'D_DATA'])
        err_id = t.insert(data_id, "end", text="stderr", values=['', 'D_STDOUT'])
        out_id = t.insert(data_id, "end", text="stdout", values=['', 'D_STDOUT'])

        keys = sorted(map(int, [x for x in h5['/output/jobs'].keys() if x.isdigit()]))
        self.errlist = []
        for j in keys:
            tout = None
            terr = None
            if self.errors:
                tout, terr = self.analyze(j)
                if tout or terr:
                    self.errlist.append(j)

            t.insert(out_id, "end", tags=[tout], text=j, values=["/output/jobs/%s/stdout" % j, "D_STDOUT"])
            t.insert(err_id, "end", tags=[terr], text=j, values=["/output/jobs/%s/stderr" % j, "D_STDOUT"])
        t.insert(data_id, "end", text='times', values=["/output/jobs/time", "TIME"])

        # params
        if '/input/params' in h5:
            par_id = t.insert("", "end", iid='params', text='parameters', values=["/input/params", 'D_PARLIST'])
            for p in h5['/input/params']:
                t.insert(par_id, "end", text=p, values=["/input/params/%s" % (p), 'PARAMETER'])

        # psweep results
        psweep = h5.attrs['UQtype']
        if type(psweep) != str:
            psweep = psweep.decode('UTF-8)')
        dir = '/' + psweep
        psweep_id = t.insert("", "end", iid='psweep', text=psweep, values=[dir, 'D_PSWEEP'])

        try:
            for d in h5[dir]:
                id = t.insert(psweep_id, "end", text=d, values=['%s/%s' % (dir, d), 'D_PSWEEP_VAR'])

                for d2 in h5['%s/%s' % (dir, d)]:
                    if d2 == 'samples':
                        continue
                    if d2 == 'pdf' and not 'samples' in h5['%s/%s' % (dir, d)]:
                        continue
                    t.insert(id, "end", text=d2, values=["%s/%s/%s" % (dir, d, d2), d2.upper()])

                if not 'pdf' in h5['%s/%s' % (dir, d)] or not 'samples' in h5['%s/%s' % (dir, d)]:
                    path = "%s/%s/pdf" % (dir, d)
                    t.insert(id, "end", tags=["generate"], text='pdf', values=[path, 'PDF'])
        except:
            pass
        t.tag_configure("ttk")

    def tree_select(self, event):
        global modified
        sel = event.widget.selection()
        # print("SEL=",sel)
        val, st = event.widget.item(sel)['values']
        tags = event.widget.item(sel)['tags']

        path = val
        # print('path=%s(%s)  st=%s(%s)' % (val, type(val), st, type(st)))

        if st.startswith("D_"):
            if st == 'D_STDOUT' and val == '':
                val = self.errlist
            else:
                val = None
        else:
            if 'generate' in tags:
                # print('generate val=%s, path=%s' % (val, path))
                dir = os.path.split(path)[0]
                rs = self.h5["%s/response" % dir].value
                if type(rs) != str:
                    rs = rs.decode('UTF-8)')
                rs = unpickle(rs)

                MyApp.state_changed('PROGRESS', val)
                root.update()
                if 'psamples' in self.h5:
                    psamples = self.h5['psamples'].value
                else:
                    psamples = None
                val, samples = rs.pdf(fit=False, return_samples=True, psamples=psamples)
                if path in self.h5:
                    del self.h5[path]
                self.h5[path] = pickle(val)
                self.h5['%s/samples' % dir] = samples
                self.h5[path].attrs['fit'] = 'Linear'
                modified = True
                event.widget.item(sel, tags=[])
            else:
                val = self.h5[val].value
                if type(val) == bytes and type(val) != str:
                    val = val.decode('UTF-8')

                try:
                    val = unpickle(val)
                except:
                    pass

        MyApp.state_changed(st, val, path)
        self.state_changed_method(st, val, path)


def analyzer(sw, errors):
    global h5, root, modified, filename, fname_orig, sweep

    sweep = sw
    fname = sweep.fname + '.hdf5'
    fname_orig = fname + '_orig'
    os.rename(fname, fname_orig)
    shutil.copy(fname_orig, fname)
    atexit.register(cleanup_and_exit, False)

    filename = fname

    h5 = h5py.File(filename)
    modified = False

    update_prefs()

    root = Tk()
    MyApp(root, h5, errors)
    root.title("PUQ Results: %s" % filename)
    root.protocol("WM_DELETE_WINDOW", ask_quit)

    # stop the window resizing insanity
    root.update()
    root.geometry(root.geometry())

    root.mainloop()
