#pragma once

#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>
#include <iostream>

struct PyObject;

enum class PyType
{
    STR,
    INT,
    FLOAT,
    COMPLEX,
    LIST,
    TUPLE,
    RANGE,
    DICT,
    SET,
    FROZENSET,
    BOOL,
    BYTES,
    BYTEARRAY,
    MEMORYVIEW,
    NONE
};

struct PyObject
{
    PyType type;
    uint64_t raw;

    PyObject(PyType t, uint64_t value);

    static PyObject from_int(int64_t v);
    static PyObject from_float(double v);
    static PyObject from_bool(bool v);
    static PyObject from_string(const std::string &s);
    static PyObject from_list(const std::vector<PyObject> &v);
    static PyObject from_dict(const std::unordered_map<std::string, PyObject> &d);

    PyObject(const PyObject &other);
    ~PyObject();
};

void py_print(const PyObject &obj);

PyObject py_add(const PyObject &a, const PyObject &b);
PyObject py_mul(const PyObject &a, const PyObject &b);
