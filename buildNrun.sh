#!/bin/bash

# Build
g++ -std=c++17 -I. -o pyclib_app pyclib/output.cpp pyclib/pyclib.cpp

# Run
./pyclib_app