# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2019 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains tests for the sweep related classes"""

import ctypes
import logging
import math
import random
from multiprocessing import sharedctypes
import timeit
import hypothesis
import numpy
import pytest
import sumpf
import sumpf._internal as sumpf_internal

###################################
# test the ExponentialSweep class #
###################################


@hypothesis.given(start_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=9999.0),
                  stop_frequency=hypothesis.strategies.floats(min_value=10000.0, max_value=22000.0),
                  sine=hypothesis.strategies.booleans(),
                  sampling_rate=hypothesis.strategies.floats(min_value=44100.0, max_value=96000.0),
                  length=hypothesis.strategies.integers(min_value=256, max_value=2 ** 14))
def test_compare_with_other_formula(start_frequency, stop_frequency, sine, sampling_rate, length):
    """Compares the current implementation with a sweep, that is created by a different but equivalent formula."""
    if sine:
        phase = 0.0
    else:
        phase = math.pi / 2.0
    sweep1 = sumpf.ExponentialSweep(start_frequency=start_frequency,
                                    stop_frequency=stop_frequency,
                                    phase=phase,
                                    sampling_rate=sampling_rate,
                                    length=length)
    sweep2 = other_sweep_formula(start_frequency=start_frequency,
                                 stop_frequency=stop_frequency,
                                 sampling_rate=sampling_rate,
                                 length=length,
                                 sine=sine)
    assert sweep1.channels() == pytest.approx(sweep2.channels(), abs=1e-7)


def test_min_and_max_frequencies():
    """Tests if the methods for computing the minimum and the maximum frequencies work as expected"""
    r = random.Random()
    start_frequency = r.uniform(1.0, 300.0)
    stop_frequency = r.uniform(5 * start_frequency, 10000.0)
    sampling_rate = r.uniform(3 * stop_frequency, 56000.0)
    length = r.randint(2 ** 10, 2 ** 16) * 2    # make sure, this is an even number
    interval = (r.uniform(0.0, 0.2), r.uniform(0.8, 1.0))
    start, stop = sumpf_internal.index(interval, length)
    frequency_ratio = stop_frequency / start_frequency
    sweep_length = stop - start
    sweep = sumpf.ExponentialSweep(start_frequency=start_frequency,
                                   stop_frequency=stop_frequency,
                                   interval=interval,
                                   sampling_rate=sampling_rate,
                                   length=length)
    assert sweep.minimum_frequency() == pytest.approx(start_frequency * frequency_ratio ** (-start / sweep_length))
    assert sweep.maximum_frequency() == pytest.approx(stop_frequency * frequency_ratio ** ((length - stop) / sweep_length))     # pylint: disable=line-too-long; nothing complicated here, only long variable names


def test_instantaneous_frequency():
    """Tests the instantaneous_frequency method"""
    r = random.Random()
    start_frequency = r.uniform(1.0, 300.0)
    stop_frequency = r.uniform(5 * start_frequency, 10000.0)
    sampling_rate = r.uniform(3 * stop_frequency, 56000.0)
    length = r.randint(2 ** 10, 2 ** 16) * 2    # make sure, this is an even number
    interval = (r.uniform(0.0, 0.2), r.uniform(0.8, 1.0))
    sweep = sumpf.ExponentialSweep(start_frequency=start_frequency,
                                   stop_frequency=stop_frequency,
                                   interval=interval,
                                   sampling_rate=sampling_rate,
                                   length=length)
    assert sweep.instantaneous_frequency(0) == sweep.minimum_frequency()
    assert sweep.instantaneous_frequency(sweep.duration()) == sweep.maximum_frequency()
    diff = numpy.diff(sweep.instantaneous_frequency(sweep.time_samples()))
    assert (diff > 0).all()     # the frequency should increase monotonically


def test_interval():
    """Tests if the interval functionality of the ExponentialSweep class works"""
    sweep1 = sumpf.ExponentialSweep(interval=(200, 800), length=2 ** 10)
    sweep2 = sumpf.ExponentialSweep(length=600)
    assert sweep1[:, 200:800].channels() == pytest.approx(sweep2.channels())
    sweep3 = sumpf.ExponentialSweep(interval=(0.1, -0.1), length=2 ** 10)
    sweep4 = sumpf.ExponentialSweep(length=int(round(2 ** 10 * 0.9) - round(2 ** 10 * 0.1)))
    assert sweep3[:, 0.1:-0.1].channels() == pytest.approx(sweep4.channels())


def test_harmonic_impulse_response():
    """Does some trivial tests with the harmonic_impulse_response method"""
    # create a sweep, an inverse sweep and a distorted version of the sweep
    sweep = sumpf.ExponentialSweep(start_frequency=20.0, stop_frequency=7800.0, sampling_rate=48000, length=2 ** 14)
    inverse = sumpf.InverseExponentialSweep(start_frequency=20.0, stop_frequency=7800.0, sampling_rate=48000, length=2 ** 14)   # pylint: disable=line-too-long
    distorted = 0.5 * sweep ** 3 - 0.6 * sweep ** 2 + 0.1 * sweep + 0.02
    lowpass = sumpf.ButterworthFilter(cutoff_frequency=1000.0, order=16, highpass=False)
    highpass = sumpf.ButterworthFilter(cutoff_frequency=1000.0, order=16, highpass=True)
    response = distorted * highpass * lowpass
    # test with non-circular deconvolution
    impulse_response = response.convolve(inverse, mode=sumpf.Signal.convolution_modes.SPECTRUM_PADDED)
    h1 = sweep.harmonic_impulse_response(impulse_response=impulse_response, harmonic=1)
    h2 = sweep.harmonic_impulse_response(impulse_response=impulse_response, harmonic=2, length=h1.length())
    h3 = sweep.harmonic_impulse_response(impulse_response=impulse_response, harmonic=3)
    assert h1.length() == h2.length()   # check if the length parameter has worked
    assert h3.length() < h2.length()    # the impulse responses of the higher order harmonics are shorter
    harmonics = sumpf.MergeSignals([h1, h2, h3]).output()
    spectrum = harmonics.fourier_transform()
    magnitude = spectrum.magnitude()
    max_indices = magnitude.argmax(axis=1)
    assert max(max_indices) - min(max_indices) <= 1     # the maximums of all harmonics' transfer functions should be roughly the same
    assert max_indices.mean() * spectrum.resolution() == pytest.approx(1000.0, rel=1e-3)    # the maximums should be around 1000Hz
    # test with circular deconvolution
    impulse_response = response.convolve(inverse, mode=sumpf.Signal.convolution_modes.SPECTRUM).shift(None)
    h1 = sweep.harmonic_impulse_response(impulse_response=impulse_response, harmonic=1, length=2048)
    h2 = sweep.harmonic_impulse_response(impulse_response=impulse_response, harmonic=2, length=2048)
    h3 = sweep.harmonic_impulse_response(impulse_response=impulse_response, harmonic=3, length=2048)
    assert h1.length() == 2048
    assert h2.length() == 2048
    assert h3.length() == 2048
    harmonics = sumpf.MergeSignals([h1, h2, h3]).output()
    spectrum = harmonics.fourier_transform()
    magnitude = spectrum.magnitude()
    max_indices = magnitude.argmax(axis=1)
    assert max(max_indices) - min(max_indices) <= 5     # the maximums of all harmonics' transfer functions should be roughly the same
    assert max_indices.mean() * spectrum.resolution() == pytest.approx(1000.0, rel=8e-3)    # the maximums should be around 1000Hz


@pytest.mark.skip("this benchmark might fail depending on the system's load")
def test_benchmark():
    """Tests if SuMPF's implementation is faster than a pure NumPy implementation"""
    # pylint: disable=wrong-spelling-in-comment
    logging.info("benchmarking SuMPF's ExponentialSweep and a pure NumPy implementation")
    # test with a very short sweep, where NumExpr's speed cannot compensate for the time it takes to parse the formula and SuMPF switches to a pure NumPy implementation
#    numpy_time = timeit.timeit("numpy_sweep(length=256)", globals=globals(), number=1000)
#    sumpf_time = timeit.timeit("sumpf.ExponentialSweep(length=256)", globals=globals(), number=1000)
#    logging.info("  performance gain with 256 samples:   {:6.2f}% (NumPy: {:6.2f}ms, SuMPF: {:6.2f}ms)".format(100 * (numpy_time - sumpf_time) / numpy_time, 1000 * numpy_time, 1000 * sumpf_time))
#    assert sumpf_time <= numpy_time * 1.1   # since both implementations are very much the same, their run-times are expected to be equal
    # test with a longer sweep, where NumExpr can shine
    numpy_time = timeit.timeit("numpy_sweep(length=16384)", globals=globals(), number=100)
    sumpf_time = timeit.timeit("sumpf.ExponentialSweep(length=16384)", globals=globals(), number=100)
    logging.info("  performance gain with 16384 samples: {:6.2f}% (NumPy: {:6.2f}ms, SuMPF: {:6.2f}ms)".format(100 * (numpy_time - sumpf_time) / numpy_time, 1000 * numpy_time, 1000 * sumpf_time))
    assert sumpf_time < numpy_time

##########################################
# test the InverseExponentialSweep class #
##########################################


def test_convolution_with_sweep():
    """Tests if the convolution with the respective sweep results in a unit impulse"""
    for kwargs in ({"start_frequency": 300.0, "length": 1024},
                   {"stop_frequency": 12747.0, "length": 1024},
                   {"phase": 2.9, "length": 1024},
                   {"interval": (0.15, 0.9), "length": 2048},
                   {"stop_frequency": 5000.0, "sampling_rate": 18312.7, "length": 1024}):
        a, b = kwargs.get("interval", (0, 1.0))
        sweep = sumpf.ExponentialSweep(**kwargs)
        isweep = sumpf.InverseExponentialSweep(**kwargs)
        impulse = sweep[:, a:b].convolve(isweep[:, a:b])
        peak = max(impulse.channels()[0])
        peak_index = impulse.channels()[0].argmax()
        other = max(max(abs(impulse.channels()[0, 0:-impulse.offset() - 1])),   # the maximum of the absolute values of the impulse except
                    max(abs(impulse.channels()[0, -impulse.offset() + 2:])))    # for the sample at t=0 and the two neighboring samples
        assert abs(peak - 1.0) < 0.005          # the highest peak should be one (unit impulse)
        assert peak_index == -impulse.offset()  # the highest peak should be at time value 0
        assert peak > 5 * abs(other)            # other peaks and notches should be much smaller than the impulse


def test_min_and_max_frequencies_inversed():
    """Tests if the methods for computing the minimum and the maximum frequencies work as expected"""
    r = random.Random()
    start_frequency = r.uniform(1.0, 300.0)
    stop_frequency = r.uniform(5 * start_frequency, 10000.0)
    sampling_rate = r.uniform(3 * stop_frequency, 56000.0)
    length = r.randint(256, 512) * 2    # make sure, this is an even number
    sweep = sumpf.ExponentialSweep(start_frequency=start_frequency,
                                   stop_frequency=stop_frequency,
                                   interval=(0.15, 0.9),
                                   sampling_rate=sampling_rate,
                                   length=length)
    isweep = sumpf.InverseExponentialSweep(start_frequency=start_frequency,
                                           stop_frequency=stop_frequency,
                                           interval=(0.1, 0.85),
                                           sampling_rate=sampling_rate,
                                           length=length)
    assert isweep.minimum_frequency() == pytest.approx(sweep.minimum_frequency())
    assert isweep.maximum_frequency() == pytest.approx(sweep.maximum_frequency())


def test_instantaneous_frequency_inversed():
    """Tests the instantaneous_frequency method"""
    r = random.Random()
    start_frequency = r.uniform(1.0, 300.0)
    stop_frequency = r.uniform(5 * start_frequency, 10000.0)
    sampling_rate = r.uniform(3 * stop_frequency, 56000.0)
    length = r.randint(2 ** 10, 2 ** 16) * 2    # make sure, this is an even number
    interval = (r.uniform(0.0, 0.2), r.uniform(0.8, 1.0))
    sweep = sumpf.InverseExponentialSweep(start_frequency=start_frequency,
                                          stop_frequency=stop_frequency,
                                          interval=interval,
                                          sampling_rate=sampling_rate,
                                          length=length)
    assert sweep.instantaneous_frequency(0.0) == sweep.maximum_frequency()
    assert sweep.instantaneous_frequency(sweep.duration()) == sweep.minimum_frequency()
    diff = numpy.diff(sweep.instantaneous_frequency(sweep.time_samples()))
    assert (diff < 0).all()     # the frequency should decrease monotonically


def test_interval_inversed():
    """Tests if the interval functionality of the :class:`~sumpf.InverseExponentialSweep` class works"""
    sweep1 = sumpf.InverseExponentialSweep(interval=(200, 800), length=2 ** 10)
    sweep2 = sumpf.InverseExponentialSweep(length=600)
    assert sweep1[:, 200:800].channels() == pytest.approx(sweep2.channels())
    sweep3 = sumpf.InverseExponentialSweep(interval=(0.1, -0.1), length=2 ** 10)
    sweep4 = sumpf.InverseExponentialSweep(length=int(round(2 ** 10 * 0.9) - round(2 ** 10 * 0.1)))
    assert sweep3[:, 0.1:-0.1].channels() == pytest.approx(sweep4.channels())

##################################################
# helper functions, that are used by these tests #
##################################################


def other_sweep_formula(start_frequency, stop_frequency, sampling_rate, length, sine=True):
    """Generates a sweep with a different but equivalent formula, than that in SuMPF"""
    f0 = start_frequency
    fT = stop_frequency
    T = length / sampling_rate
    l = 1.0 / (T * math.log(math.e, fT / f0))
    f = 2.0 * math.pi * f0 / l
    t = numpy.linspace(0.0, (length - 1) / sampling_rate / T, length)
    array = t
    array = numpy.power((fT / f0), t, out=array)
    array -= 1.0
    array *= f
    if sine:
        numpy.sin(array, out=array)
    else:
        numpy.cos(array, out=array)
    return sumpf.Signal(channels=array.reshape(1, len(array)),
                        sampling_rate=sampling_rate,
                        offset=0,
                        labels=("Sweep",))


def numpy_sweep(start_frequency=20.0,
                stop_frequency=20000.0,
                phase=0.0,
                interval=(0, 1.0),
                sampling_rate=48000.0,
                length=2 ** 16):
    """A pure NumPy implementation of the ExponentialSweep for benchmarking.
    See the ExponentialSweep class for documentation of the parameters.
    """
    # allocate shared memory for the channels
    array = sharedctypes.RawArray(ctypes.c_double, length)
    channels = numpy.frombuffer(array, dtype=numpy.float64).reshape((1, length))
    # generate the sweep
    start, stop = sumpf_internal.index(interval, length)
    sweep_offset = float(start / sampling_rate)
    sweep_duration = (stop - start) / sampling_rate
    frequency_ratio = stop_frequency / start_frequency
    l = sweep_duration / math.log(frequency_ratio)
    a = 2.0 * math.pi * start_frequency * l
    t = numpy.linspace(-sweep_offset, (length - 1) / sampling_rate - sweep_offset, length)
    array = t
    array /= l
    numpy.expm1(array, out=array)
    array *= a
    array += phase
    numpy.sin(array, out=channels[0, :])
    # fake store some additional values, because these values are actually stored in the constructor of the sweep
    _ = start_frequency * frequency_ratio ** (-sweep_offset / sweep_duration)                       # noqa: F841
    _ = start_frequency * frequency_ratio ** ((sweep_duration - sweep_offset) / sweep_duration)     # noqa: F841
    return sumpf.Signal(channels=channels, sampling_rate=sampling_rate, offset=0, labels=("Sweep",))
