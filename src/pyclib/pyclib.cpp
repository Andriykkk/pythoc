#include "pyclib.h"
#include <stdexcept>
#include <cstring>

PyObject::PyObject(PyType t, uint64_t value) : type(t), raw(value) {}

PyObject PyObject::from_int(int64_t v)
{
    return PyObject(PyType::INT, static_cast<uint64_t>(v));
}

PyObject PyObject::from_float(double v)
{
    uint64_t bits;
    std::memcpy(&bits, &v, sizeof(double));
    return PyObject(PyType::FLOAT, bits);
}

PyObject PyObject::from_bool(bool v)
{
    return PyObject(PyType::BOOL, v ? 1 : 0);
}

PyObject PyObject::from_string(const std::string &s)
{
    return PyObject(PyType::STR, reinterpret_cast<uint64_t>(new std::string(s)));
}

PyObject PyObject::from_list(const std::vector<PyObject> &v)
{
    return PyObject(PyType::LIST, reinterpret_cast<uint64_t>(new std::vector<PyObject>(v)));
}

PyObject PyObject::from_dict(const std::unordered_map<std::string, PyObject> &d)
{
    return PyObject(PyType::DICT, reinterpret_cast<uint64_t>(new std::unordered_map<std::string, PyObject>(d)));
}

PyObject::PyObject(const PyObject &other)
{
    type = other.type;
    switch (type)
    {
    case PyType::STR:
        raw = reinterpret_cast<uint64_t>(new std::string(*reinterpret_cast<std::string *>(other.raw)));
        break;
    case PyType::LIST:
        raw = reinterpret_cast<uint64_t>(new std::vector<PyObject>(*reinterpret_cast<std::vector<PyObject> *>(other.raw)));
        break;
    case PyType::DICT:
        raw = reinterpret_cast<uint64_t>(new std::unordered_map<std::string, PyObject>(*reinterpret_cast<std::unordered_map<std::string, PyObject> *>(other.raw)));
        break;
    default:
        raw = other.raw;
        break;
    }
}

PyObject::~PyObject()
{
    switch (type)
    {
    case PyType::STR:
        delete reinterpret_cast<std::string *>(raw);
        break;
    case PyType::LIST:
        delete reinterpret_cast<std::vector<PyObject> *>(raw);
        break;
    case PyType::DICT:
        delete reinterpret_cast<std::unordered_map<std::string, PyObject> *>(raw);
        break;
    default:
        break;
    }
}

void py_print(const PyObject &obj)
{
    switch (obj.type)
    {
    case PyType::INT:
        std::cout << static_cast<int64_t>(obj.raw);
        break;
    case PyType::FLOAT:
    {
        double v;
        std::memcpy(&v, &obj.raw, sizeof(double));
        std::cout << v;
        break;
    }
    case PyType::BOOL:
        std::cout << (obj.raw ? "True" : "False");
        break;
    case PyType::STR:
        std::cout << *reinterpret_cast<std::string *>(obj.raw);
        break;
    case PyType::LIST:
    {
        std::cout << "[";
        auto vec = reinterpret_cast<std::vector<PyObject> *>(obj.raw);
        for (size_t i = 0; i < vec->size(); ++i)
        {
            py_print((*vec)[i]);
            if (i + 1 < vec->size())
                std::cout << ", ";
        }
        std::cout << "]";
        break;
    }
    case PyType::DICT:
    {
        std::cout << "{";
        auto map = reinterpret_cast<std::unordered_map<std::string, PyObject> *>(obj.raw);
        size_t i = 0;
        for (const auto &[key, val] : *map)
        {
            std::cout << "'" << key << "': ";
            py_print(val);
            if (++i < map->size())
                std::cout << ", ";
        }
        std::cout << "}";
        break;
    }
    default:
        std::cout << "None";
    }
}

void py_print_type(const PyObject &obj)
{
    switch (obj.type)
    {
    case PyType::INT:
        std::cout << "int";
        break;
    case PyType::FLOAT:
        std::cout << "float";
        break;
    case PyType::BOOL:
        std::cout << "bool";
        break;
    case PyType::STR:
        std::cout << "str";
        break;
    case PyType::LIST:
        std::cout << "list";
        break;
    case PyType::DICT:
        std::cout << "dict";
        break;
    default:
        std::cout << "None";
    }
}

std::string py_get_type(const PyObject &obj)
{
    switch (obj.type)
    {
    case PyType::INT:
        return "int";
    case PyType::FLOAT:
        return "float";
    case PyType::BOOL:
        return "bool";
    case PyType::STR:
        return "str";
    case PyType::LIST:
        return "list";
    case PyType::DICT:
        return "dict";
    default:
        return "None";
    }
}

// TODO: add other operations
// TODO: make infinite integers
// TODO: PyObject py_sub(const PyObject &a, const PyObject &b);
// TODO: PyObject py_div(const PyObject &a, const PyObject &b);
// TODO: PyObject py_mod(const PyObject &a, const PyObject &b);
// TODO: PyObject py_pow(const PyObject &a, const PyObject &b);
// TODO: PyObject py_eq(const PyObject &a, const PyObject &b);
// TODO: PyObject py_neq(const PyObject &a, const PyObject &b);
// TODO: PyObject py_lt(const PyObject &a, const PyObject &b);
// TODO: PyObject py_gt(const PyObject &a, const PyObject &b);
// TODO: PyObject py_le(const PyObject &a, const PyObject &b);
// TODO: PyObject py_ge(const PyObject &a, const PyObject &b);
// TODO: PyObject py_and(const PyObject &a, const PyObject &b);
// TODO: PyObject py_or(const PyObject &a, const PyObject &b);
// TODO: PyObject py_not(const PyObject &a);
// TODO: PyObject py_xor(const PyObject &a, const PyObject &b);
// TODO: PyObject py_lshift(const PyObject &a, const PyObject &b);
// TODO: PyObject py_rshift(const PyObject &a, const PyObject &b);
// TODO: PyObject py_invert(const PyObject &a);
// TODO: PyObject py_neg(const PyObject &a);
// TODO: PyObject py_pos(const PyObject &a);
// TODO: PyObject py_call(const PyObject &func, const std::vector<PyObject> &args);
// TODO: PyObject py_getattr(const PyObject &obj, const std::string &name);
// TODO: PyObject py_setattr(const PyObject &obj, const std::string &name, const PyObject &value);
// TODO: PyObject py_getitem(const PyObject &obj, const PyObject &key);
// TODO: PyObject py_setitem(const PyObject &obj, const PyObject &key, const PyObject &value);
// TODO: PyObject py_len(const PyObject &obj);
// TODO: PyObject py_iter(const PyObject &obj);
// TODO: PyObject py_next(const PyObject &obj);
// TODO: PyObject py_contains(const PyObject &obj, const PyObject &item);
// TODO: PyObject py_str(const PyObject &obj);
// TODO: PyObject py_repr(const PyObject &obj);
// TODO: PyObject py_type(const PyObject &obj);
// TODO: PyObject py_is(const PyObject &a, const PyObject &b);
// TODO: PyObject py_is_not(const PyObject &a, const PyObject &b);
// TODO: PyObject py_in(const PyObject &item, const PyObject &container);
// TODO: PyObject py_not_in(const PyObject &item, const PyObject &container);
// TODO: PyObject py_import(const std::string &name);
// TODO: PyObject py_reload(const PyObject &module);
// TODO: PyObject py_eval(const std::string &code, const PyObject &globals, const PyObject &locals);
// TODO: PyObject py_exec(const std::string &code, const PyObject &globals, const PyObject &locals);
// TODO: PyObject py_compile(const std::string &code, const std::string &filename, const std::string &mode);
// TODO: PyObject py_dir(const PyObject &obj);
// TODO: PyObject py_vars(const PyObject &obj);
// TODO: PyObject py_globals();
// TODO: PyObject py_locals();
// TODO: PyObject py_abs(const PyObject &obj);
// TODO: PyObject py_all(const PyObject &obj);
// TODO: PyObject py_any(const PyObject &obj);
// TODO: PyObject py_ascii(const PyObject &obj);
// TODO: PyObject py_bin(const PyObject &obj);
// TODO: PyObject py_bool(const PyObject &obj);
// TODO: PyObject py_bytearray(const PyObject &obj);
// TODO: PyObject py_bytes(const PyObject &obj);
// TODO: PyObject py_callable(const PyObject &obj);
// TODO: PyObject py_chr(const PyObject &obj);
// TODO: PyObject py_classmethod(const PyObject &obj);
// TODO: PyObject py_complex(const PyObject &obj);
// TODO: PyObject py_delattr(const PyObject &obj, const std::string &name);
// TODO: PyObject py_dict(const PyObject &obj);
// TODO: PyObject py_divmod(const PyObject &a, const PyObject &b);
// TODO: PyObject py_enumerate(const PyObject &obj, const PyObject &start);
// TODO: PyObject py_filter(const PyObject &func, const PyObject &iterable);
// TODO: PyObject py_float(const PyObject &obj);
// TODO: PyObject py_format(const PyObject &obj, const std::string &format_spec);
// TODO: PyObject py_frozenset(const PyObject &obj);
// TODO: PyObject py_hasattr(const PyObject &obj, const std::string &name);
// TODO: PyObject py_hash(const PyObject &obj);
// TODO: PyObject py_help(const PyObject &obj);
// TODO: PyObject py_hex(const PyObject &obj);
// TODO: PyObject py_id(const PyObject &obj);
// TODO: PyObject py_input(const PyObject &prompt);
// TODO: PyObject py_int(const PyObject &obj);
// TODO: PyObject py_isinstance(const PyObject &obj, const PyObject &classinfo);
// TODO: PyObject py_issubclass(const PyObject &cls, const PyObject &classinfo);
// TODO: PyObject py_iter(const PyObject &obj);
// TODO: PyObject py_len(const PyObject &obj);
// TODO: PyObject py_list(const PyObject &obj);
// TODO: PyObject py_map(const PyObject &func, const PyObject &iterables);
// TODO: PyObject py_max(const PyObject &obj);
// TODO: PyObject py_memoryview(const PyObject &obj);
// TODO: PyObject py_min(const PyObject &obj);
// TODO: PyObject py_next(const PyObject &obj);
// TODO: PyObject py_object();
// TODO: PyObject py_oct(const PyObject &obj);
// TODO: PyObject py_open(const PyObject &file, const PyObject &mode, const PyObject &buffering, const PyObject &encoding, const PyObject &errors, const PyObject &newline, const PyObject &closefd, const PyObject &opener);
// TODO: PyObject py_ord(const PyObject &obj);
// TODO: PyObject py_pow(const PyObject &base, const PyObject &exp, const PyObject &mod);
// TODO: PyObject py_print(const PyObject &obj, const PyObject &sep, const PyObject &end, const PyObject &file, const PyObject &flush);
// TODO: PyObject py_property(const PyObject &fget, const PyObject &fset, const PyObject &fdel, const PyObject &doc);
// TODO: PyObject py_range(const PyObject &start, const PyObject &stop, const PyObject &step);
// TODO: PyObject py_repr(const PyObject &obj);
// TODO: PyObject py_reversed(const PyObject &obj);
// TODO: PyObject py_round(const PyObject &number, const PyObject &ndigits);
// TODO: PyObject py_set(const PyObject &obj);
// TODO: PyObject py_setattr(const PyObject &obj, const std::string &name, const PyObject &value);
// TODO: PyObject py_slice(const PyObject &start, const PyObject &stop, const PyObject &step);
// TODO: PyObject py_sorted(const PyObject &iterable, const PyObject &key, const PyObject &reverse);
// TODO: PyObject py_staticmethod(const PyObject &obj);
// TODO: PyObject py_str(const PyObject &obj);
// TODO: PyObject py_sum(const PyObject &iterable, const PyObject &start);
// TODO: PyObject py_super(const PyObject &type, const PyObject &obj);
// TODO: PyObject py_tuple(const PyObject &obj);
// TODO: PyObject py_type(const PyObject &obj);
// TODO: PyObject py_vars(const PyObject &obj);
// TODO: PyObject py_zip(const PyObject &iterables);
// TODO: PyObject py_import(const PyObject &name, const PyObject &globals, const PyObject &locals, const PyObject &fromlist, const PyObject &level);
// TODO: PyObject py_breakpoint();
// TODO: PyObject py_build_class(const PyObject &func, const PyObject &name, const PyObject &bases, const PyObject &kwds);
// TODO: PyObject py_call(const PyObject &callable, const PyObject &args, const PyObject &kwargs);
// TODO: PyObject py_new(const PyObject &cls, const PyObject &args, const PyObject &kwargs);
// TODO: PyObject py_init(const PyObject &self, const PyObject &args, const PyObject &kwargs);
// TODO: PyObject py_del(const PyObject &self);
// TODO: PyObject py_repr(const PyObject &self);
// TODO: PyObject py_str(const PyObject &self);
// TODO: PyObject py_eq(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ne(const PyObject &self, const PyObject &other);
// TODO: PyObject py_lt(const PyObject &self, const PyObject &other);
// TODO: PyObject py_le(const PyObject &self, const PyObject &other);
// TODO: PyObject py_gt(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ge(const PyObject &self, const PyObject &other);
// TODO: PyObject py_hash(const PyObject &self);
// TODO: PyObject py_bool(const PyObject &self);
// TODO: PyObject py_getattr(const PyObject &self, const PyObject &name);
// TODO: PyObject py_getattribute(const PyObject &self, const PyObject &name);
// TODO: PyObject py_setattr(const PyObject &self, const PyObject &name, const PyObject &value);
// TODO: PyObject py_delattr(const PyObject &self, const PyObject &name);
// TODO: PyObject py_dir(const PyObject &self);
// TODO: PyObject py_len(const PyObject &self);
// TODO: PyObject py_getitem(const PyObject &self, const PyObject &key);
// TODO: PyObject py_setitem(const PyObject &self, const PyObject &key, const PyObject &value);
// TODO: PyObject py_delitem(const PyObject &self, const PyObject &key);
// TODO: PyObject py_iter(const PyObject &self);
// TODO: PyObject py_next(const PyObject &self);
// TODO: PyObject py_contains(const PyObject &self, const PyObject &key);
// TODO: PyObject py_add(const PyObject &self, const PyObject &other);
// TODO: PyObject py_sub(const PyObject &self, const PyObject &other);
// TODO: PyObject py_mul(const PyObject &self, const PyObject &other);
// TODO: PyObject py_matmul(const PyObject &self, const PyObject &other);
// TODO: PyObject py_truediv(const PyObject &self, const PyObject &other);
// TODO: PyObject py_floordiv(const PyObject &self, const PyObject &other);
// TODO: PyObject py_mod(const PyObject &self, const PyObject &other);
// TODO: PyObject py_divmod(const PyObject &self, const PyObject &other);
// TODO: PyObject py_pow(const PyObject &self, const PyObject &other, const PyObject &mod);
// TODO: PyObject py_lshift(const PyObject &self, const PyObject &other);
// TODO: PyObject py_rshift(const PyObject &self, const PyObject &other);
// TODO: PyObject py_and(const PyObject &self, const PyObject &other);
// TODO: PyObject py_xor(const PyObject &self, const Py_Object &other);
// TODO: PyObject py_or(const PyObject &self, const PyObject &other);
// TODO: PyObject py_iadd(const PyObject &self, const PyObject &other);
// TODO: PyObject py_isub(const PyObject &self, const PyObject &other);
// TODO: PyObject py_imul(const PyObject &self, const PyObject &other);
// TODO: PyObject py_imatmul(const PyObject &self, const PyObject &other);
// TODO: PyObject py_itruediv(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ifloordiv(const PyObject &self, const PyObject &other);
// TODO: PyObject py_imod(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ipow(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ilshift(const PyObject &self, const PyObject &other);
// TODO: PyObject py_irshift(const PyObject &self, const PyObject &other);
// TODO: PyObject py_iand(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ixor(const PyObject &self, const PyObject &other);
// TODO: PyObject py_ior(const PyObject &self, const PyObject &other);
// TODO: PyObject py_neg(const PyObject &self);
// TODO: PyObject py_pos(const PyObject &self);
// TODO: PyObject py_abs(const PyObject &self);
// TODO: PyObject py_invert(const PyObject &self);
// TODO: PyObject py_complex(const PyObject &self);
// TODO: PyObject py_int(const PyObject &self);
// TODO: PyObject py_float(const PyObject &self);
// TODO: PyObject py_index(const PyObject &self);
// TODO: PyObject py_round(const PyObject &self, const PyObject &ndigits);
// TODO: PyObject py_trunc(const PyObject &self);
// TODO: PyObject py_floor(const PyObject &self);
// TODO: PyObject py_ceil(const PyObject &self);
// TODO: PyObject py_enter(const PyObject &self);
// TODO: PyObject py_exit(const PyObject &self, const PyObject &exc_type, const PyObject &exc_value, const PyObject &traceback);
// TODO: PyObject py_await(const PyObject &self);
// TODO: PyObject py_aiter(const PyObject &self);
// TODO: PyObject py_anext(const PyObject &self);
// TODO: PyObject py_aenter(const PyObject &self);
// TODO: PyObject py_aexit(const PyObject &self, const PyObject &exc_type, const PyObject &exc_value, const PyObject &traceback);
// TODO: PyObject py_aiter(const PyObject &self);
// TODO: PyObject py_anext(const PyObject &self);

PyObject py_add(const PyObject &a, const PyObject &b)
{
    switch (a.type)
    {
    case PyType::INT:
        switch (b.type)
        {
        case PyType::INT:
            return PyObject::from_int(static_cast<int64_t>(a.raw) + static_cast<int64_t>(b.raw));
        case PyType::FLOAT:
        {
            double ad = static_cast<double>(static_cast<int64_t>(a.raw));
            double bd;
            std::memcpy(&bd, &b.raw, sizeof(double));
            return PyObject::from_float(ad + bd);
        }
        default:
            break;
        }
        break;

    case PyType::FLOAT:
    {
        double av;
        std::memcpy(&av, &a.raw, sizeof(double));
        switch (b.type)
        {
        case PyType::INT:
        {
            double bv = static_cast<double>(static_cast<int64_t>(b.raw));
            return PyObject::from_float(av + bv);
        }
        case PyType::FLOAT:
        {
            double bv;
            std::memcpy(&bv, &b.raw, sizeof(double));
            return PyObject::from_float(av + bv);
        }
        default:
            break;
        }
        break;
    }

    case PyType::STR:
        if (b.type == PyType::STR)
        {
            return PyObject::from_string(*reinterpret_cast<std::string *>(a.raw) + *reinterpret_cast<std::string *>(b.raw));
        }
        break;

    case PyType::LIST:
        if (b.type == PyType::LIST)
        {
            auto avec = *reinterpret_cast<std::vector<PyObject> *>(a.raw);
            auto bvec = *reinterpret_cast<std::vector<PyObject> *>(b.raw);
            avec.insert(avec.end(), bvec.begin(), bvec.end());
            return PyObject::from_list(avec);
        }
        break;

    default:
        break;
    }

    throw std::runtime_error("TypeError: unsupported operand types for +: '" +
                             py_get_type(a) + "' and '" + py_get_type(b) + "'");
}

PyObject py_mul(const PyObject &a, const PyObject &b)
{
    if (a.type == PyType::INT && b.type == PyType::INT)
    {
        return PyObject::from_int(static_cast<int64_t>(a.raw) * static_cast<int64_t>(b.raw));
    }

    // int / float
    if (a.type == PyType::INT && b.type == PyType::FLOAT)
    {
        double ad = static_cast<double>(static_cast<int64_t>(a.raw));
        double bd;
        std::memcpy(&bd, &b.raw, sizeof(double));
        return PyObject::from_float(ad * bd);
    }
    else if (b.type == PyType::INT && a.type == PyType::FLOAT)
    {
        return py_mul(b, a);
    }

    // int / str
    if (a.type == PyType::INT && b.type == PyType::STR)
    {
        int64_t n = static_cast<int64_t>(a.raw);
        const auto &s = *reinterpret_cast<std::string *>(b.raw);
        std::string result;
        for (int64_t i = 0; i < n; ++i)
            result += s;
        return PyObject::from_string(result);
    }
    else if (b.type == PyType::INT && a.type == PyType::STR)
    {
        return py_mul(b, a);
    }

    // int / list
    if (a.type == PyType::INT && b.type == PyType::LIST)
    {
        int64_t n = static_cast<int64_t>(a.raw);
        auto items = *reinterpret_cast<std::vector<PyObject> *>(b.raw);
        std::vector<PyObject> result;
        for (int64_t i = 0; i < n; ++i)
            result.insert(result.end(), items.begin(), items.end());

        return PyObject::from_list(result);
    }
    else if (b.type == PyType::INT && a.type == PyType::LIST)
    {
        return py_mul(b, a);
    }

    throw std::runtime_error("TypeError: unsupported operand types for *: '" +
                             py_get_type(a) + "' and '" + py_get_type(b) + "'");
}