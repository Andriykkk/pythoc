import os
import subprocess
import unittest
import shutil
from main import parse_source, ASTParser, IRCompiler, IRRunner

class CompilerTestHelper:
    def __init__(self, code: str, filename: str = "test.py"):
        self.filename = filename
        self.code = code
        self.runner = IRRunner()

    def write_python_file(self):
        with open(self.filename, "w") as f:
            f.write(self.code)

    def remove_files(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

        rust_file = "pythoc/src/main.rs"
        if os.path.exists(rust_file):
            os.remove(rust_file)

        target_dir = "pythoc/target"
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

    def get_python_output(self):
        process = subprocess.Popen(["python", self.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = process.communicate()
        return stdout.decode().strip()

    def get_rust_output(self):
        ast_tree = parse_source(self.filename)
        parser = ASTParser(ast_tree)
        ir_tree = parser.parse_ast()
        compiler = IRCompiler(ir_tree)
        compiler.compile()
        compiler.add_test('println!("{}", z);')
        compiler.generate_rust()
        compiler.create_rust_file(logs=False)
        self.runner.build_rust_code(logs=False, errors=False)
        return self.runner.run_rust_code(return_output=True, logs=False).strip()

    def compare_outputs(self):
        return self.get_python_output() == self.get_rust_output()

    def run_all(self):
        self.write_python_file()
        py_output = self.get_python_output()
        rust_output = self.get_rust_output()
        self.remove_files()
        return py_output, rust_output