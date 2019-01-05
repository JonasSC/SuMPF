import os
import sys
import pytest

if __name__ == "__main__":
    # make the optional dependencies unavailable by inserting a set of modules,
    # that raise an ImportError at the front of sys.modules
    path = os.path.abspath(os.path.join(*os.path.split(__file__)[0:-1], "unavailable_modules"))
    sys.path.insert(0, path)
    # compile the command line parameters
    args = ["--doctest-glob=\"*.rst\"", "--doctest-modules", f"--ignore={path}"]
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    else:
        args.append("./tests")
    # run the tests
    exit_code = pytest.main(args=args)
    exit(exit_code)
