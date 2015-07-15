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

import math
import sumpf
from .auralization_base import ThieleSmallParameterAuralization

cython_available = False
if sumpf.config.get("use_cython"):
    try:
        import pyximport
        pyximport.install()
        from .auralization_nonlinear_cython import recalculate_nonlinear_cython
        cython_available = True
    except ImportError:
        pass



class ThieleSmallParameterAuralizationNonlinear(ThieleSmallParameterAuralization):
    """
    Synthesizes loudspeaker responses for a given input voltage signal.
    These responses can be the diaphragm excursion, the diaphragm velocity, the
    diaphragm acceleration, the input current and the generated sound pressure
    at a given distance.

    This synthesis also simulates nonlinear effects, which are caused by loudspeaker
    parameters that change with the diaphragm excursion or the diaphragm velocity.
    Frequency or temperature dependencies of parameters are not considered in
    this simulation.

    The simulation is implemented as an IIR-filter in the z-domain, that updates
    the excursion and velocity dependent parameters for each sample with the
    excursion and velocity that has been calculated for the previous sample.

    The formula for the IIR-filter has been calculated by using the bilinear transform
    on the voltage-to-excursion transfer function in the Laplace domain. Due to
    the non-infinite sampling rate, this causes an error in the high frequencies
    of the output signals. Specifying a "warp frequency" for the Filter minimizes
    the error at that frequency, but this increases the errors at other frequencies.
    """
    def __init__(self, thiele_small_parameters=sumpf.ThieleSmallParameters(), voltage_signal=None, listener_distance=1.0, medium_density=1.2041, warp_frequency=0.0, regularization=0.0, save_samples=False, use_cython=True):
        """
        @param thiele_small_parameters: a ThieleSmallParameters instance
        @param voltage_signal: a signal for the input voltage of the loudspeaker
        @param listener_distance: a float value for the distance between the loudspeaker and the point where the radiated sound is received in meters
        @param medium_density: a float value for the density of the medium, in which the loudspeaker radiates sound (probably air) in kilograms per cubic meter
        @param warp_frequency: a frequency in Hz, at which the error, that is caused by the bilinear transform, shall be minimized
        @param regularization: a small float < 1.0 that ensures the stability of the bilinear transform
        @param save_samples: if True, the last three samples of the calculated Signals are saved, so that a gapless simulation of two consecutive Signals is performed. If False, the samples are assumed to be zero
        @param use_cython: if True and Cython is available, a compiled version of the auralization algorithm is uses, which is slightly faster
        """
        ThieleSmallParameterAuralization.__init__(self, thiele_small_parameters=thiele_small_parameters, voltage_signal=voltage_signal, listener_distance=listener_distance, medium_density=medium_density)
        self.__warp_frequency = warp_frequency
        self.__regularization = regularization
        self.__save_samples = save_samples
        self.__use_cython = use_cython and cython_available
        self.__saved_voltage = ((0.0, 0.0, 0.0),)
        self.__saved_excursion = ([0.0, 0.0, 0.0],)
        self.__saved_velocity = ([0.0, 0.0, 0.0],)
        self.__saved_acceleration = ([0.0, 0.0, 0.0],)
        self.__saved_current = ([0.0, 0.0, 0.0],)
        self.__saved_sound_pressure = ([0.0, 0.0, 0.0],)

    @sumpf.Input(float, ("GetExcursion", "GetVelocity", "GetAcceleration", "GetCurrent", "GetSoundPressure"))
    def SetWarpFrequency(self, frequency):
        """
        Sets a frequency, at which the error, that is caused by the bilinear
        transform, shall be minimized.
        This increases the error at frequencies, that are not near the warp frequency.
        Setting the warp frequency to a high frequency, where the errors of the
        bilinear transform are especially high, causes a significant increase in
        the overall simulation error, so low warp frequencies (e.g. the resonance
        frequency of the simulated loudspeaker) are recommended.
        @param warp_frequency: a frequency in Hz as a float
        """
        self.__warp_frequency = frequency
        self._recalculate = True

    @sumpf.Input(float, ("GetExcursion", "GetVelocity", "GetAcceleration", "GetCurrent", "GetSoundPressure"))
    def SetRegularization(self, value):
        """
        Sets a regularization value, that ensures the stability of the bilinear
        transform.
        The bilinear transform has a pole at z=-1, which is on the unit circle and
        means that the resulting filter is not stable. The regularization value
        shifts the pole to z=-1+q to get a stable filter. The formula for the
        bilinear transform with regularization is:
            s = K * (z-1) / (z+1-q)
        It is recommended, to use a small regularization value, as larger values
        increase the simulation error.
        @param regularization: a small float < 1.0
        """
        self.__regularization, value
        self._recalculate = True

    @sumpf.Input(bool)
    def SetSaveSamples(self, save_samples):
        """
        Specifies, if the last three samples of the output signals shall be saved,
        in order to perform a gapless simulation with two or more consecutive input
        signals. The saved samples are used as start values for the in the feedback
        part of the IIR filter. If save_samples is False, those start values for
        the fed back samples are set to zero.

        If the arrays of saved samples have a different number of channels than
        the current input voltage, the saved samples are ignored and considered
        to be zero.

        Consider the following example, in which "Signal1 + Signal2" stands for
        the concatenation of "Signal1" and "Signal2", "Auralization(Signal1)"
        means the simulation of a loudspeaker with "Signal1" as input voltage and
        "(Signal1 + Signal2)[Signal2]" means that only the Signal2-part of the
        concatenation shall be considered:
            If save_samples is True, the following statements hold:
                Auralization(Signal1) + Auralization(Signal2) = Auralization(Signal1 + Signal2)
                (Auralization(Signal1) + Auralization(Signal2))[Signal2] != Auralization(Signal2)   # because the auralization of Signal1 has changed the state of the auralization object by saving the last samples
            If save_samples is False, the following statements hold:
                Auralization(Signal1) + Auralization(Signal2) != Auralization(Signal1 + Signal2)    # because the state after the auralization of Signal1 is not saved, so Signal2 is auralized with an "empty past"
                (Auralization(Signal1) + Auralization(Signal2))[Signal2] = Auralization(Signal2)    # because auralizing a Signal does not change the state of the auralization object

        Calling this method does not trigger a recalculation of the output Signals
        through SuMPF's connectors, but calling one of the getter methods explicitly
        will compute a new signal.
        If save_samples is set to True, the next auralization will be done with
        the saved samples from the most recently auralized signal, even if save_samples
        has been False during that auralization.

        @param save_samples: a bool that specifies if the samples shall be saved or not
        """
        if self.__save_samples != save_samples:
            self._recalculate = True
        self.__save_samples = save_samples

    @sumpf.Input(bool)
    def SetUseCython(self, use_cython):
        """
        Specifies, if a Cython implementation of the auralization algorithm shall
        be used, to increase the speed of the auralization.
        Currently the speed improvements are about 20 to 25 percent.
        @param use_cython: True if Cython shall be used, False otherwise
        """
        self.__use_cython = use_cython and cython_available

    @sumpf.Trigger()
    def ResetSavedSamples(self):
        """
        Resets the saved samples of the previously auralized signal to zero.
        Calling this method does not trigger a recalculation of the output Signals
        through SuMPF's connectors, but calling one of the getter methods explicitly
        will compute a new signal.
        """
        self.__saved_voltage = ((0.0, 0.0, 0.0),)
        self.__saved_excursion = ([0.0, 0.0, 0.0],)
        self.__saved_velocity = ([0.0, 0.0, 0.0],)
        self.__saved_acceleration = ([0.0, 0.0, 0.0],)
        self.__saved_current = ([0.0, 0.0, 0.0],)
        self.__saved_sound_pressure = ([0.0, 0.0, 0.0],)
        if self.__save_samples:
            self._recalculate = True

    def _Recalculate(self):
        """
        Calculates the channels for the excursion, velocity and acceleration
        of the diaphragm and for the input current and the generated sound pressure.
        @retval the channel data excursion_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels
        """
        thiele_small_parameter_function = self._thiele_small.GetAllParameters
        if self.__use_cython:
            auralized, saved = recalculate_nonlinear_cython(voltage_channels=self._voltage.GetChannels(),
                                                            sampling_rate=self._voltage.GetSamplingRate(),
                                                            thiele_small_parameter_function=thiele_small_parameter_function,
                                                            listener_distance=self._listener_distance,
                                                            medium_density=self._medium_density,
                                                            warp_frequency=self.__warp_frequency,
                                                            regularization=self.__regularization,
                                                            save_samples=self.__save_samples,
                                                            saved_samples=(self.__saved_voltage, self.__saved_excursion, self.__saved_velocity, self.__saved_acceleration, self.__saved_current, self.__saved_sound_pressure))
            self.__saved_voltage = saved[0]
            self.__saved_excursion = saved[1]
            self.__saved_velocity = saved[2]
            self.__saved_acceleration = saved[3]
            self.__saved_current = saved[4]
            self.__saved_sound_pressure = saved[5]
            return auralized
        else:
            # make class variables local
            saved_voltage = []
            saved_excursion = []
            saved_velocity = []
            saved_acceleration = []
            saved_current = []
            saved_sound_pressure = []
            # precalculate necessary values
            length = len(self._voltage) + 3
            K = 2.0 * self._voltage.GetSamplingRate()
            if self.__warp_frequency != 0.0:
                K = 2.0 * math.pi * self.__warp_frequency / math.tan(2.0 * math.pi * self.__warp_frequency / K)
            q = 1.0 - self.__regularization
            _3q = 3.0 * q                   # a1
            _3q2 = 3.0 * q ** 2             # a2
            _q3 = q ** 3                    # a3
            _K3 = K ** 3                    # b0
            _K2 = K ** 2
            _3K3 = 3.0 * _K3                # b1
            _K2q2 = _K2 * (q - 2.0)
            _K2q1 = K * (2.0 * q - 1.0)
            _K212q = _K2 * (1.0 - 2.0 * q)  # b2
            _Kqq2 = K * q * (q - 2.0)
            _K2q = K ** 2 * q               # b3
            _Kq2 = K * q ** 2
            sound_pressure_factor = self._medium_density / (4.0 * math.pi * self._listener_distance)
            f = 1000.0
            T = 20.0
            # start the calculation
            excursion_channels = []
            velocity_channels = []
            acceleration_channels = []
            current_channels = []
            sound_pressure_channels = []
            for c, channel in enumerate(self._voltage.GetChannels()):
                voltage = None
                excursion = [0.0] * length
                velocity = [0.0] * length
                acceleration = [0.0] * length
                current = [0.0] * length
                sound_pressure = [0.0] * length
                if self.__save_samples and len(self.__saved_voltage) == len(self._voltage.GetChannels()):
                    voltage = tuple(self.__saved_voltage[c]) + channel
                    excursion[0:3] = self.__saved_excursion[c]
                    velocity[0:3] = self.__saved_velocity[c]
                    acceleration[0:3] = self.__saved_acceleration[c]
                    current[0:3] = self.__saved_current[c]
                    sound_pressure[0:3] = self.__saved_sound_pressure[c]
                else:
                    voltage = (0.0,) * 3 + channel
                for i in range(3, length):
                    i1 = i - 1
                    i2 = i - 2
                    i3 = i - 3
                    x = excursion[i1]
                    v = velocity[i1]
                    # get the Thiele Small parameters
                    R, L, M, k, w, m, S = thiele_small_parameter_function(f, x, v, T)
                    # precalculate some values for the excursion calculation
                    Lm = L * m
                    LwRm = L * w + R * m
                    LkM2Rw = L * k + M * M + R * w
                    Rk = R * k
                    # calculate the filter coefficients for the excursion calculation
                    a0 = M
                    a1 = M * _3q
                    a2 = M * _3q2
                    a3 = M * _q3
                    b0 = Lm * _K3 + LwRm * _K2 + LkM2Rw * K + Rk
                    b1 = -Lm * _3K3 + LwRm * _K2q2 + LkM2Rw * _K2q1 + Rk * _3q
                    b2 = Lm * _3K3 + LwRm * _K212q + LkM2Rw * _Kqq2 + Rk * _3q2
                    b3 = -Lm * _K3 + LwRm * _K2q - LkM2Rw * _Kq2 + Rk * _q3
                    summed = a0 * voltage[i] + a1 * voltage[i1] + a2 * voltage[i2] + a3 * voltage[i3] - b1 * excursion[i1] - b2 * excursion[i2] - b3 * excursion[i3]
                    excursion[i] = summed / b0
                    # calculate the velocity, the acceleration, the current and the sound pressure
                    velocity[i] = K * (excursion[i] - excursion[i1]) - q * velocity[i1]
                    acceleration[i] = K * (velocity[i] - velocity[i1]) - q * acceleration[i1]
                    current[i] = (k * excursion[i] + w * velocity[i] + m * acceleration[i]) / M
                    sound_pressure[i] = acceleration[i] * S * sound_pressure_factor
                # store the Signals
                excursion_channels.append(tuple(excursion[3:]))
                velocity_channels.append(tuple(velocity[3:]))
                acceleration_channels.append(tuple(acceleration[3:]))
                current_channels.append(tuple(current[3:]))
                sound_pressure_channels.append(tuple(sound_pressure[3:]))
                saved_voltage.append(voltage[-3:])
                saved_excursion.append(excursion[-3:])
                saved_velocity.append(velocity[-3:])
                saved_acceleration.append(acceleration[-3:])
                saved_current.append(current[-3:])
                saved_sound_pressure.append(sound_pressure[-3:])
            self.__saved_voltage = saved_voltage
            self.__saved_excursion = saved_excursion
            self.__saved_velocity = saved_velocity
            self.__saved_acceleration = saved_acceleration
            self.__saved_current = saved_current
            self.__saved_sound_pressure = saved_sound_pressure
            return excursion_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels

