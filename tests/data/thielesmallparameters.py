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

import collections
import functools
import unittest
import sumpf


def testfunction(i, f=0.2, x=0.3, v=0.4, T=0.5):
    return f + x + v + T + 2.0 * i



class TestFunction(object):
    def __init__(self, i):
        self.__i = float(i)

    def __call__(self, f=0.3, x=0.2, v=0.1, T=0.0):
        return f + x + v + T + self.__i



class TestThieleSmallParameters(unittest.TestCase):
    def test_data(self):
        """
        Tests if all data can be set and retrieved as expected.
        """
        names = collections.OrderedDict()
        names["voicecoil_resistance"] = "GetVoiceCoilResistance"
        names["voicecoil_inductance"] = "GetVoiceCoilInductance"
        names["force_factor"] = "GetForceFactor"
        names["suspension_stiffness"] = "GetSuspensionStiffness"
        names["mechanical_damping"] = "GetMechanicalDamping"
        names["diaphragm_mass"] = "GetDiaphragmMass"
        names["diaphragm_area"] = "GetDiaphragmArea"
        all_kwargs = {}
        for i, n in enumerate(names):
            all_kwargs[n] = TestFunction(i)
            # test constant values
            kwargs = {n: 37.7056}
            ts = sumpf.ThieleSmallParameters(**kwargs)
            self.assertEqual(getattr(ts, names[n])(), kwargs[n])
            self.assertEqual(getattr(ts, names[n])(f=440.1, x=0.6, v=4.03, T=29.4), kwargs[n])
            self.assertFalse(ts.IsDefinedByAllParametersFunction())
            # test values that depend on the loudspeaker's state with a lambda function
            kwargs = {n: lambda f, x, v, T: f + x + v + T}
            ts = sumpf.ThieleSmallParameters(**kwargs)
            self.assertEqual(getattr(ts, names[n])(), 1020.0)
            self.assertEqual(getattr(ts, names[n])(f=440.1, x=0.6, v=4.03, T=29.4), 474.13)
            # test values that depend on the loudspeaker's state with a closure
            def tf(f=0.3, x=0.2, v=0.1, T=0.0):
                return f + x + v + T + float(i)
            kwargs = {n: tf}
            ts = sumpf.ThieleSmallParameters(**kwargs)
            self.assertEqual(getattr(ts, names[n])(), float(i) + 0.6)
            self.assertEqual(getattr(ts, names[n])(f=440.1, x=0.6, v=4.03, T=29.4), 474.13 + float(i))
            # test values that depend on the loudspeaker's state with a functools.partial object
            kwargs = {n: functools.partial(testfunction, i=float(i))}
            ts = sumpf.ThieleSmallParameters(**kwargs)
            self.assertEqual(getattr(ts, names[n])(), 2.0 * float(i) + 1.4)
            self.assertEqual(getattr(ts, names[n])(f=440.1, x=0.6, v=4.03, T=29.4), 474.13 + 2.0 * float(i))
            # test values that depend on the loudspeaker's state with a callable object
            kwargs = {n: TestFunction(i)}
            ts = sumpf.ThieleSmallParameters(**kwargs)
            self.assertEqual(getattr(ts, names[n])(), float(i) + 0.6)
            self.assertEqual(getattr(ts, names[n])(f=440.1, x=0.6, v=4.03, T=29.4), 474.13 + float(i))
        # test the GetAllParameters method
        ts = sumpf.ThieleSmallParameters(**all_kwargs)
        self.assertEqual(ts.GetAllParameters(), (1020.0, 1021.0, 1022.0, 1023.0, 1024.0, 1025.0, 1026.0))
        self.assertEqual(ts.GetAllParameters(f=440.1, x=0.6, v=4.03, T=29.4), (474.13, 475.13, 476.13, 477.13, 478.13, 479.13, 480.13))

    def test_getallparameters(self):
        """
        Tests the all_parameters parameter an the GetAllParameters method.
        """
        ts = sumpf.ThieleSmallParameters(all_parameters=lambda f, x, v, T: (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0))
        for i, n in enumerate(("GetVoiceCoilResistance", "GetVoiceCoilInductance",
                               "GetForceFactor", "GetSuspensionStiffness",
                               "GetMechanicalDamping", "GetDiaphragmMass",
                               "GetDiaphragmArea")):
            self.assertEqual(getattr(ts, n)(), float(i))
            self.assertEqual(getattr(ts, n)(f=440.1, x=0.6, v=4.03, T=29.4), float(i))
        self.assertTrue(ts.IsDefinedByAllParametersFunction())
        self.assertEqual(ts.GetAllParameters(), (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0))
        self.assertEqual(ts.GetAllParameters(f=440.1, x=0.6, v=4.03, T=29.4), (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0))

