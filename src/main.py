import argparse
from enum import Enum
import ast
import subprocess
import os
from reader import read_arguments, parse_source
from traverser import traverse
from compiler import compile_to_cpp



def main():
    args = read_arguments()
    print(args)
    ast_tree = parse_source(args.filename)

    tree = traverse(ast_tree)

    print(ast.dump(ast_tree, indent=4))
    print(tree._repr())

    cpp_code = compile_to_cpp(tree)
    
    with open("./src/pyclib/output.cpp", "w") as f:
        f.write(cpp_code)

    # print("Generated C++ code in output.cpp:")
    # print(cpp_code)

    subprocess.run(["./src/pyclib/buildNrun.sh"], check=True)

 
if __name__ == "__main__":
    main()
