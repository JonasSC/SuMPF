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


def binomial_coefficient(n, k):
    """
    This function calculates the binomial coefficient of n over k. This is the
    number of choices to pick k items out of a set of n items.
    @param n, k: two integers
    @retval : the binomial coefficient as an integer
    """
    if k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    if k == 0 or n <= 1:
        return 1
    result = 1.0
    m = n + 1.0
    for i in range(1, k + 1):
        result *= (m - i) / i
    return int(round(result))

def differentiate(sequence):
    """
    This function takes a sequence of numbers and calculates the derivative of it.
    The length of the result is the same as the length of the input.
    The result might have to be scaled by the time gap between the sequence's samples.

    This function calculates the derivative by subtracting the previous sample
    of the input sequence from the current sample. The first sample of the derivative
    is calculated by subtracting the first input sample from the second.
    This algorithm is fast and yields reasonably good results. Nevertheless, the
    calculated values are actually the derivative values between the samples, which
    means that the result is delayed by half the sampling time. Furthermore the
    limited sampling rate causes the calculated derivative to show a bandpass
    behavior rather than the expected high pass behavior. And the fact, that the
    first sample of the result is calculated in a different way than the other
    samples, is not exactly ideal.

    The differentiate_fft function avoids the aforementioned drawbacks by calculating
    the derivative in the frequency domain. However it causes ringing artifacts
    at the beginning and at the end of the calculated derivative, that are especially
    critical with short input sequences.
    The differentiate_spline function avoids the half-sample delay of this simple
    algorithm by interpolating the sequence with polynomials, but increasing the
    degree of the polynomials causes the bandpass behavior to become worse.
    Both these algorithms are only available, when the external library NumPy is
    available as well.

    @param sequence: a list of numbers
    @retval : the derivative of the given list as a list of floats
    """
    if len(sequence) == 0:
        return []
    elif len(sequence) == 1:
        return [0.0]
    else:
        result = [sequence[1] - sequence[0]]
        for i in range(1, len(sequence)):
            result.append(sequence[i] - sequence[i - 1])
        return result

try:
    import numpy
    import math

    def differentiate_fft(sequence):
        """
        This function takes a sequence of numbers and calculates the derivative
        of it. The length of the result is the same as the length of the input.
        The result might have to be scaled by the time gap between the sequence's
        samples.

        This function calculates the derivative by transforming the input sequence
        to the frequency domain, multiplying the resulting values with a factor
        that is proportional to the frequency and then transforming the result
        back to the original domain.
        This avoids the bandpass behavior of the differentiate and the differentiate_spline
        algorithms. However this algorithm causes ringing artifacts at the beginning
        and at the end of the calculated derivative, that are especially critical
        with short input sequences.

        The differentiate_fft function is only available, when the external library
        NumPy is available as well.

        @param sequence: a list of numbers
        @retval : the derivative of the given list as a list of floats
        """
        if len(sequence) == 0:
            return []
        elif len(sequence) == 1:
            return [0.0]
        else:
            def calculate(sq):
                spectrum = numpy.fft.rfft(sq)
                for i in range(len(spectrum)):
                    spectrum[i] *= 2.0j * math.pi * float(i) / float(len(sq))
                return list(numpy.fft.irfft(spectrum))
            if len(sequence) % 2 == 0:
                return calculate(sequence)
            else:
                return calculate(list(sequence) + [0])[0:-1]

    def differentiate_spline(sequence, degree=2):
        """
        This function takes a sequence of numbers and calculates the derivative of it.
        The length of the result is the same as the length of the input.
        The result might have to be scaled by the time gap between the sequence's
        samples.

        This function calculates the derivative by piecewise interpolation of the
        input sequence with polynomials and calculating the derivative of these
        polynomials. With a degree of 1, this function works exactly like the
        standard differentiation algorithm.
        This algorithm avoids delay of the standard differentiation algorithm
        and the ringing artifacts of the differentiate_fft algorithm.
        But with high degrees of the interpolation polynomials, the bandpass behavior,
        that is also a drawback of the standard algorithm, becomes worse.

        The differentiate_spline function is only available, when the external
        library NumPy is available as well.

        @param sequence: a list of numbers
        @param degree: the degree of the interpolation polynomials
        @retval : the derivative of the given list as a list of floats
        """
        if len(sequence) == 0:
            return []
        elif len(sequence) == 1:
            return [0.0]
        else:
            if degree < 1:
                raise ValueError("Approximating a sequence with a %ith degree polynomials is not useful to calculate the derivative." % degree)
            elif degree == 1:
                result = [sequence[1] - sequence[0]]
                for i in range(1, len(sequence)):
                    result.append(sequence[i] - sequence[i - 1])
                return result
            elif degree == 2:
                # speed the calculation of the derivative up by using a precalculated solution of the equation system
                result = []
                result.append(float(sequence[1] - sequence[0]))
                for i in range(1, len(sequence) - 1):
                    result.append((sequence[i + 1] - sequence[i - 1]) / 2.0)
                result.append(float(sequence[-1] - sequence[-2]))
                return result
            else:
                def get_derivative(points, index):
                    matrix = []
                    vector = []
                    for i in range(len(points)):
                        if i != index:
                            matrix.append([(i - index) ** n for n in range(len(points) - 1, 0, -1)])
                            vector.append(points[i] - points[index])
                    result = numpy.linalg.solve(matrix, vector)[-1]
                    return result
                result = []
                pointcount = degree + 1                     # number of points that are evaluated to calculate one polynomial of the spline
                beforepoints = pointcount // 2              # number of evaluated points before the point at which the derivative is calculated
                afterpoints = pointcount - 1 - beforepoints # number of evaluated points after the point at which the derivative is calculated
                for i in range(0, min(len(sequence), beforepoints)):
                    points = sequence[0:min(len(sequence), i + afterpoints + 1)]
                    result.append(get_derivative(points=points, index=i))
                for i in range(beforepoints, len(sequence) - afterpoints):
                    points = sequence[i - beforepoints:i + afterpoints + 1]
                    result.append(get_derivative(points=points, index=beforepoints))
                for i in range(max(beforepoints, len(sequence) - afterpoints), len(sequence)):
                    points = sequence[i - beforepoints:min(len(sequence), i + afterpoints + 1)]
                    result.append(get_derivative(points=points, index=beforepoints))
                return result

except ImportError:
    pass

