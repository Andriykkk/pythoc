import unittest
import ast
from main import IRRunner, ASTParser, IRCompiler
import subprocess
import os
from reader import parse_source, read_arguments
from compiler_test_helper import CompilerTestHelper

class CompilerTest(unittest.TestCase):
    def run_operator_test(self, expression: str):
        code = f"x = 10\ny = 3\nz = {expression}\nprint(z)\n"
        helper = CompilerTestHelper(code)
        helper.write_python_file()

        py_output = helper.get_python_output()

        helper.code = f"x = 10\ny = 3\nz = {expression}"
        helper.write_python_file()
        rust_output = helper.get_rust_output()

        helper.remove_files()
        self.assertEqual(py_output, rust_output)

    def test_add(self):
        self.run_operator_test("x + y")

    def test_sub(self):
        self.run_operator_test("x - y")

    def test_mult(self):
        self.run_operator_test("x * y")

    def test_matmult(self):
        pass

    def test_div(self):
        self.run_operator_test("x / y")

    # def test_mod(self):
    #     self.run_operator_test("x % y")

    def test_pow(self):
        self.run_operator_test("x ** y")

    def test_lshift(self):
        self.run_operator_test("x << y")

    def test_rshift(self):
        self.run_operator_test("x >> y")

    def test_bitor(self):
        self.run_operator_test("x | y")

    def test_bitxor(self):
        self.run_operator_test("x ^ y")

    def test_bitand(self):
        self.run_operator_test("x & y")

    # def test_floordiv(self):
    #     self.run_operator_test("x // y")