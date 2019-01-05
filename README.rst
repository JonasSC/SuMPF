SuMPF
=====

The *SuMPF* package provides some classes, that implement offline (non-realtime) signal processing functionalities.
*SuMPF* is being developed with a focus on acoustics, but it might be applicable for the analysis of other time series data as well.

Here is a brief example of *SuMPF* in action:

>>> import sumpf
>>> noise = sumpf.GaussianNoise(mean=0.0,
...                            standard_deviation=1.0,
...                            sampling_rate=48000.0,
...                            length=2 ** 14)
>>> filter_ = sumpf.ButterworthFilter(cutoff_frequency=1000.0, order=4, highpass=True)
>>> filtered = noise * filter_
>>> spectrum = filtered.fourier_transform()


Installation
------------

The *SuMPF* package requires Python version 3.7 or later.
Most features should be available with Python 3.6 as well.

::

   pip3 install sumpf

Documentation
-------------

The documentation for the *SuMPF* librariy can be found on `Read the Docs <https://sumpf.readthedocs.io/en/latest/>`_.


License
-------

The *SuMPF* package is published under the terms and conditions of the GNU lesser general public license version 3 or later (LGPLv3+).
