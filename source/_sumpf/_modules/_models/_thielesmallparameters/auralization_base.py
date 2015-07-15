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


class ThieleSmallParameterAuralization(object):
    """
    Base class for synthesizing loudspeaker responses to a given input voltage
    signal. The loudspeaker is characterized by a ThieleSmallParameters instance.
    """
    def __init__(self, thiele_small_parameters=sumpf.ThieleSmallParameters(), voltage_signal=None, listener_distance=1.0, medium_density=1.2041):
        """
        @param thiele_small_parameters: a ThieleSmallParameters instance
        @param voltage_signal: a signal for the input voltage of the loudspeaker
        @param listener_distance: a float value for the distance between the loudspeaker and the point where the radiated sound is received in meters
        @param medium_density: a float value for the density of the medium, in which the loudspeaker radiates sound (probably air) in kilograms per cubic meter
        """
        # input parameters
        self._thiele_small = thiele_small_parameters
        self._voltage = voltage_signal
        if self._voltage is None:
            self._voltage = sumpf.Signal()
        self._listener_distance = listener_distance
        self._medium_density = medium_density
        # output Signals
        self.__excursion = None
        self.__velocity = None
        self.__acceleration = None
        self.__current = None
        self.__sound_pressure = None
        # state variable
        self._recalculate = True

    @sumpf.Input(sumpf.ThieleSmallParameters, ("GetExcursion", "GetVelocity", "GetAcceleration", "GetCurrent", "GetSoundPressure"))
    def SetThieleSmallParameters(self, parameters):
        """
        Sets the Thiele-Small parameters that characterize the loudspeaker that
        shall be simulated.
        @param parameters: a ThieleSmallParameters instance
        """
        self._thiele_small = parameters
        self._recalculate = True

    @sumpf.Input(sumpf.Signal, ("GetExcursion", "GetVelocity", "GetAcceleration", "GetCurrent", "GetSoundPressure"))
    def SetVoltage(self, signal):
        """
        Sets the input voltage signal for the simulated loudspeaker.
        @param signal: a signal for the input voltage of the loudspeaker
        """
        self._voltage = signal
        self._recalculate = True
        self._Precalculate()

    @sumpf.Input(float, ("GetExcursion", "GetVelocity", "GetAcceleration", "GetCurrent", "GetSoundPressure"))
    def SetListenerDistance(self, distance):
        """
        Sets the distance between the loudspeaker and the point where the radiated
        sound is received.
        @param distance: a float value for the distance in meters
        """
        self._listener_distance = distance
        self._recalculate = True

    @sumpf.Input(float, ("GetExcursion", "GetVelocity", "GetAcceleration", "GetCurrent", "GetSoundPressure"))
    def SetMediumDensity(self, density):
        """
        Sets a value for the density of the medium in which the loudspeaker radiates
        sound (probably air).
        @param value: a float value for the density in kilograms per cubic meter
        """
        self._medium_density = density
        self._recalculate = True

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetExcursion(self):
        """
        Calculates and returns a signal for the diaphragm excursion of the
        simulated loudspeaker, when it is excited with the given input voltage.
        @retval : a Signal instance
        """
        if self._recalculate:
            self.__Recalculate()
        return self.__excursion

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetVelocity(self):
        """
        Calculates and returns a signal for the diaphragm velocity of the
        simulated loudspeaker, when it is excited with the given input voltage.
        @retval : a Signal instance
        """
        if self._recalculate:
            self.__Recalculate()
        return self.__velocity

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetAcceleration(self):
        """
        Calculates and returns a signal for the diaphragm acceleration of the
        simulated loudspeaker, when it is excited with the given input voltage.
        @retval : a Signal instance
        """
        if self._recalculate:
            self.__Recalculate()
        return self.__acceleration

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetCurrent(self):
        """
        Calculates and returns a signal for the input current of the simulated
        loudspeaker, when it is excited with the given input voltage.
        @retval : a Signal instance
        """
        if self._recalculate:
            self.__Recalculate()
        return self.__current

    @sumpf.Output(sumpf.Signal, caching=False)
    def GetSoundPressure(self):
        """
        Calculates and returns a signal for the sound pressure that is generated
        at the given listener distance by the simulated loudspeaker, when it is
        excited with the given input voltage.
        For this, the loudspeaker is assumed to be a perfect point sound source.
        Not modeled parameters like the loudspeaker enclosure, the diaphragm's
        breakup modes or the loudspeaker's directivity might cause significant
        simulation errors.
        The sound pressure signal is not delayed by the time, the sound takes to
        travel the given listener distance.
        @retval : a Signal instance
        """
        if self._recalculate:
            self.__Recalculate()
        return self.__sound_pressure

    def _Precalculate(self):
        """
        This protected method can be overridden by derived classes. It is called
        when the input voltage signal is set and is meant to compute values prior
        to the actual simulation, to speed up the computations of the simulated
        signals.
        """
        pass

    def _Recalculate(self):
        """
        This protected method has to be implemented in derived classes, so it
        computes and returns the channels of the simulated signals.
        The calculated channels shall be returned as a tuple with its elements
        in the following order:
         1) the channels for the diaphragm excursion
         2) the channels for the diaphragm velocity
         3) the channels for the diaphragm acceleration
         4) the channels for the input current
         5) the channels for the sound pressure
        @retval : a tuple like described above
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    def __Recalculate(self):
        """
        This private method does the tasks that are common to all auralization
        implementations like labeling the channels of the simulated signals and
        creating Signal instances from that.
        """
        excursion_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels = self._Recalculate()
        excursion_labels = []
        velocity_labels = []
        acceleration_labels = []
        current_labels = []
        sound_pressure_labels = []
        for c in range(len(self._voltage.GetChannels())):
            excursion_labels.append("Excursion %i" % (c + 1))
            velocity_labels.append("Velocity %i" % (c + 1))
            acceleration_labels.append("Acceleration %i" % (c + 1))
            current_labels.append("Current %i" % (c + 1))
            sound_pressure_labels.append("Sound Pressure %i" % (c + 1))
        self.__excursion = sumpf.Signal(channels=tuple(excursion_channels), samplingrate=self._voltage.GetSamplingRate(), labels=tuple(excursion_labels))
        self.__velocity = sumpf.Signal(channels=tuple(velocity_channels), samplingrate=self._voltage.GetSamplingRate(), labels=tuple(velocity_labels))
        self.__acceleration = sumpf.Signal(channels=tuple(acceleration_channels), samplingrate=self._voltage.GetSamplingRate(), labels=tuple(acceleration_labels))
        self.__current = sumpf.Signal(channels=tuple(current_channels), samplingrate=self._voltage.GetSamplingRate(), labels=tuple(current_labels))
        self.__sound_pressure = sumpf.Signal(channels=tuple(sound_pressure_channels), samplingrate=self._voltage.GetSamplingRate(), labels=tuple(sound_pressure_labels))
        self._recalculate = False

