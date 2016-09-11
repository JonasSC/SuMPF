# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sumpf

try:
    import numpy
except ImportError:
    numpy = sumpf.helper.numpydummy



class Level(object):
    """
    A class for calculating the level of a signal.

    The levels are computed individually for the channels and returned as a tuple.
    The computation of the level can be adjusted with the parameters power and
    root, which denote the exponent with which the powers of the input Signal's
    samples are computed before the integration and the degree of the root that
    is computed with the integrated values:
        level = (integrate(signal ** power)) ** (1/root)
    Here are some common examples for the coice of power and root:
        Computing the average amplitudes of the channels:  power = 1.0, root=1.0
        Computing the signal power of the channels:        power = 2.0, root=1.0
        Computing the RMS-level of the channels:           power = 2.0, root=2.0
    """
    def __init__(self, signal=None, power=2.0, root=2.0):
        """
        @param signal: the input Signal
        @param offset: an float offset that shall be added to the integrated signal, or NO_DC to avoid a dc-offset in the output Signal
        """
        if signal is None:
            self.__signal = sumpf.Signal()
        else:
            self.__signal = signal
        self.__power = power
        self.__root = root

    @sumpf.Input(sumpf.Signal, "GetLevel")
    def SetSignal(self, signal):
        """
        Sets the input Signal.
        @param signal: the input Signal
        """
        self.__signal = signal

    @sumpf.Input(float, "GetLevel")
    def SetPower(self, power):
        """
        Sets the exponent with which the powers of the input Signal's samples
        are computed before the integration.
        @param power: a float
        """
        self.__power = power

    @sumpf.Input(float, "GetLevel")
    def SetRoot(self, root):
        """
        Sets the degree of the root that is computed with the integrated values.
        @param root: a root
        """
        self.__root = root

    @sumpf.Output(tuple)
    def GetLevel(self):
        """
        Computes the level of the input Signal and returns it.
        @retval : a tuple with the individual level values for the signal's channels
        """
        powered = numpy.power(self.__signal.GetChannels(), self.__power)
        integrated = (numpy.mean(c) for c in powered)
        rooted = tuple(c ** (1.0 / self.__root) for c in integrated)
        return rooted

