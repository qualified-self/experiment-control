#!/bin/sh
gcc main.c edflib.c -Wall -O2 -o test_edflib
gcc sine.c edflib.c -Wall -O2 -lm -o sine
gcc test_generator.c edflib.c -Wall -O2 -lm -o testgenerator
gcc sweep.c edflib.c -Wall -O2 -lm -o sweep
