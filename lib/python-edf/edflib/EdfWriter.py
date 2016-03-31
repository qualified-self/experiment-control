import numpy as np
import _edflib as edf

class EdfWriter(object):
    def __init__(self, file_name, channel_info, file_type=edf.FILETYPE_EDFPLUS):
        '''Initialises an EDF file at @file_name. 
        @file_type is one of 
            edflib.FILETYPE_EDF
            edflib.FILETYPE_EDFPLUS
            edflib.FILETYPE_BDF
            edflib.FILETYPE_BDFPLUS

        @channel_info should be a 
        list of dicts, one for each channel in the data. Each dict needs 
        these values:
            
            'label' : channel label (string, <= 16 characters, must be unique)
            'dimension' : physical dimension (e.g., mV) (string, <= 8 characters)
            'sample_rate' : sample frequency in hertz (int)
            'physical_max' : maximum physical value (float)
            'physical_min' : minimum physical value (float)
            'digital_max' : maximum digital value (int, -2**15 <= x < 2**15)
            'digital_min' : minimum digital value (int, -2**15 <= x < 2**15)
        '''
        self.path = file_name
        self.file_type = file_type
        self.n_channels = len(channel_info)
        self.channels = {}
        for c in channel_info:
            if c['label'] in self.channels:
                raise ChannelLabelExists(c['label'])
            self.channels[c['label']] = c
        self.sample_buffer = dict([(c['label'],[]) for c in channel_info])
        self.handle = edf.open_file_writeonly(file_name, file_type, self.n_channels)
        self._init_channels(channel_info)

    def write_sample(self, channel_label, sample):
        '''Queues a digital sample for @channel_label for recording; the data won't 
        actually be written until one second's worth of data has been queued.'''
        if channel_label not in self.channels:
            raise ChannelDoesNotExist(channel_label)
        self.sample_buffer[channel_label].append(sample)
        if len(self.sample_buffer[channel_label]) == self.channels[channel_label]['sample_rate']:
            self._flush_samples()

    def close(self):
        edf.close_file(self.handle)

    def _init_channels(self, channels):
        hdl = self.handle
        for i,c in enumerate(channels):
            edf.set_samplefrequency(hdl, i, c['sample_rate'])
        for i,c in enumerate(channels):
            edf.set_physical_maximum(hdl, i, c['physical_max'])
        for i,c in enumerate(channels):
            edf.set_digital_maximum(hdl, i, c['physical_max'])
        for i,c in enumerate(channels):
            edf.set_digital_minimum(hdl, i, c['digital_min'])
        for i,c in enumerate(channels):
            edf.set_physical_minimum(hdl, i, c['physical_min'])
        for i,c in enumerate(channels):
            edf.set_label(hdl, i, c['label'])
        for i,c in enumerate(channels):
            edf.set_physical_dimension(hdl, i, c['dimension'])

    def _flush_samples(self):
        for c in self.channels: 
            buf = np.array(self.sample_buffer[c], dtype='int16')
            edf.write_digital_samples(self.handle, buf)
            self.sample_buffer[c] = []

