#!/usr/bin/env python
import numpy as np
import _edflib
from EdfWriter import EdfWriter

class EDF(object):
    def __init__(self, file_name):
        self.edf = _edflib.Edfreader(file_name)
        self.file_name = file_name
        edf = self.edf
        self.signal_labels = []
        self.signal_nsamples = []
        self.samplefreqs = []
        self.signals_in_file = edf.signals_in_file
        self.datarecords_in_file = edf.datarecords_in_file
        for ii in xrange(self.signals_in_file):
            self.signal_labels.append(edf.signal_label(ii))
            self.signal_nsamples.append(edf.samples_in_file(ii))
            self.samplefreqs.append(edf.samplefrequency(ii))

    def file_info(self):
        print "file name:", self.file_name
        print "signals in file:", self.signals_in_file

    def file_info_long(self):
        self.file_info()
        for ii in xrange(self.signals_in_file):
            print "label:", self.signal_labels[ii], "fs:", self.samplefreqs[ii], "nsamples", self.signal_nsamples[ii]
