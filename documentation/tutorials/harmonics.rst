Measuring the impulse responses of harmonics
============================================

This tutorial shows the measurement and analysis of the impulse response of a nonlinear system.
This demonstrates the features of *SuMPF*, that are useful for writing concise analysis scripts, such as the data generation classes, their overloaded operators and other methods.


Theoretical background
----------------------

A sweep excites only one frequency at a time and it starts with the lowest frequency.
A nonlinear system, that is excited with a frequency does not only respond with its excitation frequency, but also with its integer multiples.
This means, that when excited with a sweep, a nonlinear system responds with frequencies, that are excited at a later point in time.
When computing the impulse response of the system, these components are shifted in the non-causal part of the impulse response.
An exponential sweep has the convenient property, that this shift is constant for each frequency, which means, that the seemingly non-causal artifacts add up to impulse responses for the harmonic distortions.

This idea has been explored and described by `Angelo Farina <http://pcfarina.eng.unipr.it/Public/AES-110/154-aes110.PDF>`_ and `Antonin Novak <https://ant-novak.com/pages/sss/>`_.
Novak also developed a variation of the exponential sweep, the synchronized sweep, which allows measuring the impulse responses of the harmonics with the correct phase.
In this simple example, this variation is omitted, since it is not (yet) implemented in *SuMPF*.


Importing the required packages
-------------------------------

We need *SuMPF* for the signal processing and :mod:`matplotlib` for rendering the plots.

>>> import sumpf
>>> from matplotlib import pyplot


Defining a nonlinear system
---------------------------

In this section, we define a nonlinear system, that shall be measured with *SuMPF*.
This is a simple function, that expects the excitation signal as an argument and returns the response signal.

>>> def system(excitation):
...     x = excitation
...     distorted = 0.5 * x ** 3 - 0.6 * x ** 2 + 0.1 * x + 0.02
...     highpass = sumpf.Chebyshev1Filter(cutoff_frequency=100.0,
...                                       ripple=4.0,
...                                       order=4,
...                                       highpass=True)
...     lowpass = sumpf.ButterworthFilter(cutoff_frequency=3000.0,
...                                       order=2,
...                                       highpass=False)
...     filtered = distorted * highpass * lowpass
...     shifted = filtered.shift(50)
...     return shifted

the excitation is relabeled to ``x``, so it becomes clearer, that ``distorted`` is basically a polynomial of the excitation signal.
Note, how the :class:`~sumpf.Signal` class has overloaded its math operators, so that the power, the multiplication and the addition can be written, as if ``x`` was an ordinary number.

``lowpass`` and ``highpass`` are filters, that contain an analytical description of a filter's transfer function.
Note, that we did not instantiate the :class:`~sumpf.Filter` class and built those IIR filters from scratch.
Instead, we used subclasses of :class:`~sumpf.Filter`, which generate the desired transfer functions from common filter parameters.

The filters can be applied to a signal by multiplying the two.
Behind the scenes, this is an element-wise multiplication in the frequency domain.

The :class:`~sumpf.Signal` class has an ``offset`` parameter, which defines, where the first sample of the signal is located in relation to the sample of the zero point in time.
This allows to create signals, that start before (negative offset) or after (positive offset) that zero point in time.
The :meth:`~sumpf.Signal.shift` method is used in this example to increase the offset of the system's response :class:`~sumpf.Signal` by 50 samples, which means, that the response is delayed.


Creating an excitation signal
-----------------------------

At first, we need an exponential sweep.
*SuMPF* provides a subclass of :class:`~sumpf.Signal` to generate one.

>>> sweep = sumpf.ExponentialSweep(start_frequency=20.0,
...                                stop_frequency=5000.0,
...                                interval=(4096, -4096),
...                                sampling_rate=48000,
...                                length=2 ** 16)

The ``interval`` parameter specifies, that the sweep shall sweep from the start to the stop frequency between the given sample indices.
The stop index is given as a negative number, which means that it shall be counted from the back of the signal.

If a signal starts or stops abruptly, this jump in amplitude excites many frequencies at once, which spoils the sweep's property, that it only excites one frequency at a time.
To avoid these abrupt jumps, the sweep must be faded in and out gently.
If these fades are applied outside the interval, we know, that the specified frequency range of the sweep is unaffected by the fade.

We can now generate a signal, that defines the fade in and the fade out of the excitation signal.
In accordance with the sweep's ``interval`` parameter, the fade in should happen in the first 4096 samples, while the fade out should affect the last 4096 samples.
The fade signal is basically a mask, that rises from 0.0 to 1.0 during the rise interval, stays at 1.0 for a while and falls back to 0.0 during the fall interval.

>>> fade = sumpf.Fade(rise_interval=(0, 4096),
...                   fall_interval=(-4096, 1.0),
...                   sampling_rate=48000.0,
...                   length=2 ** 16)
>>> excitation = sweep * fade

Note how the sample indices of the ``fall_interval`` parameter are defined.
As above, the start index is given as a negative number, which means, that the index is counted from the back of the signal.
The stop index is given as a float.
*SuMPF* accepts floats between 0.0 and 1.0 as sample indices, which will be multiplied with the length of the data set and then rounded to the next integer.
In this case, the 1.0 means, that the fall interval shall span until the end of the signal.

The fading mask is then applied to the sweep, by multiplying the two.

Of course, the sweep has to start at a lower frequency and end at a higher frequency, than the given start and stop frequencies, because of the additional samples outside the interval.
Since we know, that the nonlinear system contains a third degree polynomial, we know, that it produces nonlinearities up to the third harmonic.
This means, that we should not excite more than 8kHz, because otherwise, the third harmonic will contain frequencies above 24kHz, which is more than half the sampling rate of 48kHz and therefore will cause aliasing.
Since the sweep's start and stop frequencies are defined for the given interval and the sweep continues outside that interval, we don't know the minimum and maximum frequencies, that are actually excited by the sweep.
In addition to the functionality of the :class:`~sumpf.Signal` class, the :class:`~sumpf.ExponentialSweep` class provides methods, that compute these frequencies.

>>> sweep.maximum_frequency()
7417.395449686142


Measuring the response of our system
------------------------------------

The response of our example system is computed by calling the function.

>>> response = system(excitation)


Computing the impulse response of the system
--------------------------------------------

Since the response, that we have got from our system is not the one to an impulse, but the one to an exponential sweep, we have to compensate for the differences between the sweep and an impulse.
One way to do that is to convolve the response with an inverse exponential sweep, which is a signal, whose convolution with an exponential sweep results in an impulse.
*SuMPF* offers a class to create such a signal.

>>> inverse = sumpf.InverseExponentialSweep(start_frequency=20.0,
...                                         stop_frequency=5000.0,
...                                         interval=(4096, -4096),
...                                         sampling_rate=48000,
...                                         length=2 ** 16)

Note that the inverse sweep takes exactly the same parameter values as the sweep, to which it shall be the inverse.

The convolution is computed with the :meth:`~sumpf.Signal.convolve` method.
This method accepts a ``mode``-parameter, which specifies, how the convolution shall be computed.
In this case, the convolution is computed in the frequency domain, which is faster than the time domain implementations.

>>> impulse_response = response.convolve(inverse, mode=sumpf.Signal.convolution_modes.SPECTRUM_PADDED)


Properties of the impulse response
----------------------------------

Now, the impulse response can be plotted.

>>> pyplot.plot(impulse_response.time_samples(), impulse_response.channels()[0])    # doctest: +SKIP
>>> pyplot.xlabel("time")                                                           # doctest: +SKIP
>>> pyplot.ylabel("amplitude")                                                      # doctest: +SKIP
>>> pyplot.show()                                                                   # doctest: +SKIP

There are two things to point out here.
First, the :class:`~sumpf.Signal` class provides the method :meth:`~sumpf.Signal.time_samples`, which creates an array, that contains the time values of the signal's samples.
This array can be used for the x-values of the plot.
And second, all data sets in *SuMPF* support multiple channels.
For the :class:`~sumpf.Signal` class, this means, that the :meth:`~sumpf.Signal.channels` method returns a two dimensional array, in which the rows correspond to a channel.
For the plot, a single channel of this array has to be extracted.

.. plot ::

   import sumpf
   from matplotlib import pyplot
   def system(excitation):
       distorted = 0.5 * excitation ** 3 - 0.6 * excitation ** 2 + 0.1 * excitation + 0.02
       highpass = sumpf.Chebyshev1Filter(cutoff_frequency=100.0, ripple=4.0, order=4, highpass=True)
       lowpass = sumpf.ButterworthFilter(cutoff_frequency=3000.0, order=2, highpass=False)
       filtered = distorted * highpass * lowpass
       shifted = filtered.shift(50)
       return shifted
   sweep = sumpf.ExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   fade = sumpf.Fade(rise_interval=(0, 4096), fall_interval=(-4096, 1.0), sampling_rate=48000.0, length=2 ** 16)
   excitation = sweep * fade
   response = system(excitation)
   inverse = sumpf.InverseExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   impulse_response = response.convolve(inverse)
   pyplot.plot(impulse_response.time_samples(), impulse_response.channels()[0])  # doctest: +SKIP
   pyplot.xlabel("time")                                                         # doctest: +SKIP
   pyplot.ylabel("amplitude")                                                    # doctest: +SKIP
   pyplot.show()                                                                 # doctest: +SKIP

The plot shows three impulses.
The largest one around time point zero is the one, that corresponds to the linear components of the system's response.
The two impulses in the negative time domain are the impulse responses of the second and third harmonic.


Cutting out the impulse responses
---------------------------------

The :class:`~sumpf.ExponentialSweep` and :class:`~sumpf.InverseExponentialSweep` classes provide the :meth:`~sumpf.ExponentialSweep.harmonic_impulse_response` method, with which the impulse responses of the harmonics can be cut out of the measured impulse response.

>>> harmonic1 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
...                                             harmonic=1)
>>> harmonic2 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
...                                             harmonic=2)
>>> harmonic3 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
...                                             harmonic=3)

The resulting impulse responses of the harmonics are ordinary signals, that can be plotted like described above.

>>> for harmonic in [harmonic1, harmonic2, harmonic3]:                                             # doctest: +SKIP
...     pyplot.plot(harmonic.time_samples(), harmonic.channels()[0], label=harmonic.labels()[0])   # doctest: +SKIP
>>> pyplot.xlabel("time")                                                                          # doctest: +SKIP
>>> pyplot.ylabel("amplitude")                                                                     # doctest: +SKIP
>>> pyplot.legend()                                                                                # doctest: +SKIP
>>> pyplot.show()                                                                                  # doctest: +SKIP

Note, that this time, the plot has a legend, that was created from the impulse responses' labels.

.. plot ::

   import sumpf
   from matplotlib import pyplot
   def system(excitation):
       distorted = 0.5 * excitation ** 3 - 0.6 * excitation ** 2 + 0.1 * excitation + 0.02
       highpass = sumpf.Chebyshev1Filter(cutoff_frequency=100.0, ripple=4.0, order=4, highpass=True)
       lowpass = sumpf.ButterworthFilter(cutoff_frequency=3000.0, order=2, highpass=False)
       filtered = distorted * highpass * lowpass
       shifted = filtered.shift(50)
       return shifted
   sweep = sumpf.ExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   fade = sumpf.Fade(rise_interval=(0, 4096), fall_interval=(-4096, 1.0), sampling_rate=48000.0, length=2 ** 16)
   excitation = sweep * fade
   response = system(excitation)
   inverse = sumpf.InverseExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   impulse_response = response.convolve(inverse)
   harmonic1 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=1,
                                               circular=False)
   harmonic2 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=2,
                                               circular=False)
   harmonic3 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=3,
                                               circular=False)
   for harmonic in [harmonic1, harmonic2, harmonic3]:                                              # doctest: +SKIP
       pyplot.plot(harmonic.time_samples(), harmonic.channels()[0], label=harmonic.labels()[0])    # doctest: +SKIP
   pyplot.xlabel("time")                                                                           # doctest: +SKIP
   pyplot.ylabel("amplitude")                                                                      # doctest: +SKIP
   pyplot.legend()                                                                                 # doctest: +SKIP
   pyplot.show()                                                                                   # doctest: +SKIP

Note that the cut out impulse responses are all shifted to the zero point in time.


Merging the impulse responses into one multi-channel signal
-----------------------------------------------------------

For convenience (and to demonstrate that feature), the harmonics are merged into a single :class:`~sumpf.Signal` instance with one channel per harmonic.

>>> harmonics = sumpf.MergeSignals([harmonic1, harmonic2, harmonic3]).output()

In a scripting application, like this tutorial, the API for merging signals is inconvenient.
Rather than being a function, it requires instantiating the :class:`~sumpf.MergeSignals` class and calling its :meth:`~sumpf.MergeSignals.output` method.
This is due to a :ref:`design decision<concepts>` in *SuMPF*, that all functionalities, that do not fit in the data container classes, are implemented in classes for signal processing blocks, that can be connected to form complex signal processing networks, in which value changes are automatically propagated.

Thanks to the :func:`zip` function, plotting the merged signal is mildly more convenient, than plotting the individual harmonics before.

>>> for channel, label in zip(harmonics.channels(), harmonics.labels()):   # doctest: +SKIP
...     pyplot.plot(harmonics.time_samples(), channel, label=label)        # doctest: +SKIP
>>> pyplot.xlabel("time")                                                  # doctest: +SKIP
>>> pyplot.ylabel("amplitude")                                             # doctest: +SKIP
>>> pyplot.legend()                                                        # doctest: +SKIP
>>> pyplot.show()                                                          # doctest: +SKIP

.. plot ::

   import sumpf
   from matplotlib import pyplot
   def system(excitation):
       distorted = 0.5 * excitation ** 3 - 0.6 * excitation ** 2 + 0.1 * excitation + 0.02
       highpass = sumpf.Chebyshev1Filter(cutoff_frequency=100.0, ripple=4.0, order=4, highpass=True)
       lowpass = sumpf.ButterworthFilter(cutoff_frequency=3000.0, order=2, highpass=False)
       filtered = distorted * highpass * lowpass
       shifted = filtered.shift(50)
       return shifted
   sweep = sumpf.ExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   fade = sumpf.Fade(rise_interval=(0, 4096), fall_interval=(-4096, 1.0), sampling_rate=48000.0, length=2 ** 16)
   excitation = sweep * fade
   response = system(excitation)
   inverse = sumpf.InverseExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   impulse_response = response.convolve(inverse)
   harmonic1 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=1,
                                               circular=False)
   harmonic2 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=2,
                                               circular=False)
   harmonic3 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=3,
                                               circular=False)
   harmonics = sumpf.MergeSignals([harmonic1, harmonic2, harmonic3]).output()
   for channel, label in zip(harmonics.channels(), harmonics.labels()):    # doctest: +SKIP
       pyplot.plot(harmonics.time_samples(), channel, label=label)         # doctest: +SKIP
   pyplot.xlabel("time")                                                   # doctest: +SKIP
   pyplot.ylabel("amplitude")                                              # doctest: +SKIP
   pyplot.legend()                                                         # doctest: +SKIP
   pyplot.show()                                                           # doctest: +SKIP

Note, that now, all impulse responses have the same length.
Internally, the :class:`~sumpf.Signal` class uses a two-dimensional :func:`numpy.array`, that cannot store channels with different lengths.
Therefore, the :class:`~sumpf.MergeSignals` class fills missing samples with zeros.


Visualizing the transfer function
---------------------------------

Computing the transfer function from an impulse response is done by transforming it to the frequency domain with the help of the fourier transform.

>>> transfer_function = harmonics.fourier_transform()

The resulting transfer function is stored in a :class:`~sumpf.Spectrum` instance.
Since the transfer function's channels store complex values, it is most common, to plot only its magnitude.
The :class:`~sumpf.Spectrum` class's :meth:`~sumpf.Spectrum.frequency_samples` method provides an array of frequency values, that can be used as x-axis values for the plot.

>>> for magnitude, label in zip(transfer_function.magnitude(), transfer_function.labels()):  # doctest: +SKIP
...     pyplot.plot(transfer_function.frequency_samples(), magnitude, label=label)           # doctest: +SKIP

In addition to the transfer function's magnitude spectrum, it is possible to include a couple of frequencies, that have been used in this tutorial, as vertical lines in the plot:

* The red lines mark the defined start and stop frequencies of the exponential sweep.
* The black lines mark the minimum and maximum frequencies, that the sweep has excited, due to its fade in and fade out.
* The blue lines mark the cutoff frequencies of the filters in the system, that has been measured with the sweep.

>>> pyplot.axvline(20.0, linestyle="--", color="r")                        # doctest: +SKIP
>>> pyplot.axvline(5000.0, linestyle="--", color="r")                      # doctest: +SKIP
>>> pyplot.axvline(sweep.minimum_frequency(), linestyle="--", color="k")   # doctest: +SKIP
>>> pyplot.axvline(sweep.maximum_frequency(), linestyle="--", color="k")   # doctest: +SKIP
>>> pyplot.axvline(100.0, linestyle="--", color="b")                       # doctest: +SKIP
>>> pyplot.axvline(3000.0, linestyle="--", color="b")                      # doctest: +SKIP

And with that done, it's only a few lines of code to fine tune and display the plot.

>>> pyplot.xlabel("frequency")   # doctest: +SKIP
>>> pyplot.ylabel("magnitude")   # doctest: +SKIP
>>> pyplot.loglog()              # doctest: +SKIP
>>> pyplot.legend()              # doctest: +SKIP
>>> pyplot.xlim(10.0, 12000.0)   # doctest: +SKIP
>>> pyplot.ylim(0.001, 10.0)     # doctest: +SKIP
>>> pyplot.show()                # doctest: +SKIP

.. plot ::

   import sumpf
   from matplotlib import pyplot
   def system(excitation):
       distorted = 0.5 * excitation ** 3 - 0.6 * excitation ** 2 + 0.1 * excitation + 0.02
       highpass = sumpf.Chebyshev1Filter(cutoff_frequency=100.0, ripple=4.0, order=4, highpass=True)
       lowpass = sumpf.ButterworthFilter(cutoff_frequency=3000.0, order=2, highpass=False)
       filtered = distorted * highpass * lowpass
       shifted = filtered.shift(50)
       return shifted
   sweep = sumpf.ExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   fade = sumpf.Fade(rise_interval=(0, 4096), fall_interval=(-4096, 1.0), sampling_rate=48000.0, length=2 ** 16)
   excitation = sweep * fade
   response = system(excitation)
   inverse = sumpf.InverseExponentialSweep(start_frequency=20.0, stop_frequency=5000.0, interval=(4096, -4096), sampling_rate=48000, length=2 ** 16)
   impulse_response = response.convolve(inverse)
   harmonic1 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=1,
                                               circular=False)
   harmonic2 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=2,
                                               circular=False)
   harmonic3 = sweep.harmonic_impulse_response(impulse_response=impulse_response,
                                               harmonic=3,
                                               circular=False)
   harmonics = sumpf.MergeSignals([harmonic1, harmonic2, harmonic3]).output()
   transfer_function = harmonics.fourier_transform()
   for magnitude, label in zip(transfer_function.magnitude(), transfer_function.labels()):   # doctest: +SKIP
       pyplot.plot(transfer_function.frequency_samples(), magnitude, label=label)            # doctest: +SKIP
   pyplot.axvline(20.0, linestyle="--", color="r")                                           # doctest: +SKIP
   pyplot.axvline(5000.0, linestyle="--", color="r")                                         # doctest: +SKIP
   pyplot.axvline(sweep.minimum_frequency(), linestyle="--", color="k")                      # doctest: +SKIP
   pyplot.axvline(sweep.maximum_frequency(), linestyle="--", color="k")                      # doctest: +SKIP
   pyplot.axvline(100.0, linestyle="--", color="b")                                          # doctest: +SKIP
   pyplot.axvline(3000.0, linestyle="--", color="b")                                         # doctest: +SKIP
   pyplot.xlabel("frequency")                                                                # doctest: +SKIP
   pyplot.ylabel("magnitude")                                                                # doctest: +SKIP
   pyplot.loglog()                                                                           # doctest: +SKIP
   pyplot.legend()                                                                           # doctest: +SKIP
   pyplot.xlim(10.0, 12000.0)                                                                # doctest: +SKIP
   pyplot.ylim(0.001, 10.0)                                                                  # doctest: +SKIP
   pyplot.show()                                                                             # doctest: +SKIP
