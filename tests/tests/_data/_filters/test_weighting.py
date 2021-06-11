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

"""Contains the tests for the frequency weighting filters."""

import math
import sumpf
from sumpf._data._filters._base import Quotient, Polynomial


def test_a_weighting_table():
    """checks if the :class:`~sumpf.AWeighting` filter has a magnitude, which is
    close to the values, that are specified in ANSI S1.4.
    """
    table = {
        10.0: -70.4,
        12.589: -63.4,
        15.849: -56.7,
        19.953: -50.5,
        25.119: -44.7,
        31.623: -39.4,
        39.811: -34.6,
        50.119: -30.2,
        63.096: -26.2,
        79.433: -22.5,
        100.0: -19.1,
        125.89: -16.1,
        158.49: -13.4,
        199.53: -10.9,
        251.19: -8.6,
        316.23: -6.6,
        398.11: -4.8,
        501.19: -3.2,
        630.96: -1.9,
        794.33: -0.8,
        1000.0: 0.0,
        1258.9: 0.6,
        1584.9: 1.0,
        1995.3: 1.2,
        2511.9: 1.3,
        3162.3: 1.2,
        3981.1: 1.0,
        5011.9: 0.5,
        6309.6: -0.1,
        7943.3: -1.1,
        10000.0: -2.5,
        12589.0: -4.3,
        15849.0: -6.6,
        19953.0: -9.3,
    }
    weighting = sumpf.AWeighting()
    tolerance = 0.05
    for frequency, decibels in table.items():
        upper_tolerance = 10 ** ((decibels + tolerance) / 20)
        lower_tolerance = 10 ** ((decibels - tolerance) / 20)
        assert lower_tolerance < abs(weighting(frequency)[0]) < upper_tolerance


def test_a_weighting_poles():
    """checks if the :class:`~sumpf.AWeighting` filter has poles, which are close
    to the frequencies, that are specified in IEC 61672-1.
    """
    f1 = 20.6
    f2 = 107.7
    f3 = 737.9
    f4 = 12194.2
    expected_poles = [f1, f1, f2, f3, f4, f4]
    weighting = sumpf.AWeighting()
    poles = []
    for term in weighting.transfer_functions()[0].factors:
        if isinstance(term, Quotient):
            coefficients = term.denominator.coefficients
            if len(coefficients) == 2:
                poles.append(coefficients[-1] / 2 / math.pi)
            else:
                raise NotImplementedError("Evaluating filter terms with more than one pole is not implemented")
    for pole, expected in zip(sorted(poles), expected_poles):
        assert round(pole, 1) == expected


def test_b_weighting_table():
    """checks if the :class:`~sumpf.BWeighting` filter has a magnitude, which is
    close to the values, that are specified in ANSI S1.4.
    """
    table = {
        10.0: -38.2,
        12.589: -33.2,
        15.849: -28.5,
        19.953: -24.2,
        25.119: -20.4,
        31.623: -17.1,
        39.811: -14.2,
        50.119: -11.6,
        63.096: -9.3,
        79.433: -7.4,
        100.0: -5.6,
        125.89: -4.2,
        158.49: -3.0,
        199.53: -2.0,
        251.19: -1.3,
        316.23: -0.8,
        398.11: -0.5,
        501.19: -0.3,
        630.96: -0.1,
        794.33: 0.0,
        1000.0: 0.0,
        1258.9: 0.0,
        1584.9: 0.0,
        1995.3: -0.1,
        2511.9: -0.2,
        3162.3: -0.4,
        3981.1: -0.7,
        5011.9: -1.2,
        6309.6: -1.9,
        7943.3: -2.9,
        10000.0: -4.3,
        12589.0: -6.1,
        15849.0: -8.4,
        19953.0: -11.1,
    }
    weighting = sumpf.BWeighting()
    tolerance = 0.05
    for frequency, decibels in table.items():
        upper_tolerance = 10 ** ((decibels + tolerance) / 20)
        lower_tolerance = 10 ** ((decibels - tolerance) / 20)
        assert lower_tolerance < abs(weighting(frequency)[0]) < upper_tolerance


def test_b_weighting_poles():
    """checks if the :class:`~sumpf.BWeighting` filter has poles, which are close
    to the frequencies, that are specified in the withdrawn standard IEC 60651.
    """
    f1 = 20.6
    fb = 158.5
    f4 = 12194.2
    expected_poles = [f1, f1, fb, f4, f4]
    weighting = sumpf.BWeighting()
    poles = []
    for term in weighting.transfer_functions()[0].factors:
        if isinstance(term, Quotient):
            coefficients = term.denominator.coefficients
            if len(coefficients) == 2:
                poles.append(coefficients[-1] / 2 / math.pi)
            else:
                raise NotImplementedError("Evaluating filter terms with more than one pole is not implemented")
    for pole, expected in zip(sorted(poles), expected_poles):
        assert round(pole, 1) == expected


def test_c_weighting_table():
    """checks if the :class:`~sumpf.CWeighting` filter has a magnitude, which is
    close to the values, that are specified in ANSI S1.4.
    """
    table = {
        10.0: -14.3,
        12.589: -11.2,
        15.849: -8.5,
        19.953: -6.2,
        25.119: -4.4,
        31.623: -3.0,
        39.811: -2.0,
        50.119: -1.3,
        63.096: -0.8,
        79.433: -0.5,
        100.0: -0.3,
        125.89: -0.2,
        158.49: -0.1,
        199.53: 0.0,
        251.19: 0.0,
        316.23: 0.0,
        398.11: 0.0,
        501.19: 0.0,
        630.96: 0.0,
        794.33: 0.0,
        1000.0: 0.0,
        1258.9: 0.0,
        1584.9: -0.1,
        1995.3: -0.2,
        2511.9: -0.3,
        3162.3: -0.5,
        3981.1: -0.8,
        5011.9: -1.3,
        6309.6: -2.0,
        7943.3: -3.0,
        10000.0: -4.4,
        12589.0: -6.2,
        15849.0: -8.5,
        19953.0: -11.2,
    }
    weighting = sumpf.CWeighting()
    tolerance = 0.05
    for frequency, decibels in table.items():
        upper_tolerance = 10 ** ((decibels + tolerance) / 20)
        lower_tolerance = 10 ** ((decibels - tolerance) / 20)
        assert lower_tolerance < abs(weighting(frequency)[0]) < upper_tolerance


def test_c_weighting_poles():
    """checks if the :class:`~sumpf.CWeighting` filter has poles, which are close
    to the frequencies, that are specified in IEC 61672-1.
    """
    f1 = 20.6
    f4 = 12194.2
    expected_poles = [f1, f1, f4, f4]
    weighting = sumpf.CWeighting()
    poles = []
    for term in weighting.transfer_functions()[0].factors:
        if isinstance(term, Quotient):
            coefficients = term.denominator.coefficients
            if len(coefficients) == 2:
                poles.append(coefficients[-1] / 2 / math.pi)
            else:
                raise NotImplementedError("Evaluating filter terms with more than one pole is not implemented")
    for pole, expected in zip(sorted(poles), expected_poles):
        assert round(pole, 1) == expected


def test_d_weighting_table():
    """checks if the :class:`~sumpf.DWeighting` filter has a magnitude, which is
    close to the values, that are specified in the reference table.
    """
    table = {
        10.0: -26.6,
        12.589: -24.6,
        15.849: -22.6,
        19.953: -20.6,
        25.119: -18.7,
        31.623: -16.7,
        39.811: -14.7,
        50.119: -12.8,
        63.096: -10.9,
        79.433: -9.0,
        100.0: -7.2,
        125.89: -5.5,
        158.49: -4.0,
        199.53: -2.6,
        251.19: -1.6,
        316.23: -0.8,
        398.11: -0.4,
        501.19: -0.3,
        630.96: -0.5,
        794.33: -0.6,
        1000.0: 0.0,
        1258.9: 2.0,
        1584.9: 4.9,
        1995.3: 7.9,
        2511.9: 10.4,
        3162.3: 11.5,  # 11.6,
        3981.1: 11.1,
        5011.9: 9.6,
        6309.6: 7.6,
        7943.3: 5.5,
        10000.0: 3.4,
        12589.0: 1.4,
        15849.0: -0.7,
        19953.0: -2.7,
    }
    weighting = sumpf.DWeighting()
    tolerance = 0.05
    for frequency, decibels in table.items():
        upper_tolerance = 10 ** ((decibels + tolerance) / 20)
        lower_tolerance = 10 ** ((decibels - tolerance) / 20)
        assert lower_tolerance < abs(weighting(frequency)[0]) < upper_tolerance


def test_d_weighting_polynomials():
    """checks if the :class:`~sumpf.DWeighting` filter has has a transfer function
    with coefficients like they are specified on the [Wikipedia page](https://en.wikipedia.org/wiki/A-weighting#D_2).
    """
    n1 = (1.0, 0.0)
    n2 = (1.0, 6532, 40975379.2)
    d1 = (1.0, 1776.3)
    d2 = (1.0, 7288.5)
    d3 = (1.0, 21513.6, 388362142.9)
    numerators = {n1, n2}
    denominators = {d1, d2, d3}
    weighting = sumpf.DWeighting()
    for term in weighting.transfer_functions()[0].factors:
        if isinstance(term, Quotient):
            if isinstance(term.numerator, Polynomial):
                n = tuple(round(c, 1) for c in term.numerator.coefficients)
                assert n in numerators
                numerators.remove(n)
            d = tuple(round(c, 1) for c in term.denominator.coefficients)
            assert d in denominators
            denominators.remove(d)
    assert not numerators
    assert not denominators


def test_u_weighting_table():
    """checks if the :class:`~sumpf.UWeighting` filter has a magnitude, which is
    close to the values, that are specified in IEC 61012.
    """
    table = {
        10.0: 0.0,
        12.589: 0.0,
        15.849: 0.0,
        19.953: 0.0,
        25.119: 0.0,
        31.623: 0.0,
        39.811: 0.0,
        50.119: 0.0,
        63.096: 0.0,
        79.433: 0.0,
        100.0: 0.0,
        125.89: 0.0,
        158.49: 0.0,
        199.53: 0.0,
        251.19: 0.0,
        316.23: 0.0,
        398.11: 0.0,
        501.19: 0.0,
        630.96: 0.0,
        794.33: 0.0,
        1000.0: 0.0,
        1258.9: 0.0,
        1584.9: 0.0,
        1995.3: 0.0,
        2511.9: 0.0,
        3162.3: 0.0,
        3981.1: 0.0,
        5011.9: 0.0,
        6309.6: 0.0,
        7943.3: 0.1,  # 0.0,
        10000.0: 0.0,
        12589.0: -2.8,
        15849.0: -13.0,
        19953.0: -25.3,
        25119.0: -37.6,
        31623.0: -49.7,
        39811.0: -61.8,
    }
    weighting = sumpf.UWeighting()
    tolerance = 0.05
    for frequency, decibels in table.items():
        upper_tolerance = 10 ** ((decibels + tolerance) / 20)
        lower_tolerance = 10 ** ((decibels - tolerance) / 20)
        assert lower_tolerance < abs(weighting(frequency)[0]) < upper_tolerance


def test_u_weighting_poles():
    """checks if the :class:`~sumpf.UWeighting` filter has poles, which are close
    to the frequencies, that are specified in IEC 61012.
    """
    f1 = 12200
    f3 = 7850 - 8800j
    f4 = 7850 + 8800j
    f5 = 2900 - 12150j
    f6 = 2900 + 12150j
    expected_poles = [f1, f1, f3, f4, f5, f6]
    weighting = sumpf.UWeighting()
    poles = []
    for term in weighting.transfer_functions()[0].factors:
        if isinstance(term, Quotient):
            coefficients = term.denominator.coefficients
            if len(coefficients) == 2:
                poles.append(coefficients[-1] / 2 / math.pi)
            else:
                raise NotImplementedError("Evaluating filter terms with more than one pole is not implemented")
    for pole, expected in zip(poles, expected_poles):
        assert round(pole, 1) == expected
