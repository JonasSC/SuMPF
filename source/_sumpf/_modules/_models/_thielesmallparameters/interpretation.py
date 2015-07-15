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


def parameter_getter(parameter_name):
    """
    This decorator encapsulates the raising of the ParameterNotSpecifiedError.
    It also maintains the callers list, which is a call stack of getter methods
    that have been called to calculate a requested parameter value.
    """
    def decorator(function):
        def new_function(self, callers=None):
            if callers is None:
                callers = [function.__name__]
            elif function.__name__ in callers:
                raise ParameterNotSpecifiedError("The %s has not been specified and neither have the values that are necessary to calculate it." % parameter_name)
            else:
                callers.append(function.__name__)
            result = function(self, callers)
            callers.remove(function.__name__)
            return result
        return new_function
    return decorator



class ParameterNotSpecifiedError(Exception):
    """
    This error is raised and caught inside the parameter calculations of the
    ThieleSmallParameterInterpretation class. It is not raised to be caught outside
    this class.
    This error is raised, when not all parameters, that are required for a certain
    calculation, are specified.
    """
    pass



class ThieleSmallParameterInterpretation(object):
    """
    This class calculates loudspeaker parameters from other parameters.
    It can be used to create a ThieleSmallParameters instance from a parameter
    set that has been specified by a loudspeaker manufacturer. Or it can be
    used to calculate parameters that have not been specified.

    It is possible to specify parameters for this class redundantly, by specifying
    a ThieleSmallParameters instance, specifying the value explicitly and/or specifying
    parameters from which the respective parameter can be calculated.
    When retrieving a parameter, the class will look first, if the parameter has
    been specified explicitly, then, if it is one of the parameters of the
    ThieleSmallParameters class, it will check if such an instance has been given
    and if that fails, the class will try to calculate the requested parameter
    from other parameters. If the calculation is not possible, due to missing other
    parameters, a RuntimeError is raised.
    """
    def __init__(self,
                 thiele_small_parameters=None,
                 voicecoil_resistance=None,
                 voicecoil_inductance=None,
                 force_factor=None,
                 suspension_stiffness=None,
                 mechanical_damping=None,
                 diaphragm_mass=None,
                 diaphragm_area=None,
                 suspension_compliance=None,
                 diaphragm_radius=None,
                 resonance_frequency=None,
                 electrical_q_factor=None,
                 mechanical_q_factor=None,
                 total_q_factor=None,
                 equivalent_compliance_volume=None,
                 resonance_impedance=None,
                 efficiency_bandwidth_product=None,
                 medium_density=1.2041,
                 speed_of_sound=343.21):
        """
        It is not necessary to specify all parameters, as most parameters can be
        calculated from other parameters.
        @param thiele_small_parameters: a ThieleSmallParameters instance
        @param voicecoil_resistance: a float value for the voice coil resistance in Ohms
        @param voicecoil_inductance: a float value for the voice coil inductance in Henrys
        @param force_factor: a float value for the force factor in Tesla times meters
        @param suspension_stiffness: a float value for the suspension stiffness in Newtons per meter
        @param mechanical_damping: a float value for the mechanical damping in Newton times seconds per meter
        @param diaphragm_mass: a float value for the combined mass of the diaphragm, the voice coil and the acoustic load in kilograms
        @param diaphragm_area: a float value for the effective diaphragm area in square meters
        @param suspension_compliance: a float value for the suspension compliance in meters per Newton
        @param diaphragm_radius: a float value for the radius from which the effective diaphragm area can be calculated in meters
        @param resonance_frequency: a float value for the resonance frequency in Hertz
        @param electrical_q_factor: a float value for the electrical Q factor
        @param mechanical_q_factor: a float value for the mechanical Q factor
        @param total_q_factor: a float value for the total Q factor
        @param equivalent_compliance_volume: a float value for the equivalent compliance volume in cubic meters
        @param resonance_impedance: a float value for the impedance at the resonance frequency in Ohms
        @param efficiency_bandwidth_product: a float value for the efficiency bandwidth product in Hertz
        @param medium_density: a float value for the density of the medium, in which the loudspeaker radiates sound (probably air) in kilograms per cubic meter
        @param speed_of_sound: a float value for the speed of sound in the medium, in which the loudspeaker radiates sound (probably air) in meters per second
        """
        self.__thiele_small_parameters = thiele_small_parameters
        self.__voicecoil_resistance = voicecoil_resistance
        self.__voicecoil_inductance = voicecoil_inductance
        self.__force_factor = force_factor
        self.__suspension_stiffness = suspension_stiffness
        self.__mechanical_damping = mechanical_damping
        self.__diaphragm_mass = diaphragm_mass
        self.__diaphragm_area = diaphragm_area
        self.__suspension_compliance = suspension_compliance
        self.__diaphragm_radius = diaphragm_radius
        self.__resonance_frequency = resonance_frequency
        self.__electrical_q_factor = electrical_q_factor
        self.__mechanical_q_factor = mechanical_q_factor
        self.__total_q_factor = total_q_factor
        self.__equivalent_compliance_volume = equivalent_compliance_volume
        self.__resonance_impedance = resonance_impedance
        self.__efficiency_bandwidth_product = efficiency_bandwidth_product
        self.__medium_density = medium_density
        self.__speed_of_sound = speed_of_sound

    ##################
    # Getter methods #
    ##################

    @sumpf.Output(sumpf.ThieleSmallParameters)
    def GetThieleSmallParameters(self):
        """
        Calculates and returns a ThieleSmallParameters instance from the parameters
        that have been passed to this object.
        @retval : a ThieleSmallParameters instance
        """
        return self.__GetThieleSmallParameters()

    @sumpf.Output(float)
    def GetVoiceCoilResistance(self):
        """
        Calculates and returns the voice coil resistance in Ohms from the parameters,
        that have been passed to this object.
        @retval : a float
        """
        return self.__GetVoiceCoilResistance()

    @sumpf.Output(float)
    def GetVoiceCoilInductance(self):
        """
        Calculates and returns the voice coil inductance in Henrys from the
        parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetVoiceCoilInductance()

    @sumpf.Output(float)
    def GetForceFactor(self):
        """
        Calculates and returns the force factor in Tesla times meters from the
        parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetForceFactor()

    @sumpf.Output(float)
    def GetSuspensionStiffness(self):
        """
        Calculates and returns the suspension stiffness in Newtons per meter from
        the parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetSuspensionStiffness()

    @sumpf.Output(float)
    def GetMechanicalDamping(self):
        """
        Calculates and returns the mechanical damping in Newton times seconds per
        meter from the parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetMechanicalDamping()

    @sumpf.Output(float)
    def GetDiaphragmMass(self):
        """
        Calculates and returns the combined mass of the diaphragm, the voice coil
        and the acoustic load in kilograms from the parameters, that have been
        passed to this object.
        @retval : a float
        """
        return self.__GetDiaphragmMass()

    @sumpf.Output(float)
    def GetDiaphragmArea(self):
        """
        Calculates and returns the effective diaphragm area in square meters from
        the parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetDiaphragmArea()

    @sumpf.Output(float)
    def GetSuspensionCompliance(self):
        """
        Calculates and returns the suspension compliance in meters per Newton
        from the parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetSuspensionCompliance()

    @sumpf.Output(float)
    def GetDiaphragmRadius(self):
        """
        Calculates and returns the radius, from which the effective diaphragm area
        can be calculated, in meters from the parameters, that have been passed
        to this object.
        @retval : a float
        """
        return self.__GetDiaphragmRadius()

    @sumpf.Output(float)
    def GetResonanceFrequency(self):
        """
        Calculates and returns the resonance frequency in Hertz from the parameters,
        that have been passed to this object.
        @retval : a float
        """
        return self.__GetResonanceFrequency()

    @sumpf.Output(float)
    def GetElectricalQFactor(self):
        """
        Calculates and returns the electrical Q factor from the parameters, that
        have been passed to this object.
        @retval : a float
        """
        return self.__GetElectricalQFactor()

    @sumpf.Output(float)
    def GetMechanicalQFactor(self):
        """
        Calculates and returns the mechanical Q factor from the parameters, that
        have been passed to this object.
        @retval : a float
        """
        return self.__GetMechanicalQFactor()

    @sumpf.Output(float)
    def GetTotalQFactor(self):
        """
        Calculates and returns the total Q factor from the parameters, that have
        been passed to this object.
        @retval : a float
        """
        return self.__GetTotalQFactor()

    @sumpf.Output(float)
    def GetEquivalentComplianceVolume(self):
        """
        Calculates and returns the equivalent compliance volume in cubic meters
        from the parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetEquivalentComplianceVolume()

    @sumpf.Output(float)
    def GetResonanceImpedance(self):
        """
        Calculates and returns the electrical input impedance at the resonance
        frequency in Ohms from the parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetResonanceImpedance()

    @sumpf.Output(float)
    def GetEfficiencyBandwidthProduct(self):
        """
        Calculates and returns the efficiency bandwidth product in Hertz from the
        parameters, that have been passed to this object.
        @retval : a float
        """
        return self.__GetEfficiencyBandwidthProduct()

    ##################
    # setter methods #
    ##################

    @sumpf.Input(sumpf.ThieleSmallParameters, ("GetThieleSmallParameters", "GetVoiceCoilResistance",
    "GetVoiceCoilInductance", "GetForceFactor", "GetSuspensionStiffness", "GetMechanicalDamping",
    "GetDiaphragmMass", "GetDiaphragmArea", "GetSuspensionCompliance", "GetDiaphragmRadius",
    "GetResonanceFrequency", "GetElectricalQFactor", "GetMechanicalQFactor", "GetTotalQFactor",
    "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetThieleSmallParameters(self, parameters):
        """
        Specifies a ThieleSmallParameters instance from which all other values
        can be calculated.
        @param parameters: a ThieleSmallParameters instance
        """
        self.__thiele_small_parameters = parameters

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetVoiceCoilResistance(self, value):
        """
        Specifies a value for the voice coil resistance from which other parameters
        can be calculated.
        @param value: a float value for the voice coil resistance in Ohms
        """
        self.__voicecoil_resistance = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilInductance"))
    def SetVoiceCoilInductance(self, value):
        """
        Specifies a value for the voice coil inductance from which other parameters
        can be calculated.
        @param value: a float value for the voice coil inductance in Henrys
        """
        self.__voicecoil_inductance = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetForceFactor(self, value):
        """
        Specifies a value for the force factor from which other parameters can be
        calculated.
        @param value: a float value for the force factor in Tesla times meters
        """
        self.__force_factor = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetSuspensionStiffness(self, value):
        """
        Specifies a value for the suspension stiffness from which other parameters
        can be calculated.
        @param value: a float value for the suspension stiffness in Newtons per meter
        """
        self.__suspension_stiffness = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetMechanicalDamping(self, value):
        """
        Specifies a value for the mechanical damping from which other parameters
        can be calculated.
        @param value: a float value for the mechanical damping in Newton times seconds per meter
        """
        self.__mechanical_damping = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetDiaphragmMass(self, value):
        """
        Specifies a value for the diaphragm mass including the masses of the voice
        coil and the acoustic load. This parameter can be used to calculate other
        parameters.
        @param value: a float value for the combined diaphragm mass in kilograms
        """
        self.__diaphragm_mass = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetDiaphragmArea(self, value):
        """
        Specifies a value for the effective diaphragm area from which other parameters
        can be calculated.
        @param value: a float value for the effective diaphragm area in square meters
        """
        self.__diaphragm_area = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetSuspensionCompliance(self, value):
        """
        Specifies a value for the suspension compliance from which the suspension
        stiffness can be calculated.
        @param value: a float value for the suspension compliance in meters per Newton
        """
        self.__suspension_compliance = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetDiaphragmRadius(self, value):
        """
        Specifies a value for the effective diaphragm radius from which the effective
        diaphragm area can be calculated.
        @param value: a float value for the radius in meters
        """
        self.__diaphragm_radius = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetResonanceFrequency(self, value):
        """
        Specifies a value for the resonance frequency from which other parameters
        can be calculated.
        @param value: a float value for the resonance frequency in Hertz
        """
        self.__resonance_frequency = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetElectricalQFactor(self, value):
        """
        Specifies a value for the electrical Q factor from which other parameters
        can be calculated.
        @param value: a float value for the electrical Q factor
        """
        self.__electrical_q_factor = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetMechanicalQFactor(self, value):
        """
        Specifies a value for the mechanical Q factor from which other parameters
        can be calculated.
        @param value: a float value for the mechanical Q factor
        """
        self.__mechanical_q_factor = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetTotalQFactor(self, value):
        """
        Specifies a value for the total Q factor from which other parameters
        can be calculated.
        @param value: a float value for the total Q factor
        """
        self.__total_q_factor = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetEquivalentComplianceVolume(self, value):
        """
        Specifies a value for the equivalent compliance volume from which other
        parameters can be calculated.
        @param value: a float value for the equivalent compliance volume in cubic meters
        """
        self.__equivalent_compliance_volume = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetResonanceImpedance(self, value):
        """
        Specifies a value for the electrical impedance at the resonance frequency
        from which other parameters can be calculated.
        @param value: a float value for the impedance at the resonance frequency in Ohms
        """
        self.__resonance_impedance = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetEfficiencyBandwidthProduct(self, value):
        """
        Specifies a value for the efficiency bandwidth product from which other
        parameters can be calculated.
        @param value: a float value for the efficiency bandwidth product in Hertz
        """
        self.__efficiency_bandwidth_product = value

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetMediumDensity(self, density):
        """
        Specifies a value for the density of the medium in which the loudspeaker
        radiates sound (probably air).
        @param value: a float value for the density in kilograms per cubic meter
        """
        self.__medium_density = density

    @sumpf.Input(float, ("GetThieleSmallParameters", "GetVoiceCoilResistance", "GetForceFactor",
    "GetSuspensionStiffness", "GetMechanicalDamping", "GetDiaphragmMass", "GetDiaphragmArea",
    "GetSuspensionCompliance", "GetDiaphragmRadius", "GetResonanceFrequency", "GetElectricalQFactor",
    "GetMechanicalQFactor", "GetTotalQFactor", "GetResonanceImpedance", "GetEfficiencyBandwidthProduct"))
    def SetSpeedOfSound(self, speed):
        """
        Specifies a value for the speed of sound in the medium in which the loudspeaker
        radiates sound (probably air).
        @param value: a float value for the speed of sound in meters per second
        """
        self.__speed_of_sound = speed

    ##########################
    # private getter methods #
    ##########################

    @parameter_getter("set of Thiele-Small parameters")
    def __GetThieleSmallParameters(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested object immediately
        if self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters
        else:
            try:
                # get the necessary values to create a new object
                R = self.__GetVoiceCoilResistance(callers)
                L = self.__GetVoiceCoilInductance(callers)
                M = self.__GetForceFactor(callers)
                k = self.__GetSuspensionStiffness(callers)
                w = self.__GetMechanicalDamping(callers)
                m = self.__GetDiaphragmMass(callers)
                S = self.__GetDiaphragmArea(callers)
                return sumpf.ThieleSmallParameters(voicecoil_resistance=R,
                                                   voicecoil_inductance=L,
                                                   force_factor=M,
                                                   suspension_stiffness=k,
                                                   mechanical_damping=w,
                                                   diaphragm_mass=m,
                                                   diaphragm_area=S)
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetThieleSmallParameters":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("voice coil resistance")
    def __GetVoiceCoilResistance(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__voicecoil_resistance is not None:
            return self.__voicecoil_resistance
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetVoiceCoilResistance()
        else:
            try:
                # try to calculate the voice coil resistance from the electrical q-factor
                Qe = self.__GetElectricalQFactor(callers)
                fr = self.__GetResonanceFrequency(callers)
                m = self.__GetDiaphragmMass(callers)
                M = self.__GetForceFactor(callers)
                return (Qe * M ** 2) / (2.0 * math.pi * fr * m)
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the electrical q-factor from the resonance impedance
                    Zmax = self.__GetResonanceImpedance(callers)
                    Qe = self.__GetElectricalQFactor(callers)
                    Qms = self.__GetMechanicalQFactor(callers)
                    return (Qe * Zmax) / (Qe + Qms)
                except ParameterNotSpecifiedError as e:
                    if callers[0] == "__GetVoiceCoilResistance":
                        return self.__OnParameterNotSpecified(exception=e)
                    else:
                        raise e

    @parameter_getter("voice coil inductance")
    def __GetVoiceCoilInductance(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        if self.__voicecoil_inductance is not None:
            return self.__voicecoil_inductance
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetVoiceCoilInductance()
        else:
            e = ParameterNotSpecifiedError("The voice coil inductance has not been specified and neither have the values that are necessary to calculate it.")
            return self.__OnParameterNotSpecified(exception=e)

    @parameter_getter("force factor")
    def __GetForceFactor(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__force_factor is not None:
            return self.__force_factor
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetForceFactor()
        else:
            try:
                # try to calculate the force factor from the electrical q-factor
                Qe = self.__GetElectricalQFactor(callers)
                fr = self.__GetResonanceFrequency(callers)
                m = self.__GetDiaphragmMass(callers)
                R = self.__GetVoiceCoilResistance(callers)
                return ((2.0 * math.pi * fr * m * R) / Qe) ** 0.5
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetForceFactor":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("suspension stiffness")
    def __GetSuspensionStiffness(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__suspension_stiffness is not None:
            return self.__suspension_stiffness
        elif self.__suspension_compliance is not None:
            return 1.0 / self.__suspension_compliance
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetSuspensionStiffness()
        else:
            try:
                # try to calculate the suspension stiffness from the suspension compliance
                n = self.__GetSuspensionCompliance(callers)
                return 1.0 / n
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetSuspensionStiffness":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("mechanical damping")
    def __GetMechanicalDamping(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__mechanical_damping is not None:
            return self.__mechanical_damping
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetMechanicalDamping()
        else:
            try:
                # try to calculate the mechanical damping from the mechanical q-factor
                Qms = self.__GetMechanicalQFactor(callers)
                fr = self.__GetResonanceFrequency(callers)
                m = self.__GetDiaphragmMass(callers)
                return (2.0 * math.pi * fr * m) / Qms
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetMechanicalDamping":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("diaphragm mass")
    def __GetDiaphragmMass(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__diaphragm_mass is not None:
            return self.__diaphragm_mass
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetDiaphragmMass()
        else:
            try:
                # try to calculate the diaphragm mass from the resonance frequency
                fr = self.__GetResonanceFrequency(callers)
                n = self.__GetSuspensionCompliance(callers)
                return 1.0 / (n * (2.0 * math.pi * fr) ** 2)
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the diaphragm mass from the mechanical q-factor
                    Qms = self.__GetMechanicalQFactor(callers)
                    fr = self.__GetResonanceFrequency(callers)
                    w = self.__GetMechanicalDamping(callers)
                    return (Qms * w) / (2.0 * math.pi * fr)
                except ParameterNotSpecifiedError:
                    try:
                        # try to calculate the diaphragm mass from the electrical q-factor
                        Qe = self.__GetElectricalQFactor(callers)
                        fr = self.__GetResonanceFrequency(callers)
                        R = self.__GetVoiceCoilResistance(callers)
                        M = self.__GetForceFactor(callers)
                        return (Qe * M ** 2) / (2.0 * math.pi * fr * R)
                    except ParameterNotSpecifiedError:
                        if callers[0] == "__GetDiaphragmMass":
                            return self.__OnParameterNotSpecified(exception=e)
                        else:
                            raise e

    @parameter_getter("diaphragm area")
    def __GetDiaphragmArea(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__diaphragm_area is not None:
            return self.__diaphragm_area
        elif self.__thiele_small_parameters is not None:
            return self.__thiele_small_parameters.GetDiaphragmArea()
        else:
            try:
                # try to calculate the diaphragm area from the equivalent compliance volume
                Vas = self.__GetEquivalentComplianceVolume(callers)
                n = self.__GetSuspensionCompliance(callers)
                rho = self.__medium_density
                c = self.__speed_of_sound
                return (Vas / (rho * c ** 2 * n)) ** 0.5
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the diaphragm area from the diaphragm radius
                    r = self.__GetDiaphragmRadius(callers)
                    return math.pi * r ** 2
                except ParameterNotSpecifiedError:
                    if callers[0] == "__GetDiaphragmArea":
                        return self.__OnParameterNotSpecified(exception=e)
                    else:
                        raise e

    @parameter_getter("suspension compliance")
    def __GetSuspensionCompliance(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__suspension_compliance is not None:
            return self.__suspension_compliance
        elif self.__suspension_stiffness is not None:
            return 1.0 / self.__suspension_stiffness
        elif self.__thiele_small_parameters is not None:
            return 1.0 / self.__thiele_small_parameters.GetSuspensionStiffness()
        else:
            try:
                # try to calculate the suspension compliance from the resonance frequency
                fr = self.__GetResonanceFrequency(callers)
                m = self.__GetDiaphragmMass(callers)
                return 1.0 / (m * (2.0 * math.pi * fr) ** 2)
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the suspension compliance from the equivalent compliance volume
                    Vas = self.__GetEquivalentComplianceVolume(callers)
                    S = self.__GetDiaphragmArea(callers)
                    rho = self.__medium_density
                    c = self.__speed_of_sound
                    return Vas / (rho * c ** 2 * S ** 2)
                except ParameterNotSpecifiedError:
                    if callers[0] == "__GetSuspensionCompliance":
                        return self.__OnParameterNotSpecified(exception=e)
                    else:
                        raise e

    @parameter_getter("diaphragm radius")
    def __GetDiaphragmRadius(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__diaphragm_radius is not None:
            return self.__diaphragm_radius
        else:
            try:
                # try to calculate the diaphragm radius from the diaphragm area
                S = self.__GetDiaphragmArea(callers)
                return (S / math.pi) ** 0.5
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetDiaphragmRadius":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("resonance frequency")
    def __GetResonanceFrequency(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__resonance_frequency is not None:
            return self.__resonance_frequency
        else:
            try:
                # try to calculate the resonance frequency from the suspension compliance and the diaphragm mass
                n = self.__GetSuspensionCompliance(callers)
                m = self.__GetDiaphragmMass(callers)
                return 1.0 / (2.0 * math.pi * (n * m) ** 0.5)
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the resonance frequency from the mechanical q-factor
                    Qms = self.__GetMechanicalQFactor(callers)
                    w = self.__GetMechanicalDamping(callers)
                    m = self.__GetDiaphragmMass(callers)
                    return Qms * w / (2.0 * math.pi * m)
                except ParameterNotSpecifiedError:
                    try:
                        # try to calculate the resonance frequency from the electrical q-factor
                        Qe = self.__GetElectricalQFactor(callers)
                        R = self.__GetVoiceCoilResistance(callers)
                        M = self.__GetForceFactor(callers)
                        m = self.__GetDiaphragmMass(callers)
                        return Qe * M ** 2 / (2.0 * math.pi * m * R)
                    except ParameterNotSpecifiedError:
                        if callers[0] == "__GetResonanceFrequency":
                            return self.__OnParameterNotSpecified(exception=e)
                        else:
                            raise e

    @parameter_getter("electrical q-factor")
    def __GetElectricalQFactor(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__electrical_q_factor is not None:
            return self.__electrical_q_factor
        else:
            try:
                # try to calculate the electrical q-factor from the electrical parameters
                R = self.__GetVoiceCoilResistance(callers)
                M = self.__GetForceFactor(callers)
                m = self.__GetDiaphragmMass(callers)
                fr = self.__GetResonanceFrequency(callers)
                return (2.0 * math.pi * fr * m * R) / (M ** 2)
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the electrical q-factor from the other q-factors
                    Qt = self.__GetTotalQFactor(callers)
                    Qms = self.__GetMechanicalQFactor(callers)
                    return (Qms * Qt) / (Qms - Qt)
                except ParameterNotSpecifiedError:
                    try:
                        # try to calculate the electrical q-factor from the resonance impedance
                        Zmax = self.__GetResonanceImpedance(callers)
                        R = self.__GetVoiceCoilResistance(callers)
                        Qms = self.__GetMechanicalQFactor(callers)
                        return (Qms * R) / (Zmax - R)
                    except ParameterNotSpecifiedError:
                        try:
                            # try to calculate the electrical q-factor from the efficiency bandwidth product
                            fr = self.__GetResonanceFrequency(callers)
                            EBP = self.__GetEfficiencyBandwidthProduct(callers)
                            return fr / EBP
                        except ParameterNotSpecifiedError:
                            if callers[0] == "__GetElectricalQFactor":
                                return self.__OnParameterNotSpecified(exception=e)
                            else:
                                raise e

    @parameter_getter("mechanical q-factor")
    def __GetMechanicalQFactor(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__mechanical_q_factor is not None:
            return self.__mechanical_q_factor
        else:
            try:
                # try to calculate the mechanical q-factor from the mechanical parameters
                w = self.__GetMechanicalDamping(callers)
                m = self.__GetDiaphragmMass(callers)
                fr = self.__GetResonanceFrequency(callers)
                return (2.0 * math.pi * fr * m) / w
            except ParameterNotSpecifiedError as e:
                try:
                    # try to calculate the mechanical q-factor from the other q-factors
                    Qt = self.__GetTotalQFactor(callers)
                    Qe = self.__GetElectricalQFactor(callers)
                    return (Qe * Qt) / (Qe - Qt)
                except ParameterNotSpecifiedError:
                    try:
                        # try to calculate the mechanical q-factor from the resonance impedance
                        Zmax = self.__GetResonanceImpedance(callers)
                        R = self.__GetVoicecoilResistance(callers)
                        Qe = self.__GetElectricalQFactor(callers)
                        return Qe * (Zmax - R) / R
                    except ParameterNotSpecifiedError:
                        if callers[0] == "__GetMechanicalQFactor":
                            return self.__OnParameterNotSpecified(exception=e)
                        else:
                            raise e

    @parameter_getter("total q-factor")
    def __GetTotalQFactor(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__total_q_factor is not None:
            return self.__total_q_factor
        else:
            try:
                # try to calculate the total q-factor from the other q-factors
                Qe = self.__GetElectricalQFactor(callers)
                Qms = self.__GetMechanicalQFactor(callers)
                return (Qe * Qms) / (Qe + Qms)
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetTotalQFactor":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("equivalent compliance volume")
    def __GetEquivalentComplianceVolume(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__equivalent_compliance_volume is not None:
            return self.__equivalent_compliance_volume
        else:
            try:
                # try to calculate the equivalent compliance volume from the suspension compliance and the diaphragm area
                n = self.__GetSuspensionCompliance(callers)
                S = self.__GetDiaphragmArea(callers)
                rho = self.__medium_density
                c = self.__speed_of_sound
                return rho * (c * S) ** 2 * n
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetEquivalentComplianceVolume":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("resonance impedance")
    def __GetResonanceImpedance(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__resonance_impedance is not None:
            return self.__resonance_impedance
        else:
            try:
                # try to calculate the resonance impedance from the voice coil impedance and the q-factors
                R = self.__GetVoiceCoilResistance(callers)
                Qe = self.__GetElectricalQFactor(callers)
                Qms = self.__GetMechanicalQFactor(callers)
                return R * (1.0 + (Qms / Qe))
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetResonanceImpedance":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    @parameter_getter("efficiency bandwidth product")
    def __GetEfficiencyBandwidthProduct(self, callers=None):
        """
        A private getter method that hides the "callers"-parameter from the public
        API.
        The "callers"-list is maintained by the "parameter_getter"-decorator.
        @param callers: a call stack as a list of getter functions that have been called to calculate the desired value
        """
        # if possible, return the requested value immediately
        if self.__efficiency_bandwidth_product is not None:
            return self.__efficiency_bandwidth_product
        else:
            try:
                # try to calculate the efficiency bandwidth product from the resonance frequency and the electrical q-factor
                fr = self.__GetResonanceFrequency(callers)
                Qe = self.__GetElectricalQFactor(callers)
                return fr / Qe
            except ParameterNotSpecifiedError as e:
                if callers[0] == "__GetEfficiencyBandwidthProduct":
                    return self.__OnParameterNotSpecified(exception=e)
                else:
                    raise e

    #########################
    # other private methods #
    #########################

    def __OnParameterNotSpecified(self, exception):
        """
        A private method that is called, when a requested parameter is neither
        specified, nor is it possible to calculate it from the given parameters.
        It requires the ParameterNotSpecifiedError instance, that has been raised,
        when one of the necessary parameters could not be determined. The error
        message will be extracted from that message.
        @param exception: a ParameterNotSpecifiedError instance
        """
        raise RuntimeError(str(exception))

