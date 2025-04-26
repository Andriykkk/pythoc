import argparse
import ast
import os

def parse_source(source_code: str):
    try:
        with open(source_code, "r") as file:
            tree = ast.parse(file.read(), mode="exec")

            compile(tree, "<string>", "exec")

            return tree
    except SyntaxError as e:
        raise e
    except Exception as e:
        raise e
    
def check_source_file(file_path: str):
    if file_path.endswith(".py") and os.path.isfile(file_path):
        return True
    elif os.path.isfile(file_path + ".py"):
        return True
    else:
        return False


def read_arguments():
    parser = argparse.ArgumentParser(
        description="Process a file name provided either as a positional argument or with -f/--file."
    )

    parser.add_argument("filename", nargs="?", help="Name of the file")
    parser.add_argument("-f", "--file", dest="file_arg",
                        help="Name of the file (alternative to positional)")

    args = parser.parse_args()

    file_name = args.filename or args.file_arg
    if not file_name:
        print("No file name provided.")
        return
    
    if not check_source_file(file_name):
        print(f"File {file_name} does not exist or is not a Python file.")
        return

    if args.file_arg is not None and args.filename is None:
        args.filename = args.file_arg
    
    return args 