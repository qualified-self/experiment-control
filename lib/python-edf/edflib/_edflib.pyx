cimport cpython
import numpy as np
cimport numpy as np

include "edf.pxi"

open_errors = {
    EDFLIB_MALLOC_ERROR : "malloc error",                                                
    EDFLIB_NO_SUCH_FILE_OR_DIRECTORY   : "can not open file, no such file or directory",
    EDFLIB_FILE_CONTAINS_FORMAT_ERRORS : "the file is not EDF(+) or BDF(+) compliant (it contains format errors)",
    EDFLIB_MAXFILES_REACHED            : "to many files opened",
    EDFLIB_FILE_READ_ERROR             : "a read error occurred",
    EDFLIB_FILE_ALREADY_OPENED         : "file has already been opened",
    'default' : "unknown error"
    }

# constants are redeclared here so we can access them from Python
FILETYPE_EDF = EDFLIB_FILETYPE_EDF
FILETYPE_EDFPLUS = EDFLIB_FILETYPE_EDFPLUS
FILETYPE_BDF = EDFLIB_FILETYPE_BDF
FILETYPE_BDFPLUS = EDFLIB_FILETYPE_BDFPLUS
                                                
def check_open_ok(result):
    if result == 0:
        return True
    else:
        raise IOError, open_errors[result]
        return False


def lib_version():
    return edflib_version()

cdef class Edfreader:
    """
    This provides a simple interface to read EDF, EDF+, and probably is ok with
    BDF and BDF+ files
    Note that edflib.c is encapsulated so there is no direct access to the file
    from here unless I add a raw interface or something
    
    """
    cdef int handle
    cdef edf_hdr_struct hdr
    cdef size_t nsamples_per_record
    #
    def __init__(self, file_name, annotations_mode='all'):
        self.open(file_name, mode='r', annotations_mode='all')

    def make_buffer(self):
        """make a buffer that can hold a single datarecord, might extend
        to provide for N datarecord size"""
        print "self.hdr.datarecords_in_file", self.hdr.datarecords_in_file
        tmp =0
        for ii in range(self.signals_in_file):
            tmp += self.samples_in_datarecord(ii)
        self.nsamples_per_record = tmp # assume 16-bit? or check first?
        dbuffer = np.zeros(tmp, dtype='float64')
        return dbuffer
    
    def open(self, file_name, mode='r', annotations_mode='all'):
        result = edfopen_file_readonly(file_name, &self.hdr, EDFLIB_READ_ALL_ANNOTATIONS)
        return check_open_ok(result)


    property handle:
        "edflib internal int handle"
        def __get__(self):
            return self.handle
        
    property datarecords_in_file:
        "number of data records"
        def __get__(self):
            return self.hdr.datarecords_in_file

    property signals_in_file:
        def __get__(self):
            return self.hdr.edfsignals

    property file_duration:
        "file duration in seconds"
        def __get__(self):
            return self.hdr.file_duration/EDFLIB_TIME_DIMENSION

    property patient:
        "patient name?"
        def __get__(self):
            return self.hdr.patient

    property datarecord_duration:
        def __get__(self):
            return (<double>self.hdr.datarecord_duration) / EDFLIB_TIME_DIMENSION

    property annotations_in_file:
        def __get__(self):
            return self.hdr.annotations_in_file

    # signal parameters
    def signal_label(self, channel):
        return self.hdr.signalparam[channel].label

    def samples_in_file(self,channel):
        return self.hdr.signalparam[channel].smp_in_file

    def samples_in_datarecord(self, channel):
        return self.hdr.signalparam[channel].smp_in_datarecord

    def physical_max(self, channel):
        return self.hdr.signalparam[channel].phys_max

    def physical_min(self, channel):
        return self.hdr.signalparam[channel].phys_min

    def digital_max(self, channel):
        return self.hdr.signalparam[channel].dig_max    

    def digital_min(self, channel):
        return self.hdr.signalparam[channel].dig_min

    def samplefrequency(self, channel):
        return (<double>self.hdr.signalparam[channel].smp_in_datarecord / self.hdr.datarecord_duration) * EDFLIB_TIME_DIMENSION

    def _tryoffset(self):
        """
        fooling around to find offset in file to allow shortcut mmap interface
        """
        # cdef long offset = self.hdr.hdrsize  # from edflib.c read_physical_samples()
        print "trying to find data offset in file"
        nrecords = self.hdr.datarecords_in_file
        print "nrecords in file:", nrecords
        return 1,2
        # return offset, nrecords
        # print "offset via edftell:",  edftell(self.hdr.handle, 0)
        

    def close(self):
        edfclose_file(self.hdr.handle)
        
    def readsignal(self, signalnum, start, n, np.ndarray[np.float64_t, ndim=1] sigbuf):

        """read @n number of samples from signal number @signum starting at
        @start into numpy float64 array @sigbuf sigbuf must be at least n long
        """
        
        edfseek(self.hdr.handle, signalnum, start, EDFSEEK_SET)
        readn = edfread_physical_samples(self.hdr.handle, signalnum, n, <double*>sigbuf.data)
        # print "read %d samples" % readn
        if readn != n:
            print "read %d, less than %d requested!!!" % (readn, n)
        
    def load_datarecord(self, np.ndarray[np.float64_t, ndim=1] db, n=0):
        cdef size_t offset =0

        if n < self.hdr.datarecords_in_file:
            for ii in range(self.signals_in_file):
                edfseek(self.hdr.handle, ii, n*self.samples_in_datarecord(ii), EDFSEEK_SET) # just a guess
                readn = edfread_physical_samples(self.hdr.handle, ii, self.samples_in_datarecord(ii),
                                                 (<double*>db.data)+offset)
                print "readn this many samples", readn
                offset += self.samples_in_datarecord(ii)


###############################    
# low level functions

def set_patientcode(int handle, char *patientcode):
    # check if rw?
    return edf_set_patientcode(handle, patientcode)

    

cpdef int write_annotation_latin1(int handle, long long onset, long long duration, char *description):
        return edfwrite_annotation_latin1(handle, onset, duration, description)


cpdef int set_technician(int handle, char *technician):
    return edf_set_technician(handle, technician)

cdef class EdfAnnotation:
    cdef edf_annotation_struct annotation


cpdef int get_annotation(int handle, int n, EdfAnnotation edf_annotation):
    return edf_get_annotation(handle, n, &(edf_annotation.annotation))

# need to use npbuffers
cpdef read_int_samples(int handle, int edfsignal, int n,
                         np.ndarray[np.int32_t,ndim=1] buf):
    """
/* reads n samples from edfsignal, starting from the current sample position indicator, into buf (edfsignal starts at 0) */
/* the values are the "raw" digital values */
/* bufsize should be equal to or bigger than sizeof(int[n]) */
/* the sample position indicator will be increased with the amount of samples read */
/* returns the amount of samples read (this can be less than n or zero!) */
/* or -1 in case of an error */


    ToDO!!!
    assert that these are stored as EDF/EDF+ files with int16 sized samples
    returns how many were actually read
    doesn't currently check that buf can hold all the data
    """
    return edfread_digital_samples(handle, edfsignal, n,<int*>buf.data)

cpdef int blockwrite_digital_samples(int handle, np.ndarray[np.int16_t,ndim=1] buf):
    return edf_blockwrite_digital_samples(handle, <int*>buf.data)

cpdef int blockwrite_physical_samples(int handle, np.ndarray[np.float64_t,ndim=1] buf):
    return edf_blockwrite_physical_samples(handle, <double*>buf.data)

cpdef int set_recording_additional(int handle, char *recording_additional):
    return edf_set_recording_additional(handle,recording_additional)

cpdef int write_physical_samples(int handle, np.ndarray[np.float64_t] buf):
    return edfwrite_physical_samples(handle, <double *>buf.data)

    # int edfwrite_annotation_utf8(int, long long int, long long int, char *)

cpdef int set_patientname(int handle, char *name):
    return edf_set_patientname(handle, name)

cpdef int set_physical_minimum(int handle, int edfsignal, double phys_min):
    edf_set_physical_minimum(handle, edfsignal, phys_min)

cpdef int read_physical_samples(int handle, int edfsignal, int n,
                                np.ndarray[np.float64_t] buf):
    return edfread_physical_samples(handle, edfsignal, n, <double *>buf.data)

def close_file(handle):
    return edfclose_file(handle)

# so you can use the same name if defining a python only function
def set_physical_maximum(handle, edfsignal, phys_max):
    return edf_set_physical_maximum(handle, edfsignal, phys_max)

def open_file_writeonly(path, filetype, number_of_signals):
    """int edfopen_file_writeonly(char *path, int filetype, int number_of_signals)"""
    return edfopen_file_writeonly(path, filetype, number_of_signals)
    
def set_patient_additional(handle, patient_additional):
    """int edf_set_patient_additional(int handle, const char *patient_additional)"""
    return edf_set_patient_additional(handle, patient_additional)

def set_digital_maximum(handle, edfsignal, dig_max):
    "int edf_set_digital_maximum(int handle, int edfsignal, int dig_max)"
    return edf_set_digital_maximum(handle, edfsignal, dig_max)

        
# see Edfreader() class
# int edfopen_file_readonly(const char *path, struct edf_hdr_struct *edfhdr, int read_annotations)

def set_birthdate(handle, birthdate_year, birthdate_month, birthdate_day):
    """int edf_set_birthdate(int handle, int birthdate_year, int birthdate_month, int birthdate_day)"""
    return edf_set_birthdate(handle, birthdate_year,  birthdate_month, birthdate_day)

def set_digital_minimum(handle, edfsignal, dig_min):
    """int edf_set_digital_minimum(int handle, int edfsignal, int dig_min)"""
    return edf_set_digital_minimum(handle,  edfsignal, dig_min)

def write_digital_samples(handle, np.ndarray[np.int16_t] buf):
    """write_digital_samples(int handle, np.ndarray[np.int16_t] buf)"""
    return edfwrite_digital_samples(handle, <int*>buf.data)

def set_equipment(handle, equipment):
    """int edf_set_equipment(int handle, const char *equipment)"""
    return edf_set_equipment(handle, equipment)

def set_samplefrequency(handle, edfsignal, samplefrequency):
    """int edf_set_samplefrequency(int handle, int edfsignal, int samplefrequency)"""
    return edf_set_samplefrequency(handle, edfsignal, samplefrequency)

def set_admincode(handle, admincode):
    """int edf_set_admincode(int handle, const char *admincode)"""
    return edf_set_admincode(handle, admincode)

def set_label(handle, edfsignal, label):
    """int edf_set_label(int handle, int edfsignal, const char *label)"""
    return edf_set_label(handle, edfsignal, label)


#FIXME need to make sure this gives the proper values for large values
def tell(handle, edfsignal):
    """long long edftell(int handle, int edfsignal)"""
    return edftell(handle,  edfsignal)

def rewind(handle, edfsignal):
    """void edfrewind(int handle, int edfsignal)"""
    edfrewind(handle, edfsignal)
    
def set_gender(handle, gender):
    """int edf_set_gender(int handle, int gender)"""
    return edf_set_gender(handle, gender)

def set_physical_dimension(handle, edfsignal, phys_dim):
    """int edf_set_physical_dimension(int handle, int edfsignal, const char *phys_dim)"""
    return edf_set_physical_dimension(handle, edfsignal, phys_dim)

def set_transducer(handle, edfsignal, transducer):
    """int edf_set_transducer(int handle, int edfsignal, const char *transducer)"""
    return edf_set_transducer(handle, edfsignal, transducer)

def set_prefilter(handle, edfsignal, prefilter):
    """int edf_set_prefilter(int handle, int edfsignal, const char*prefilter)"""
    return edf_set_prefilter(handle, edfsignal, prefilter)

def seek(handle, edfsignal, offset, whence):
    """long long edfseek(int handle, int edfsignal, long long offset, int whence)"""
    return edfseek(handle, edfsignal, offset, whence)

def set_startdatetime(handle, startdate_year, startdate_month, startdate_day,
                          starttime_hour, starttime_minute, starttime_second):
    """int edf_set_startdatetime(int handle, int startdate_year, int startdate_month, int startdate_day,
                                      int starttime_hour, int starttime_minute, int starttime_second)"""
    return edf_set_startdatetime(handle, startdate_year, startdate_month, startdate_day,
                                 starttime_hour, starttime_minute, starttime_second)


def set_datarecord_duration(handle, duration):
    """int edf_set_datarecord_duration(int handle, int duration)"""
    return edf_set_datarecord_duration(handle, duration)

## old test function ###


def test1_edfopen():
    print "hi"
    # based upon main.c
    cdef:
        int i, hdl, channel, n
        double *buf
        edf_hdr_struct hdr
        np.ndarray[np.float64_t, ndim=1] carr 
        
    result = edfopen_file_readonly("test_generator.edf", &hdr, EDFLIB_READ_ALL_ANNOTATIONS)
    print "result:", result
    check_open_ok(result)
    hdl = hdr.handle
    print "hdr.edfsignals", hdr.edfsignals

    print "edflib_version:", edflib_version()
    print "hdr.filetype", hdr.filetype
    print "hdr.file_duration / EDFLIB_TIME_DIMENSION", hdr.file_duration / EDFLIB_TIME_DIMENSION
    print hdr.startdate_day, hdr.startdate_month, hdr.startdate_year
    print hdr.recording
    print "hdr.datarecords_in_file", hdr.datarecords_in_file
    print "hdr.annotations_in_file", hdr.annotations_in_file

    array_list = []
    N = 200
    for channel in range(hdr.edfsignals):
        print channel
        print "hdr.signalparam[channel].label",hdr.signalparam[channel].label
        print "hdr.signalparam[channel].smp_in_file", hdr.signalparam[channel].smp_in_file
        print "hdr.signalparam[channel].smp_in_datarecord / <double>hdr.datarecord_duration) * EDFLIB_TIME_DIMENSION", (hdr.signalparam[channel].smp_in_datarecord / <double>hdr.datarecord_duration) * EDFLIB_TIME_DIMENSION

        #print "annot.onset / EDFLIB_TIME_DIMENSION",annot.onset / EDFLIB_TIME_DIMENSION,
        # print "annot.duration", annot.duration,

        x = 10 # start reading x seconds from start
        edfseek(hdl, channel, <long long>(((<double>x) / (<double>hdr.file_duration / <double>EDFLIB_TIME_DIMENSION)) * (<double>hdr.signalparam[channel].smp_in_file)), EDFSEEK_SET)

        n = N
        print "data[%d]:" % N
        arr = np.zeros(N, dtype='float64')
        carr = arr
        n = edfread_physical_samples(hdl, channel, n, <double*>carr.data);
        #arr = carr.copy() # hmm
        array_list.append(arr)
        print carr
    return array_list
