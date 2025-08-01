#include <pyclib/pyclib.h>

int main()
{
    PyObject a = PyObject::from_string("ha");
    PyObject b = PyObject::from_int(3);

    PyObject c = py_mul(a, b); // "hahaha"
    py_print(c);
    std::cout << "\n";
    std::cout << "sdfsdf";

    PyObject list = PyObject::from_list({b});
    PyObject d = py_mul(list, PyObject::from_int(2)); // [3, 3]
    py_print(d);
    std::cout << "\n";

    PyObject sum = py_add(PyObject::from_int(10), PyObject::from_float(2.5));
    py_print(sum);
    std::cout << "\n";

    py_add(PyObject::from_int(1), PyObject::from_string("x"));

    return 0;
}
