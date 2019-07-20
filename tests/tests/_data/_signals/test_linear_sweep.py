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
from multiprocessing import sharedctypes
import timeit
import hypothesis
import numpy
import pytest
import sumpf
import sumpf._internal as sumpf_internal

##############################
# test the LinearSweep class #
##############################


def test_spectrogram():
    """Checks the linear frequency increase by finding the maximums in the spectrogram."""
    pytest.importorskip("scipy")
    sweep = sumpf.LinearSweep()
    spectrogram = sweep.short_time_fourier_transform(window=2048)
    frequencies = sweep.instantaneous_frequency(spectrogram.time_samples())
    for c in spectrogram.magnitude():
        maximums = numpy.multiply(c.argmax(axis=0), spectrogram.resolution())
        diff = numpy.abs(frequencies - maximums)
        assert (diff[1:-1] <= spectrogram.resolution() * 1.2).all()


@hypothesis.given(start_frequency=hypothesis.strategies.floats(min_value=1e-15, max_value=9999.0),
                  stop_frequency=hypothesis.strategies.floats(min_value=10000.0, max_value=22000.0),
                  phase=hypothesis.strategies.floats(min_value=-2.0 * math.pi, max_value=2.0 * math.pi),
                  sampling_rate=hypothesis.strategies.floats(min_value=44100.0, max_value=96000.0),
                  length=hypothesis.strategies.integers(min_value=256, max_value=2 ** 14))
@hypothesis.settings(deadline=None)
def test_compare_with_numpy_implementation(start_frequency, stop_frequency, phase, sampling_rate, length):
    """Compares the current implementation with a sweep, that is created with a pure numpy implementation."""
    sweep1 = sumpf.LinearSweep(start_frequency=start_frequency,
                               stop_frequency=stop_frequency,
                               phase=phase,
                               sampling_rate=sampling_rate,
                               length=length)
    sweep2 = numpy_sweep(start_frequency=start_frequency,
                         stop_frequency=stop_frequency,
                         phase=phase,
                         sampling_rate=sampling_rate,
                         length=length)
    assert sweep1.channels() == pytest.approx(sweep2.channels(), abs=1e-7)


@hypothesis.given(start_frequency=hypothesis.strategies.floats(min_value=1.0, max_value=300.0),
                  stop_frequency=hypothesis.strategies.floats(min_value=1000.0, max_value=10000.0),
                  sampling_rate=hypothesis.strategies.floats(min_value=21000.0, max_value=60000.0),
                  interval_start=hypothesis.strategies.floats(min_value=0.0, max_value=0.2),
                  interval_stop=hypothesis.strategies.floats(min_value=0.8, max_value=1.0),
                  length=hypothesis.strategies.integers(min_value=2 ** 10, max_value=2 ** 16))
def test_min_and_max_frequencies(start_frequency, stop_frequency, sampling_rate,
                                 length, interval_start, interval_stop):
    """Tests if the methods for computing the minimum and the maximum frequencies work as expected"""
    interval = (interval_start, interval_stop)
    start, stop = sumpf_internal.index(interval, length)
    sweep_length = stop - start
    frequency_range = stop_frequency - start_frequency
    sweep = sumpf.LinearSweep(start_frequency=start_frequency,
                              stop_frequency=stop_frequency,
                              interval=interval,
                              sampling_rate=sampling_rate,
                              length=length)
    assert sweep.minimum_frequency() == pytest.approx(start_frequency + frequency_range * (-start / sweep_length))
    assert sweep.maximum_frequency() == pytest.approx(stop_frequency + frequency_range * ((length - stop) / sweep_length))  # pylint: disable=line-too-long; nothing complicated here, only long variable names


@hypothesis.given(start_frequency=hypothesis.strategies.floats(min_value=1.0, max_value=300.0),
                  stop_frequency=hypothesis.strategies.floats(min_value=1000.0, max_value=10000.0),
                  sampling_rate=hypothesis.strategies.floats(min_value=21000.0, max_value=60000.0),
                  interval_start=hypothesis.strategies.floats(min_value=0.0, max_value=0.2),
                  interval_stop=hypothesis.strategies.floats(min_value=0.8, max_value=1.0),
                  length=hypothesis.strategies.integers(min_value=2 ** 10, max_value=2 ** 16))
def test_instantaneous_frequency(start_frequency, stop_frequency, sampling_rate,
                                 length, interval_start, interval_stop):
    """Tests the instantaneous_frequency method of the LinearSweep class"""
    sweep = sumpf.LinearSweep(start_frequency=start_frequency,
                              stop_frequency=stop_frequency,
                              interval=(interval_start, interval_stop),
                              sampling_rate=sampling_rate,
                              length=length)
    assert sweep.instantaneous_frequency(0.0) == sweep.minimum_frequency()
    assert sweep.instantaneous_frequency(round(interval_start * length) / sampling_rate) == pytest.approx(start_frequency)  # pylint: disable=line-too-long
    assert sweep.instantaneous_frequency(round(interval_stop * length) / sampling_rate) == pytest.approx(stop_frequency)    # pylint: disable=line-too-long
    assert sweep.instantaneous_frequency(sweep.duration()) == sweep.maximum_frequency()
    diff = numpy.diff(sweep.instantaneous_frequency(sweep.time_samples()))
    assert (diff > 0).all()     # the frequency should increase monotonically


def test_interval():
    """Tests if the interval functionality of the LinearSweep class works"""
    sweep1 = sumpf.LinearSweep(interval=(200, 800), length=2 ** 10)
    sweep2 = sumpf.LinearSweep(length=600)
    assert sweep1[:, 200:800].channels() == pytest.approx(sweep2.channels())
    sweep3 = sumpf.LinearSweep(interval=(0.1, -0.1), length=2 ** 10)
    sweep4 = sumpf.LinearSweep(length=int(round(2 ** 10 * 0.9) - round(2 ** 10 * 0.1)))
    assert sweep3[:, 0.1:-0.1].channels() == pytest.approx(sweep4.channels())


@pytest.mark.skip("this benchmark might fail depending on the system's load")
def test_benchmark():
    """Tests if SuMPF's implementation is faster than a pure NumPy implementation"""
    # pylint: disable=wrong-spelling-in-comment
    logging.info("benchmarking SuMPF's LinearSweep and a pure NumPy implementation")
    # test with a very short sweep, where NumExpr's speed cannot compensate for the time it takes to parse the formula and SuMPF switches to a pure NumPy implementation
    numpy_time = timeit.timeit("numpy_sweep(length=512)", globals=globals(), number=1000)
    sumpf_time = timeit.timeit("sumpf.LinearSweep(length=512)", globals=globals(), number=2000)
    numpy_time += timeit.timeit("numpy_sweep(length=512)", globals=globals(), number=1000)
    logging.info("  performance gain with 512 samples:   {:6.2f}% (NumPy: {:6.2f}ms, SuMPF: {:6.2f}ms)".format(100 * (numpy_time - sumpf_time) / numpy_time, 1000 * numpy_time, 1000 * sumpf_time))
#    assert sumpf_time <= numpy_time * 1.1   # since both implementations are very much the same, their run-times are expected to be equal
    # test with a longer sweep, where NumExpr can shine
    numpy_time = timeit.timeit("numpy_sweep(length=65536)", globals=globals(), number=100)
    sumpf_time = timeit.timeit("sumpf.LinearSweep(length=65536)", globals=globals(), number=200)
    numpy_time += timeit.timeit("numpy_sweep(length=65536)", globals=globals(), number=100)
    logging.info("  performance gain with 65536 samples: {:6.2f}% (NumPy: {:6.2f}ms, SuMPF: {:6.2f}ms)".format(100 * (numpy_time - sumpf_time) / numpy_time, 1000 * numpy_time, 1000 * sumpf_time))
    assert sumpf_time < numpy_time

##########################################
# test the InverseExponentialSweep class #
##########################################


def test_convolution_with_sweep():
    """Tests if the convolution with the respective sweep results in a unit impulse"""
    for kwargs in ({"start_frequency": 300.0, "length": 1024},
                   {"stop_frequency": 12747.0, "length": 8192},
                   {"phase": 2.4, "length": 8192},
                   {"interval": (0.15, 0.9), "length": 8192},
                   {"stop_frequency": 5000.0, "sampling_rate": 18312.7, "length": 4096}):
        a, b = kwargs.get("interval", (0, 1.0))
        sweep = sumpf.LinearSweep(**kwargs)
        isweep = sumpf.InverseLinearSweep(**kwargs)
        impulse = sweep[:, a:b].convolve(isweep[:, a:b])
        peak = max(impulse.channels()[0])
        peak_index = impulse.channels()[0].argmax()
        other = max(max(abs(impulse.channels()[0, 0:-impulse.offset() - 1])),   # the maximum of the absolute values of the impulse except
                    max(abs(impulse.channels()[0, -impulse.offset() + 2:])))    # for the sample at t=0 and the two neighboring samples
        assert abs(peak - 1.0) < 0.005          # the highest peak should be one (unit impulse)
        assert peak_index == -impulse.offset()  # the highest peak should be at time value 0
        assert peak > 5 * abs(other)            # other peaks and notches should be much smaller than the impulse


def test_spectrogram_inversed():
    """Checks the linear frequency increase by finding the maximums in the spectrogram."""
    pytest.importorskip("scipy")
    isweep = sumpf.InverseLinearSweep()
    spectrogram = isweep.shift(None).short_time_fourier_transform(window=2048)
    frequencies = isweep.instantaneous_frequency(spectrogram.time_samples())
    for c in spectrogram.magnitude():
        maximums = numpy.multiply(c.argmax(axis=0), spectrogram.resolution())
        diff = numpy.abs(frequencies - maximums)
        assert (diff[1:-1] <= spectrogram.resolution() * 1.2).all()


@hypothesis.given(start_frequency=hypothesis.strategies.floats(min_value=1.0, max_value=300.0),
                  stop_frequency=hypothesis.strategies.floats(min_value=1000.0, max_value=10000.0),
                  sampling_rate=hypothesis.strategies.floats(min_value=21000.0, max_value=60000.0),
                  interval_start=hypothesis.strategies.floats(min_value=0.0, max_value=0.2),
                  interval_stop=hypothesis.strategies.floats(min_value=0.8, max_value=1.0),
                  length=hypothesis.strategies.integers(min_value=2 ** 10, max_value=2 ** 16))
def test_min_and_max_frequencies_inversed(start_frequency, stop_frequency, sampling_rate,
                                          length, interval_start, interval_stop):
    """Tests if the methods for computing the minimum and the maximum frequencies work as expected"""
    start, stop = sumpf_internal.index((interval_start, interval_stop), length)
    sweep = sumpf.LinearSweep(start_frequency=start_frequency,
                              stop_frequency=stop_frequency,
                              interval=(start, stop),
                              sampling_rate=sampling_rate,
                              length=length)
    isweep = sumpf.InverseLinearSweep(start_frequency=start_frequency,
                                      stop_frequency=stop_frequency,
                                      interval=(length - stop, length - start),
                                      sampling_rate=sampling_rate,
                                      length=length)
    assert isweep.minimum_frequency() == pytest.approx(sweep.minimum_frequency())
    assert isweep.maximum_frequency() == pytest.approx(sweep.maximum_frequency())


@hypothesis.given(start_frequency=hypothesis.strategies.floats(min_value=1.0, max_value=300.0),
                  stop_frequency=hypothesis.strategies.floats(min_value=1000.0, max_value=10000.0),
                  sampling_rate=hypothesis.strategies.floats(min_value=21000.0, max_value=60000.0),
                  interval_start=hypothesis.strategies.floats(min_value=0.0, max_value=0.2),
                  interval_stop=hypothesis.strategies.floats(min_value=0.8, max_value=1.0),
                  length=hypothesis.strategies.integers(min_value=2 ** 10, max_value=2 ** 16))
def test_instantaneous_frequency_inversed(start_frequency, stop_frequency, sampling_rate,
                                          length, interval_start, interval_stop):
    """Tests the instantaneous_frequency method of the InverseLinearSweep class"""
    sweep = sumpf.InverseLinearSweep(start_frequency=start_frequency,
                                     stop_frequency=stop_frequency,
                                     interval=(interval_start, interval_stop),
                                     sampling_rate=sampling_rate,
                                     length=length)
    assert sweep.instantaneous_frequency(0.0) == sweep.maximum_frequency()
    assert sweep.instantaneous_frequency(round(interval_start * length) / sampling_rate) == pytest.approx(stop_frequency)   # pylint: disable=line-too-long
    assert sweep.instantaneous_frequency(round(interval_stop * length) / sampling_rate) == pytest.approx(start_frequency)   # pylint: disable=line-too-long
    assert sweep.instantaneous_frequency(sweep.duration()) == sweep.minimum_frequency()
    diff = numpy.diff(sweep.instantaneous_frequency(sweep.time_samples()))
    assert (diff < 0).all()     # the frequency should decrease monotonically


def test_interval_inversed():
    """Tests if the interval functionality of the :class:`~sumpf.InverseLinearSweep` class works"""
    sweep1 = sumpf.InverseLinearSweep(interval=(200, 800), length=2 ** 10)
    sweep2 = sumpf.InverseLinearSweep(length=600)
    assert sweep1[:, 200:800].channels() == pytest.approx(sweep2.channels())
    sweep3 = sumpf.InverseLinearSweep(interval=(0.1, -0.1), length=2 ** 10)
    sweep4 = sumpf.InverseLinearSweep(length=int(round(2 ** 10 * 0.9) - round(2 ** 10 * 0.1)))
    assert sweep3[:, 0.1:-0.1].channels() == pytest.approx(sweep4.channels())

##################################################
# helper functions, that are used by these tests #
##################################################


def numpy_sweep(start_frequency=20.0,
                stop_frequency=20000.0,
                phase=0.0,
                interval=(0, 1.0),
                sampling_rate=48000.0,
                length=2 ** 16):
    """A pure NumPy implementation of the LinearSweep for benchmarking.
    See the LinearSweep class for documentation of the parameters.
    """
    # allocate shared memory for the channels
    array = sharedctypes.RawArray(ctypes.c_double, length)
    channels = numpy.frombuffer(array, dtype=numpy.float64).reshape((1, length))
    # compute some parameters
    start, stop = sumpf_internal.index(interval, length)
    sweep_offset = start / sampling_rate
    sweep_length = stop - start
    T = sweep_length / sampling_rate
    k = (stop_frequency - start_frequency) / T
    a = 2.0 * math.pi * start_frequency
    b = math.pi * k
    t = numpy.linspace(-sweep_offset, (length - 1) / sampling_rate - sweep_offset, length)  # the time values for the samples
    # generate the sweep
    array = t * t
    array *= b
    array += a * t
    array += phase
    numpy.sin(array, out=channels[0, :])
    # fake store some additional values, because these values are actually stored in the constructor of the sweep
    _ = start_frequency + k * (-sweep_offset / T)       # noqa: F841
    _ = start_frequency + k * ((T - sweep_offset) / T)  # noqa: F841
    return sumpf.Signal(channels=channels, sampling_rate=sampling_rate, offset=0, labels=("Sweep",))
