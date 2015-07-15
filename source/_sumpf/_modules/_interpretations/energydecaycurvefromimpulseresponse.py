# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
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


class EnergyDecayCurveFromImpulseResponse(object):
    """
    This module calculates the energy decay curve or schroeder curve from a given
    impulse response.
    To get the dB curve, in which the linear slope can be found, that is used to
    calculate the reverberation time, the output of this class has to be processed
    by a LogarithmSignal module and then by a AmplifySignal module with a factor
    of 10.
    The output of this module is an energy Signal, rather than a sound pressure
    Signal, so it does not have negative samples. Please do not attempt to play
    it back through the sound card, as it will certainly have a massive dc offset,
    that might damage the loudspeakers.
    """
    def __init__(self, impulseresponse=None):
        """
        @param impulseresponse: the impulse response from which the energy decay curve shall be calculated
        """
        if impulseresponse is None:
            self.__impulseresponse = sumpf.Signal()
        else:
            self.__impulseresponse = impulseresponse

    @sumpf.Input(sumpf.Signal, "GetEnergyDecayCurve")
    def SetImpulseResponse(self, impulseresponse):
        """
        Sets the impulse response from which the energy decay curve shall be calculated.
        @param impulseresponse: a Signal instance that contains an impulse response
        """
        self.__impulseresponse = impulseresponse

    @sumpf.Output(sumpf.Signal)
    def GetEnergyDecayCurve(self):
        """
        Returns the calculated energy decay curve.
        @retval : a Signal that contains the calculated energy decay curve
        """
        channels = []
        for c in self.__impulseresponse.GetChannels():
            channel = [0.0] * len(c)
            energy = 0.0
            for i in range(len(c) - 1, -1, -1):
                energy += c[i] ** 2
                channel[i] = energy
            channels.append(tuple(channel))
        return sumpf.Signal(channels=tuple(channels), samplingrate=self.__impulseresponse.GetSamplingRate(), labels=self.__impulseresponse.GetLabels())

