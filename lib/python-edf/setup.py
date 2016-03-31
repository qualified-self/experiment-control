from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import sys
if sys.platform == 'win32':
    # could just import numpy and use that as base library
    include_dirs=['src', r"c:/Python26/Lib/site-packages/numpy/core/include"]
    define=['-D_CRT_SECURE_NO_WARNINGS']
else:
    include_dirs=['src',"edflib"]
    define=[]
    
# ext_modules_edf = [Extension("edf", ["edf.pyx", "edflib.c"],
#                          library_dirs=['.'],
#                          include_dirs=include_dirs,
#                          )]

ext_modules_edflib = [Extension("edflib._edflib", ["edflib/_edflib.pyx", "src/edflib.c"],
                         library_dirs=['src'],
                         include_dirs=include_dirs,
#                         define=define,
                         )]               

setup(
    name = 'python-edf',
    version='0.3',
    description="""python-edf is a python package ot allow access to European Data Format files (EDF for short). This is a standard for biological signals such as EEG, evoked potentials and EMG.  This module wraps Teunis van Beelen's edflib.""",
    author="""Chris Lee-Messer""",
    url="http://bitbucket.org/cleemesser/python-edf",
    download_url="http://bitbucket.org/cleemesser/python-edf/downloads",
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules_edflib,
    packages=["edflib"],
    classifiers=['Topic :: Science :: EEG'],
    package_data={'edflib' : ['_edflib.so']},
    # data_files=[],
    # scripts = [],
    )
