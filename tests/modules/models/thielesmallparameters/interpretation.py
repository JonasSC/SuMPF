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
import unittest

import sumpf
import _common as common


class TestThieleSmallParameterInterpretation(unittest.TestCase):
    """
    A TestCase for the NormalizeSignal module.
    """
    def test_functions(self):
        """
        Tests if the calculation of a parameter from a given set of other parameters
        works as expected.
        """
        rho = 1.2041
        c = 343.21
        # functions is a list of tuples that allow the automated testing of the
        # ThieleSmallParameterInterpretation's getter and setter methods.
        # Each tuple consists of three elements and represents a formula to
        # calculate a value from a given set of other parameters. First, that
        # value is calculated and compared to the expected result (the third
        # element of the tuple). After that, the calculation of each of the other
        # parameters with permutations of the formula is tested.
        # The first element of the tuple is the name of the parameter, that is
        # calculated by the formula. That name is the same as the name of the
        # respective getter or setter method, but without the "Get" or "Set".
        # The second element of the tuple is a tuple of the names of the parameters
        # that are required to compute a value with the formula.
        # The third element of the tuple is the result of the calculation, when
        # the other parameters are set to 1.0, 2.0, 3.0 etc. (their index in the
        # "other parameters"-tuple plus 1.0).
        functions = [("SuspensionCompliance", ("SuspensionStiffness",), 1.0),
                     ("DiaphragmRadius", ("DiaphragmArea",), (1.0 / math.pi) ** 0.5),
                     ("ResonanceFrequency", ("SuspensionCompliance", "DiaphragmMass"), 1.0 / (2.0 * math.pi * 2.0 ** 0.5)),
                     ("ElectricalQFactor", ("ResonanceFrequency", "DiaphragmMass", "VoiceCoilResistance", "ForceFactor"), 12.0 * math.pi / 16.0),
                     ("MechanicalQFactor", ("ResonanceFrequency", "DiaphragmMass", "MechanicalDamping"), 4.0 * math.pi / 3.0),
                     ("TotalQFactor", ("ElectricalQFactor", "MechanicalQFactor"), 2.0 / 3.0),
                     ("EquivalentComplianceVolume", ("DiaphragmArea", "SuspensionCompliance"), rho * c ** 2 * 2.0),
                     ("ResonanceImpedance", ("VoiceCoilResistance", "MechanicalQFactor", "ElectricalQFactor"), 1.0 + 2.0 / 3.0),
                     ("EfficiencyBandwidthProduct", ("ResonanceFrequency", "ElectricalQFactor"), 0.5)]
        for f in functions:
            interpretation = sumpf.modules.ThieleSmallParameterInterpretation(medium_density=rho, speed_of_sound=c)
            for i in range(len(f[1])):
                getattr(interpretation, "Set%s" % f[1][i])(i + 1.0)
            result = getattr(interpretation, "Get%s" % f[0])()
            self.assertEqual(result, f[2])
            for i in range(len(f[1])):
                interpretation2 = sumpf.modules.ThieleSmallParameterInterpretation(medium_density=rho, speed_of_sound=c)
                getattr(interpretation2, "Set%s" % f[0])(result)
                for j in range(len(f[1])):
                    if i != j:
                        getattr(interpretation2, "Set%s" % f[1][j])(j + 1.0)
                result2 = getattr(interpretation, "Get%s" % f[1][i])()
                self.assertEqual(result2, i + 1.0)

    @unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
    def test_errors(self):
        """
        Tests if the errors are raised as expected.
        """
        all_parameters = ["ThieleSmallParameters", "VoiceCoilResistance",
                          "VoiceCoilInductance", "ForceFactor", "SuspensionStiffness",
                          "MechanicalDamping", "DiaphragmMass", "DiaphragmArea",
                          "SuspensionCompliance", "DiaphragmRadius", "ResonanceFrequency",
                          "ElectricalQFactor", "MechanicalQFactor", "TotalQFactor",
                          "ResonanceImpedance", "EfficiencyBandwidthProduct"]
        ts_int = sumpf.modules.ThieleSmallParameterInterpretation()
        for p in all_parameters:
            self.assertRaises(RuntimeError, getattr(ts_int, "Get" + p))
            getattr(ts_int, "Set" + p)(getattr(ts_int, "Set" + p).GetType()())
            getattr(ts_int, "Get" + p)()
            getattr(ts_int, "Set" + p)(None)
            self.assertRaises(RuntimeError, getattr(ts_int, "Get" + p))

    def test_connectors(self):
        """
        Tests if the connectors are properly decorated.
        """
        all_parameters = set(["ThieleSmallParameters", "VoiceCoilResistance",
                              "VoiceCoilInductance", "ForceFactor", "SuspensionStiffness",
                              "MechanicalDamping", "DiaphragmMass", "DiaphragmArea",
                              "SuspensionCompliance", "DiaphragmRadius", "ResonanceFrequency",
                              "ElectricalQFactor", "MechanicalQFactor", "TotalQFactor",
                              "ResonanceImpedance", "EfficiencyBandwidthProduct"])
        additional_parameters = set(["MediumDensity", "SpeedOfSound"])
        ts_int = sumpf.modules.ThieleSmallParameterInterpretation()
        self.assertEqual(ts_int.SetThieleSmallParameters.GetType(), sumpf.ThieleSmallParameters)
        self.assertEqual(ts_int.GetThieleSmallParameters.GetType(), sumpf.ThieleSmallParameters)
        common.test_connection_observers(testcase=self,
                                         inputs=[getattr(ts_int, "Set" + p) for p in (all_parameters | additional_parameters)],
                                         noinputs=[],
                                         output=ts_int.GetThieleSmallParameters)
        for p in all_parameters - set(["ThieleSmallParameters"]):
            self.assertEqual(getattr(ts_int, "Get" + p).GetType(), float)
            self.assertEqual(getattr(ts_int, "Set" + p).GetType(), float)
            if p == "VoiceCoilInductance":
                common.test_connection_observers(testcase=self,
                                                 inputs=[ts_int.SetThieleSmallParameters, ts_int.SetVoiceCoilInductance],
                                                 noinputs=[getattr(ts_int, "Set" + q) for q in ((all_parameters | additional_parameters) - set(["VoiceCoilInductance", "ThieleSmallParameters"]))],
                                                 output=ts_int.GetVoiceCoilInductance)
            else:
                common.test_connection_observers(testcase=self,
                                                 inputs=[getattr(ts_int, "Set" + q) for q in ((all_parameters | additional_parameters) - set(["VoiceCoilInductance"]))],
                                                 noinputs=[ts_int.SetVoiceCoilInductance],
                                                 output=getattr(ts_int, "Get" + p))

