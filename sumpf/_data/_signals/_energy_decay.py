# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2021 Jonas Schulte-Coerne
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

"""Contains the :class:`~sumpf.EnergyDecayCurve` class."""

import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("EnergyDecayCurve",)


class EnergyDecayCurve(Signal):
    """A class for computing an energy decay curve from an impulse response.

    Such an energy decay curve is sometimes also called "Schroeder curve". It is
    computed as the tail integral of the squared impulse response. Let C(t) be the
    energy decay curve and h(t) be the impulse response, then the computation is
    as follows:

    .. math::

       C(t) = \\int_t^\\infty h(\\tau) d\\tau


    This class also provides methods to analyze the reverberation time of the system,
    from which the given impulse response was recorded.

    The instances will have the same sampling rate, offset and labels as the given
    impulse response.
    """

    def __init__(self, impulse_response):
        """
        :param impulse_response: the impulse response :class:`~sumpf.Signal`, from
                                 which this energy decay curve shall be computed.
        """
        channels = sumpf_internal.allocate_array(shape=impulse_response.shape())
        numpy.square(impulse_response.channels(), out=channels)
        numpy.cumsum(channels[:, ::-1], axis=1, out=channels[:, ::-1])
        Signal.__init__(self,
                        channels=channels,
                        sampling_rate=impulse_response.sampling_rate(),
                        offset=impulse_response.offset(),
                        labels=impulse_response.labels())

    def reverberation_time(self, start, stop):
        """Computes the reverberation time from the segment of the energy decay
        curve, that is specified by the start and stop parameters.

        In order to produce a meaningful result, the start and stop parameters must
        frame the segment, in which the semi-logarithmic plot (dB plot) of the energy
        decay curve falls linearly over time.

        The given start and stop parameters are the indices of the respective samples
        of the signal. These indices can be given as (negative) integers, which
        work just like :class:`list` indices, or as floats between -1.0 and 1.0,
        which will be scaled to the length of the signal.

        :param start: the sample index of the first sample in the segment
        :param stop: the sample index of the first sample after the segment
        :returns: a tuple of float reverberation times
        """
        return tuple(-60.0 / m / self.sampling_rate() for m, _ in self.__solve(start, stop))

    def decay_model(self, start, stop):
        """Computes an exponential decay curve, that is fitted to the segment of
        the energy decay curve, which is specified by the start and stop parameters.

        The :class:`~sumpf.Signal`, that is returned by this method, can be plotted
        alongside this energy decay curve in order to check, if the reverberation
        time, that is computed from the specified segment, is realistic.

        In order to produce a meaningful result, the start and stop parameters must
        frame the segment, in which the semi-logarithmic plot (dB plot) of the energy
        decay curve falls linearly over time.

        The given start and stop parameters are the indices of the respective samples
        of the signal. These indices can be given as (negative) integers, which
        work just like :class:`list` indices, or as floats between -1.0 and 1.0,
        which will be scaled to the length of the signal.

        :param start: the sample index of the first sample in the segment
        :param stop: the sample index of the first sample after the segment
        :returns: a :class:`~sumpf.Signal`
        """
        channels = sumpf_internal.allocate_array(shape=self.shape())
        i = numpy.arange(self._length)
        for c, (m, n) in zip(channels, self.__solve(start, stop)):
            c[:] = numpy.power(10.0, (m / 10.0) * i + (n / 10.0))
        return Signal(channels=channels,
                      sampling_rate=self.sampling_rate(),
                      offset=self.offset(),
                      labels=self.labels())

    def __solve(self, start, stop):
        """A helper method, that computes a least squares solution for the ``m``
        and ``n`` parameters of the linear decay of the dB-values:

        Let ``y(i)`` be the dB-value of the energy decay curve at sample ``i``,
        then ``m`` and ``n`` are used as follows to compute the linear decay:

        .. math::

           y(i) = m \\cdot i + n


        :param start: the sample index of the first sample in the segment
        :param stop: the sample index of the first sample after the segment
        :returns: a generator, that yields (m, n) tuples (actually :func:`numpy.array` s)
                  for each channel
        """
        start_index = sumpf_internal.index(start, length=self._length)
        stop_index = sumpf_internal.index(stop, length=self._length)
        i = numpy.arange(start_index, stop_index)
        for c in self._channels:
            x = numpy.empty(shape=(len(i), 2))
            x[:, 0] = i
            x[:, 1] = 1.0
            y = 10.0 * numpy.log10(c[start_index:stop_index])
            yield numpy.linalg.lstsq(x, y, rcond=None)[0]
