.. module:: sumpf

Welcome to SuMPF's documentation!
=================================

The *SuMPF* package provides some classes, that implement offline (non-realtime) signal processing functionalities.
*SuMPF* is being developed with a focus on acoustics, but it might be applicable for the analysis of other time series data as well.

Here is a brief example of *SuMPF* in action:

>>> import sumpf
>>> noise = sumpf.GaussianNoise(mean=0.0,
...                             standard_deviation=1.0,
...                             sampling_rate=48000.0,
...                             length=2 ** 14)
>>> filter_ = sumpf.ButterworthFilter(cutoff_frequency=1000.0, order=4, highpass=True)
>>> filtered = noise * filter_
>>> spectrum = filtered.fourier_transform()


Contents
--------

.. toctree::
   :maxdepth: 2
   :numbered:

   reference/index
   organisation/index
   tutorials/index


Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
