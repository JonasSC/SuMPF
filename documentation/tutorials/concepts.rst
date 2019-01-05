.. _concepts:

Basic concepts
==============

This section explains the basic concepts of the *SuMPF* package.

Data containers and signal processing blocks
--------------------------------------------

*SuMPF* provides mainly two sets of classes.
One is a set of data containers, while the other classes implement signal processing operations.

The data containers are used to store measurements or analysis results, which are passed around between the signal processing steps.
Data containers should be considered immutable.

The instances of signal processing steps are mutable objects, which have setter methods for data and parameters.
Their getter methods return the processing results.
The methods of the processing objects can be connected to each other, so that the whole processing chain is updated, once a parameter is changed.
See the :mod:`connectors` package for further information on this.

While the connections between signal processing classes are handy in interactive applications, the instantiation of these classes is tedious in simple analysis scripts.
For this reason, the data containers provide many methods and overloaded operators, which implement a readable API for signal processing operations.


Derived classes of data containers
----------------------------------

So far, *SuMPF* features three base classes for signal processing related data:

* :class:`sumpf.Signal` stores equidistantly sampled time series data.
* :class:`sumpf.Spectrum` stores equidistantly sampled frequency domain data.
* :class:`sumpf.Filter` provides some functions to give an analytical description of a transfer function.

The classes :class:`~sumpf.Signal` and :class:`~sumpf.Spectrum` are basically wrappers around :func:`numpy.array`\ s, that add metadata and convenience methods.

*SuMPF* provides sub-classes of these data containers, that allow the generation of specific data sets, such as :class:`~sumpf.ExponentialSweep` or :class:`~sumpf.ButterworthFilter`.
These sub-classes take some parameters as constructor arguments and initialize the respective data container accordingly.
Often they also feature additional methods to those, that are already provided by their base class.
