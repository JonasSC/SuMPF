# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2020 Jonas Schulte-Coerne
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

"""Contains the tests for the noise signal classes"""

import hypothesis
import numpy
import sumpf
import tests

# pylint: disable=line-too-long; some of the @hypothesis.given-statements are too
#                                long, but they are still better readable, when
#                                a single strategy definition is not split to
#                                multiple lines.


def check_numpy_noise(noise, function, seed, sampling_rate, length, label):
    """A helper function, that performs the checks, that are common to all noise
    signal classes, which use the random distributions from NumPy.
    """
    # check the metadata
    assert noise.sampling_rate() == sampling_rate
    assert noise.length() == length
    assert noise.shape() == (1, length)
    assert noise.labels() == (label,)
    assert noise.seed() == seed
    # check the channels
    generator = numpy.random.RandomState(seed)
    reference = function(generator)
    assert (noise.channels()[0] == reference).all()


def test_default_parameters():
    """Tests if all default parameters of the noise signal classes' constructors
    are valid"""
    for cls in (sumpf.UniformNoise,
                sumpf.GaussianNoise,
                sumpf.PoissonNoise,
                sumpf.LaplaceNoise,
                sumpf.VonMisesNoise,
                sumpf.TriangularNoise,
                sumpf.GeometricNoise,
                sumpf.HypergeometricNoise,
                sumpf.BinomialNoise,
                sumpf.BetaNoise,
                sumpf.GammaNoise,
                sumpf.LogarithmicNoise,
                sumpf.LogisticNoise,
                sumpf.LomaxNoise,
                sumpf.WaldNoise,
                sumpf.ChiSquareNoise):
        noise = cls()
        assert numpy.isfinite(noise.channels()).all()


@hypothesis.given(lower_boundary=hypothesis.strategies.floats(min_value=-1e300, max_value=1e300),
                  upper_boundary=hypothesis.strategies.floats(min_value=-1e300, max_value=1e300),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_uniform_noise(lower_boundary, upper_boundary, seed, sampling_rate, length):
    """Tests the class for uniform noise signals."""
    if lower_boundary > upper_boundary:
        lower_boundary, upper_boundary = upper_boundary, lower_boundary
    noise = sumpf.UniformNoise(lower_boundary, upper_boundary, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.uniform(lower_boundary, upper_boundary, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Uniform noise")


@hypothesis.given(mean=hypothesis.strategies.floats(allow_nan=False, allow_infinity=False),
                  standard_deviation=hypothesis.strategies.floats(min_value=0.0, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_gaussian_noise(mean, standard_deviation, seed, sampling_rate, length):
    """Tests the class for Gaussian noise signals."""
    noise = sumpf.GaussianNoise(mean, standard_deviation, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.normal(mean, standard_deviation, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Gaussian noise")


@hypothesis.given(lambda_=hypothesis.strategies.floats(min_value=0.0, max_value=1e17, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_poisson_noise(lambda_, seed, sampling_rate, length):
    """Tests the class for Poisson noise signals."""
    noise = sumpf.PoissonNoise(lambda_, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.poisson(lambda_, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Poisson noise")


@hypothesis.given(mean=hypothesis.strategies.floats(allow_nan=False, allow_infinity=False),
                  decay=hypothesis.strategies.floats(min_value=0.0, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_laplace_noise(mean, decay, seed, sampling_rate, length):
    """Tests the class for Laplace noise signals."""
    noise = sumpf.LaplaceNoise(mean, decay, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.laplace(mean, decay, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Laplace noise")


@hypothesis.given(mode=hypothesis.strategies.floats(allow_nan=False, allow_infinity=False),
                  dispersion=hypothesis.strategies.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),    # for values larger than 1e15, the test takes forever
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_von_mises_noise(mode, dispersion, seed, sampling_rate, length):
    """Tests the class for von Mises noise signals."""
    noise = sumpf.VonMisesNoise(mode, dispersion, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.vonmises(mode, dispersion, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="von Mises noise")


@hypothesis.given(lower_boundary=hypothesis.strategies.floats(min_value=-1e300, max_value=1e300),
                  upper_boundary=hypothesis.strategies.floats(min_value=-1e300, max_value=1e300),
                  mode=hypothesis.strategies.floats(min_value=-1e300, max_value=1e300),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_triangular_noise(lower_boundary, upper_boundary, mode, seed, sampling_rate, length):
    """Tests the class for triangular noise signals."""
    lower_boundary, mode, upper_boundary = sorted((lower_boundary, upper_boundary, mode))
    if lower_boundary == upper_boundary:
        upper_boundary = abs(2.0 * upper_boundary + 1.0)
    noise = sumpf.TriangularNoise(lower_boundary, upper_boundary, mode, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.triangular(lower_boundary, mode, upper_boundary, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Triangular noise")
    # check the automated determination of the mode
    noise = sumpf.TriangularNoise(lower_boundary, upper_boundary, None, seed, sampling_rate, length)
    middle = (lower_boundary + upper_boundary) / 2.0
    check_numpy_noise(noise=noise,
                      function=lambda g: g.triangular(lower_boundary, middle, upper_boundary, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Triangular noise")


@hypothesis.given(p=hypothesis.strategies.floats(min_value=1e-15, max_value=1.0),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_geometric_noise(p, seed, sampling_rate, length):
    """Tests the class for geometric noise signals."""
    noise = sumpf.GeometricNoise(p, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.geometric(p, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Geometric noise")


@hypothesis.given(acceptable=hypothesis.strategies.integers(min_value=0, max_value=2 ** 15),
                  non_acceptable=hypothesis.strategies.integers(min_value=0, max_value=2 ** 15),
                  draws=hypothesis.strategies.integers(min_value=1, max_value=2 ** 15),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_hypergeometric_noise(acceptable, non_acceptable, draws, seed, sampling_rate, length):
    """Tests the class for hypergeometric noise signals."""
    if acceptable + non_acceptable == 0:
        acceptable += 1
        non_acceptable += 1
    draws = min(draws, acceptable + non_acceptable)
    noise = sumpf.HypergeometricNoise(acceptable, non_acceptable, draws, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.hypergeometric(acceptable, non_acceptable, draws, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Hypergeometric noise")


@hypothesis.given(p=hypothesis.strategies.floats(min_value=0.0, max_value=1.0),
                  draws=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_binomial_noise(p, draws, seed, sampling_rate, length):
    """Tests the class for binomial noise signals."""
    noise = sumpf.BinomialNoise(p, draws, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.binomial(draws, p, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Binomial noise")


@hypothesis.given(alpha=hypothesis.strategies.floats(min_value=1e-15, allow_nan=False, allow_infinity=False),
                  beta=hypothesis.strategies.floats(min_value=1e-15, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_beta_noise(alpha, beta, seed, sampling_rate, length):
    """Tests the class for beta noise signals."""
    noise = sumpf.BetaNoise(alpha, beta, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.beta(alpha, beta, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Beta noise")


@hypothesis.given(shape=hypothesis.strategies.floats(min_value=0.0, allow_nan=False, allow_infinity=False),
                  scale=hypothesis.strategies.floats(min_value=0.0, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_gamma_noise(shape, scale, seed, sampling_rate, length):
    """Tests the class for gamma noise signals."""
    noise = sumpf.GammaNoise(shape, scale, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.gamma(shape, scale, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Gamma noise")


@hypothesis.given(p=hypothesis.strategies.floats(min_value=1e-15, max_value=1.0 - 1e-15),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_logarithmic_noise(p, seed, sampling_rate, length):
    """Tests the class for logarithmic noise signals."""
    noise = sumpf.LogarithmicNoise(p, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.logseries(p, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Logarithmic noise")


@hypothesis.given(mean=hypothesis.strategies.floats(allow_nan=False, allow_infinity=False),
                  scale=hypothesis.strategies.floats(min_value=0.0, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_logistic_noise(mean, scale, seed, sampling_rate, length):
    """Tests the class for logistic noise signals."""
    noise = sumpf.LogisticNoise(mean, scale, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.logistic(mean, scale, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Logistic noise")


@hypothesis.given(shape=hypothesis.strategies.floats(min_value=1e-15, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_lomax_noise(shape, seed, sampling_rate, length):
    """Tests the class for Lomax noise signals."""
    noise = sumpf.LomaxNoise(shape, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.pareto(shape, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Lomax noise")


@hypothesis.given(mean=hypothesis.strategies.floats(min_value=1e-15, max_value=1e100, allow_nan=False, allow_infinity=False),
                  scale=hypothesis.strategies.floats(min_value=1e-15, max_value=1e300, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_wald_noise(mean, scale, seed, sampling_rate, length):
    """Tests the class for Wald noise signals."""
    noise = sumpf.WaldNoise(mean, scale, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.wald(mean, scale, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Wald noise")


@hypothesis.given(degrees_of_freedom=hypothesis.strategies.floats(min_value=1e-10, allow_nan=False, allow_infinity=False),
                  seed=hypothesis.strategies.integers(min_value=0, max_value=2 ** 32 - 1),
                  sampling_rate=tests.strategies.sampling_rates,
                  length=tests.strategies.short_lengths)
def test_chi_square_noise(degrees_of_freedom, seed, sampling_rate, length):
    """Tests the class for chi-square noise signals."""
    noise = sumpf.ChiSquareNoise(degrees_of_freedom, seed, sampling_rate, length)
    check_numpy_noise(noise=noise,
                      function=lambda g: g.chisquare(degrees_of_freedom, length),
                      seed=seed,
                      sampling_rate=sampling_rate,
                      length=length,
                      label="Chi-square noise")
