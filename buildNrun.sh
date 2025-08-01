#!/bin/bash

# Build
g++ -std=c++17 -I. -o pyclib_app pyclib/main.cpp pyclib/pyclib.cpp

# Run
./pyclib_app