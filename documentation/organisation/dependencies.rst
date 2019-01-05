.. _dependencies:

Dependencies
============

Python version
--------------

The *SuMPF* package is currently developed and tested with Python 3.7.
Most features should be available with Python 3.6 as well.


Other packages and tools
------------------------

Many core features of *SuMPF* depend on :mod:`numpy` and :mod:`connectors`.
Importing *SuMPF* will fail, if these packages are not available.

Other packages are optional, but not installing them, will reduce the number of features of SuMPF.

* some computations require :mod:`scipy`.
* saving certain audio files requires :mod:`soundfile`.
* :mod:`numexpr` is used for performance gains.
* playing back and recording audio signals is done with :mod:`jack`.
* the setup is done with :mod:`setuptools`.
* the tests are run with :mod:`pytest`.
   - thorough testing is achieved with :mod:`hypothesis`.
   - the test coverage is assessed with :mod:`pytest-cov`.
   - the code is analyzed with *Pylint* and :mod:`flake8`.
   - spell-checking is done with *pyenchant*.
* the documentation is built with :mod:`sphinx`.
   - the documentation uses the :mod:`sphinx_rtd_theme`.
   - graphs are drawn with :mod:`sphinx.ext.graphviz`.
   - some examples rely on :mod:`matplotlib`.
