import argparse
from enum import Enum
import ast
import subprocess
import os
from reader import read_arguments, parse_source
from traverser import traverse



def main():
    args = read_arguments()

    ast_tree = parse_source(args.filename)

    tree = traverse(ast_tree)

    print(ast.dump(ast_tree, indent=4))
    print(tree._repr())

    # code = compileToCpp(tree)
    # print(code)
 
if __name__ == "__main__":
    main()