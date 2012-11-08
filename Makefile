install:
	# installs the python module for SuMPF on the system.
	cd source && python setup.py install && rm -r build

install_user:
	# installs the python module for SuMPF for the current user.
	# The module will most likely be somewhere in ~/.local/lib/python...
	cd source && python setup.py install --user && rm -r build

clean:
	# deletes the python bytecode by removing the *.pyc files and __pycache__
	# directories from the source, the test and the tools directories.
	rm -vf `find -name *.pyc`
	rm -vrf `find -name __pycache__`

mrproper:	clean
	# deletes the Python bytecode just like "make clean", but also deletes the
	# automatically generated documentation.
	rm -rf documentation/doxygen
	rm -rf documentation/moduledoc
	rm -f documentation/statistics.htm

doc:
	# creates the documentation files that are created automatically.
	# The files can be found in the ./documentation folder
	doxygen tools/Doxyfile
	export PYTHONPATH="$$PYTHONPATH":"`pwd`/source" && python tools/moduledoc.py -o documentation/moduledoc/ -d documentation/doxygen/html/ -m sumpf -s documentation/header.js
	python tools/statistics.py -f documentation/statistics.htm

install_examples:
	# installs the examples of SuMPF as executable programs on the system.
	# The programs can be run with the command sumpf_NAME, where NAME is the
	# name of the example function.
	# SuMPF needs to be installed before this make target can be run.
	python tools/installexamples.py -o /usr/bin/bin

install_examples_local:
	# installs the examples of SuMPF as executable programs in ./bin.
	# SuMPF needs to be installed before this make target can be run.
	python tools/installexamples.py -o ./bin

