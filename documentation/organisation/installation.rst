Installation
============


Installation from source
------------------------

To retrieve the sources, the ``git``-repository of the *SuMPF* package has to be cloned.

::

   git clone https://github.com/JonasSC/SuMPF.git SuMPF

The ``SuMPF`` at the end of this command specifies the directory, in which the local copy of the repository shall be created.
After cloning, move to that directory.

::

   cd SuMPF

Now the *SuMPF* package can be installed system wide with the following command:

::

   python3 setup.py install

Alternatively, the package can be installed only for the current user.

::

   python3 setup.py install --user
