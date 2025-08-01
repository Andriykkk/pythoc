#!/bin/bash

# Build
g++ -std=c++17 -I. -o pyclib_app src/pyclib/output.cpp src/pyclib/pyclib.cpp

# Run
./pyclib_app