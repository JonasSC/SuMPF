# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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
import cython
#import numpy

@cython.boundscheck(False)
def recalculate_nonlinear_cython(voltage_channels, double sampling_rate,
                                 thiele_small_parameter_function,
                                 double listener_distance, double medium_density,
                                 double warp_frequency, double regularization,
                                 bint save_samples, saved_samples):
    """
    This is mainly a direct copy of the pure Python implementation from the
    ThieleSmallParameterAuralizationNonlinear class with some staticly typed
    variables.
    """
    saved_voltage = []
    saved_excursion = []
    saved_velocity = []
    saved_acceleration = []
    saved_current = []
    saved_sound_pressure = []
    # precalculate necessary values
    cdef int length = len(voltage_channels[0]) + 3
    cdef double K = 2.0 * sampling_rate
    if warp_frequency != 0.0:
        K = 2.0 * math.pi * warp_frequency / math.tan(2.0 * math.pi * warp_frequency / K)
    cdef double q = 1.0 - regularization
    cdef double _3q = 3.0 * q                       # a1
    cdef double _3q2 = 3.0 * q ** 2                 # a2
    cdef double _q3 = q ** 3                        # a3
    cdef double _K3 = K ** 3                        # b0
    cdef double _K2 = K ** 2
    cdef double _3K3 = 3.0 * _K3                    # b1
    cdef double _K2q2 = _K2 * (q - 2.0)
    cdef double _K2q1 = K * (2.0 * q - 1.0)
    cdef double _K212q = _K2 * (1.0 - 2.0 * q)      # b2
    cdef double _Kqq2 = K * q * (q - 2.0)
    cdef double _K2q = K ** 2 * q                   # b3
    cdef double _Kq2 = K * q ** 2
    cdef double sound_pressure_factor = medium_density / (4.0 * math.pi * listener_distance)
    cdef double f = 1000.0
    cdef double T = 20.0
    # static type declarations
    cdef:
        int c, i
        double x, v
        double R, L, M, k, w, m, S
        double Lm, LwRm, LkM2Rw, Rk
        double a0, a1, a2, a3
        double b0, b1, b2, b3
        double summed
    # start the calculation
    excursion_channels = []
    velocity_channels = []
    acceleration_channels = []
    current_channels = []
    sound_pressure_channels = []
    for c, channel in enumerate(voltage_channels):
        excursion = [0.0] * length
        velocity = [0.0] * length
        acceleration = [0.0] * length
        current = [0.0] * length
        sound_pressure = [0.0] * length
        if save_samples and len(saved_samples[0]) == len(voltage_channels):
            voltage = tuple(saved_samples[0][c]) + channel
            excursion[0:3] = saved_samples[1][c]
            velocity[0:3] = saved_samples[2][c]
            acceleration[0:3] = saved_samples[3][c]
            current[0:3] = saved_samples[4][c]
            sound_pressure[0:3] = saved_samples[5][c]
        else:
            voltage = (0.0,) * 3 + channel
        for i in range(3, length):
            x = excursion[i - 1]
            v = velocity[i - 1]
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
            summed = a0 * voltage[i] + a1 * voltage[i - 1] + a2 * voltage[i - 2] + a3 * voltage[i - 3] - b1 * excursion[i - 1] - b2 * excursion[i - 2] - b3 * excursion[i - 3]
            excursion[i] = summed / b0
            # calculate the velocity, the acceleration, the current and the sound pressure
            velocity[i] = K * (excursion[i] - excursion[i - 1]) - q * velocity[i - 1]
            acceleration[i] = K * (velocity[i] - velocity[i - 1]) - q * acceleration[i - 1]
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
    return ((excursion_channels, velocity_channels, acceleration_channels, current_channels, sound_pressure_channels),
            (saved_voltage, saved_excursion, saved_velocity, saved_acceleration, saved_current, saved_sound_pressure))

#@cython.boundscheck(False)
#def recalculate_nonlinear_cython_numpy(voltage_channels, double sampling_rate,
#                                       thiele_small_parameter_function,
#                                       double listener_distance, double medium_density,
#                                       double warp_frequency, double regularization,
#                                       bint save_samples, saved_samples):
#    """
#    This implementation tries to gain a performance improvement over the pure
#    Python implementation by using NumPy's efficient linear algebra functions
#    for calculating the filter coefficients.
#    But somehow this implementation runs only slightly faster than the pure Python
#    implementation and much slower than the other compiled implementation.
#    """
#    # precalculate necessary values
#    cdef int number_of_channels = len(voltage_channels)
#    cdef int length = len(voltage_channels[0]) + 3
#    cdef double K = 2.0 * sampling_rate
#    if warp_frequency != 0.0:
#        K = 2.0 * math.pi * warp_frequency / math.tan(2.0 * math.pi * warp_frequency / K)
#    cdef double q = 1.0 - regularization
#    cdef double[:, :] b_matrix = numpy.asfarray([(-K ** 3, K ** 2 * q, -K * q ** 2, q ** 3),
#                                                 (3.0 * K ** 3, K ** 2 * (1.0 - 2.0 * q), K * q * (q - 2.0), 3.0 * q ** 2),
#                                                 (-3.0 * K ** 3, K ** 2 * (q - 2.0), K * (2.0 * q - 1.0), 3.0 * q),
#                                                 (K ** 3, K ** 2, K, 1.0)])
#    cdef double sound_pressure_factor = medium_density / (4.0 * math.pi * listener_distance)
#    cdef double f = 0.0
#    cdef double T = 20.0
#    # static type declarations
#    cdef:
#        int c, i, i1, i3, i_1
#        double x, v
#        double R, L, M, k, w, m, S
#    cdef double[:] a_vector = numpy.asfarray((q ** 3, 3.0 * q ** 2, 3.0 * q, 1.0))
#    cdef double[:] a = numpy.zeros(4, dtype=numpy.float64)
#    cdef double[:] b_vector = numpy.zeros(4, dtype=numpy.float64)
#    cdef double[:] b = numpy.zeros(4, dtype=numpy.float64)
#    # start the calculation
#    cdef double[:, :, :] output = numpy.zeros(shape=(6, number_of_channels, length), dtype=numpy.float64)
#    output[0, :, 3:] = numpy.asfarray(voltage_channels)
#    for c in range(number_of_channels):
#        for i in range(3, length):
#            output[0][c][i] = voltage_channels[c][i - 3]
#    if save_samples and len(saved_samples[0]) == number_of_channels:
#        output[:, :, 0:3] = saved_samples
#    for c in range(number_of_channels):
#        for i in range(3, length):
#            i1 = i - 1
#            i3 = i - 3
#            i_1 = i + 1
#            x = output[1][c][i1]
#            v = output[1][c][i1]
#            # get the Thiele Small parameters
#            R, L, M, k, w, m, S = thiele_small_parameter_function(f, x, v, T)
#            # calculate the filter coefficients for the excursion calculation
#            a[0:4] = numpy.multiply(a_vector, M)
#            b_vector[0:4] = (L * m, L * w + R * m, L * k + M * M + R * w, R * k)
#            b[0:4] = numpy.dot(b_matrix, b_vector)
#            output[1][c][i] = (numpy.sum(numpy.multiply(output[0][c][i3:i_1], a)) - numpy.sum(numpy.multiply(output[1][c][i3:i], b[0:3]))) / b[3]
#            # calculate the velocity, the acceleration, the current and the sound pressure
#            output[2][c][i] = K * (output[1][c][i] - output[1][c][i1]) - q * output[2][c][i1]
#            output[3][c][i] = K * (output[2][c][i] - output[2][c][i1]) - q * output[3][c][i1]
#            output[4][c][i] = (k * output[1][c][i] + w * output[2][c][i] + m * output[3][c][i]) / M
#            output[5][c][i] = output[3][c][i] * S * sound_pressure_factor
#    return output[1:, :, 3:], output[:, :, -3:]

