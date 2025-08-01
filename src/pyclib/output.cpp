#include "pyclib.h"

int main() {
    PyObject x = PyObject::from_int(10);
    PyObject y = PyObject::from_int(3);
    PyObject z = py_add(x, y);
    py_print(z); 
 std::cout << "\n";;
    return 0;
}
