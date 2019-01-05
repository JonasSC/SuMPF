Makefile targets
================

The Makefile in the source code repository of the *SuMPF* package has the following targets:

* ``make test`` runs the unit tests.
* ``make test_coverage`` runs the unit tests and prints information about their test coverage.
* ``make test_without_optional_dependencies`` runs the unit tests with the :ref:`optional dependencies<dependencies>` being made unavailable, so that it's tested, if *SuMPF* degrades gracefully.
* ``make lint`` checks the package and the unit tests with *Pylint* and :mod:`flake8`.
* ``make docs`` builds the documentation.

The ``test``, ``test_coverage`` and ``test_without_optional_dependencies`` targets also accept parameters, which are passed to the :mod:`pytest` call.
This allows to run only specific tests, for example ``make test documentation`` will only run the :mod:`doctest` tests of the files in the documentation directory.
