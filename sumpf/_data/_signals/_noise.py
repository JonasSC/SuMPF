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

"""Contains classes for signals with random noise."""

import numpy
import sumpf._internal as sumpf_internal
from ._signal import Signal

__all__ = ("UniformNoise", "GaussianNoise", "PoissonNoise", "LaplaceNoise",
           "VonMisesNoise", "TriangularNoise", "GeometricNoise", "HypergeometricNoise",
           "BinomialNoise", "BetaNoise", "GammaNoise", "LogarithmicNoise",
           "LogisticNoise", "LomaxNoise", "WaldNoise", "ChiSquareNoise")

##############
# Base class #
##############


class Noise(Signal):
    """Abstract base class for signals with random noise samples."""

    def __init__(self, seed, sampling_rate, length, label):
        """
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__seed = seed
        channels = sumpf_internal.allocate_array(shape=(1, length), dtype=numpy.float64)
        channels[0, :] = self._function(length)
        Signal.__init__(self, channels=channels, sampling_rate=sampling_rate, offset=0, labels=(label,))

    def _function(self, length):
        """An abstract method, in which derived classes shall implement the generation
        of the noise signal.

        :param length: the length of the signal as an integer number of samples
        :returns: the noise signal in a one-dimensional :func:`numpy.array`
        """
        raise NotImplementedError("This method has to be implemented in a derived class")

    def seed(self):
        """Returns the seed, with which the random number generator was seeded.

        :returns: the seed object
        """
        return self.__seed

#################################################################
# Classes with NumPy implementations of the noise distributions #
#################################################################


class UniformNoise(Noise):
    """A signal with samples drawn from a uniform distribution."""

    def __init__(self, lower_boundary=-1.0, upper_boundary=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param lower_boundary: lower boundary of the generated samples. All samples
                               of the signal are greater or equal of this value
        :param upper_boundary: upper boundary of the generated samples. All samples
                               of the signal are smaller than this value
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__lower_boundary = lower_boundary
        self.__upper_boundary = upper_boundary
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Uniform noise")

    def _function(self, length):
        return self.__random.uniform(low=self.__lower_boundary, high=self.__upper_boundary, size=length)


class GaussianNoise(Noise):
    """A signal with samples drawn from a Gaussian or normal distribution."""

    def __init__(self, mean=0.0, standard_deviation=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param mean: the mean of the Gaussian distribution
        :param standard_deviation: the standard deviation of the Gaussian distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__mean = mean
        self.__standard_deviation = standard_deviation
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Gaussian noise")

    def _function(self, length):
        return self.__random.normal(loc=self.__mean, scale=self.__standard_deviation, size=length)


class PoissonNoise(Noise):
    """A signal with samples drawn from a Poisson distribution."""

    def __init__(self, lambda_=0.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param lambda_: the lambda parameter of the Poisson distribution, which
                        happens to be its mean and variance
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__lambda = lambda_
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Poisson noise")

    def _function(self, length):
        return self.__random.poisson(lam=self.__lambda, size=length)


class LaplaceNoise(Noise):
    """A signal with samples drawn from a Laplace distribution."""

    def __init__(self, mean=0.0, decay=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param mean: the mean of the Laplace distribution
        :param decay: the parameter in the denominator, that defines the exponential
                      decay of the probability density function
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__mean = mean
        self.__decay = decay
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Laplace noise")

    def _function(self, length):
        return self.__random.laplace(loc=self.__mean, scale=self.__decay, size=length)


class VonMisesNoise(Noise):
    """A signal with samples drawn from a von Mises distribution."""

    def __init__(self, mode=0.0, dispersion=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param mode: the mu or mode parameter of the von Mises distribution
        :param dispersion: the kappa or dispersion parameter of the von Mises distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__mode = mode
        self.__dispersion = dispersion
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "von Mises noise")

    def _function(self, length):
        return self.__random.vonmises(mu=self.__mode, kappa=self.__dispersion, size=length)


class TriangularNoise(Noise):
    """A signal with samples drawn from a triangular distribution."""

    def __init__(self, lower_boundary=-1.0, upper_boundary=1.0, mode=None,
                 seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param lower_boundary: the minimum value of the samples, that can be produced
        :param upper_boundary: the maximum value of the samples, that can be produced
        :param mode: the value, at which the peak of the distribution occurs. If
                     this is None, the middle between the boundaries will be taken
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__lower_boundary = lower_boundary
        self.__upper_boundary = upper_boundary
        if mode is None:
            self.__mode = (lower_boundary + upper_boundary) / 2.0
        else:
            self.__mode = mode
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Triangular noise")

    def _function(self, length):
        return self.__random.triangular(left=self.__lower_boundary,
                                        mode=self.__mode,
                                        right=self.__upper_boundary,
                                        size=length)


class GeometricNoise(Noise):
    """A signal with samples drawn from a geometric distribution."""

    def __init__(self, p=0.5, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param p: the probability value of the geometric distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__p = p
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Geometric noise")

    def _function(self, length):
        return self.__random.geometric(p=self.__p, size=length)


class HypergeometricNoise(Noise):
    """A signal with samples drawn from a hypergeometric distribution.

    The hypergeometric distribution of ``X`` describes the probability to draw
    ``X`` acceptable items with ``N`` draws from a pool of ``A`` acceptable items
    and ``B`` non-acceptable items without putting the drawn items back in the pool.
    """

    def __init__(self, acceptable=1, non_acceptable=1, draws=1, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param acceptable: the number of acceptable items in the pool (``A``)
        :param non_acceptable: the number of non-acceptable items in the pool (``B``)
        :param draws: the number of draws (``N``)
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__acceptable = acceptable
        self.__non_acceptable = non_acceptable
        self.__draws = draws
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Hypergeometric noise")

    def _function(self, length):
        return self.__random.hypergeometric(ngood=self.__acceptable,
                                            nbad=self.__non_acceptable,
                                            nsample=self.__draws,
                                            size=length)


class BinomialNoise(Noise):
    """A signal with samples drawn from a binomial distribution."""

    def __init__(self, p=0.5, draws=1, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param p: the probability parameter of the binomial distribution
        :param draws: the number-of-draws parameter value of the binomial distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__p = p
        self.__draws = draws
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Binomial noise")

    def _function(self, length):
        return self.__random.binomial(n=self.__draws, p=self.__p, size=length)


class BetaNoise(Noise):
    """A signal with samples drawn from a beta distribution."""

    def __init__(self, alpha=1.0, beta=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param alpha: the alpha parameter of the beta distribution
        :param beta: the beta parameter of the beta distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__alpha = alpha
        self.__beta = beta
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Beta noise")

    def _function(self, length):
        return self.__random.beta(a=self.__alpha, b=self.__beta, size=length)


class GammaNoise(Noise):
    """A signal with samples drawn from a gamma distribution."""

    def __init__(self, shape=1.0, scale=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param shape: the shape or ``k`` parameter of the gamma distribution
        :param scale: the scale or theta parameter of the gamma distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__shape = shape
        self.__scale = scale
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Gamma noise")

    def _function(self, length):
        return self.__random.gamma(shape=self.__shape, scale=self.__scale, size=length)


class LogarithmicNoise(Noise):
    """A signal with samples drawn from a logarithmic distribution."""

    def __init__(self, p=0.5, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param p: the probability value of the logarithmic distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__p = p
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Logarithmic noise")

    def _function(self, length):
        return self.__random.logseries(p=self.__p, size=length)


class LogisticNoise(Noise):
    """A signal with samples drawn from a logistic distribution."""

    def __init__(self, mean=0.0, scale=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param mean: the mean of the logistic distribution
        :param scale: the scale parameter of the logistic distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__mean = mean
        self.__scale = scale
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Logistic noise")

    def _function(self, length):
        return self.__random.logistic(loc=self.__mean, scale=self.__scale, size=length)


class LomaxNoise(Noise):
    """A signal with samples drawn from a Lomax or Pareto II distribution."""

    def __init__(self, shape=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param shape: the shape parameter of the Lomax distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__shape = shape
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Lomax noise")

    def _function(self, length):
        return self.__random.pareto(a=self.__shape, size=length)


class WaldNoise(Noise):
    """A signal with samples drawn from a Wald or inverse Gaussian distribution."""

    def __init__(self, mean=1.0, scale=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param mean: the mean of the Wald distribution
        :param scale: the scale parameter of the Wald distribution
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__mean = mean
        self.__scale = scale
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Wald noise")

    def _function(self, length):
        return self.__random.wald(mean=self.__mean, scale=self.__scale, size=length)


class ChiSquareNoise(Noise):
    """A signal with samples drawn from a chi-square distribution."""

    def __init__(self, degrees_of_freedom=1.0, seed=None, sampling_rate=48000.0, length=2 ** 16):
        """
        :param degrees_of_freedom: a float number of degrees of freedom for the
                                   chi-square distribution. Should be greater
                                   than zero
        :param seed: if seed is not None, the random number generator of the
                     instance is seeded with the given seed, so that the generated
                     noise signal is reproducible
        :param sampling_rate: the sampling rate of the resulting signal in Hz as
                              an integer or a float
        :param length: the number of samples of the noise signal
        """
        self.__degrees_of_freedom = degrees_of_freedom
        self.__random = numpy.random.default_rng(seed)
        Noise.__init__(self, seed, sampling_rate, length, "Chi-square noise")

    def _function(self, length):
        return self.__random.chisquare(df=self.__degrees_of_freedom,
                                       size=length)
