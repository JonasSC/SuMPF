# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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
import inspect
import sys

if sys.version_info.major == 2:
    def get_argspec(function):
        if inspect.isfunction(function):
            return inspect.getargspec(function)
        elif isinstance(function, functools.partial):
            original_argspec = get_argspec(function.func)
            names = list(original_argspec[0] or [])
            defaults = list(original_argspec[3] or [])
            if function.args != []:
                names = names[len(function.args):]
                defaults = defaults[-len(names):]
            for a in function.keywords or []:
                if a in names:
                    index = names.index(a)
                    if index > len(names) - len(defaults):
                        del defaults[index + len(names) - len(defaults)]
                    del names[index]
            return inspect.ArgSpec(args=names, varargs=original_argspec[1], keywords=original_argspec[2], defaults=defaults)
        elif hasattr(function, "__call__"):
            result = inspect.getargspec(function.__call__)
            result.args.remove("self")
            return  result

    def get_callable(function):
        argspec = get_argspec(function)
        if argspec.args == ["f", "x", "v", "T"] and argspec.defaults is not None and len(argspec.defaults) == 4:
            return function
        else:
            return lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: function(f, x, v, T)
else:
    def get_callable(function):
        signature = inspect.signature(function)
        if tuple(signature.parameters.keys()) == ("f", "x", "v", "T") and inspect.Parameter.empty not in [p.default for p in signature.parameters.values()]:
            return function
        else:
            return lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: function(f, x, v, T)

def get_parameter(parameter):
    if isinstance(parameter, collections.Callable):
        return get_callable(parameter)
    else:
        return lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: parameter



class ThieleSmallParameters(object):
    """
    Objects of this class store a set of parameters for the description of the
    small signal performance of a dynamic loudspeaker.

    The parameters in this class are the values that can be substituted directly
    in most mathematical equations that describe the behavior of a loudspeaker
    (e.g. the force-balance equation or the voltage equation). Other parameter
    sets, that are commonly published by loudspeaker manufacturers consist of
    different values like the suspension compliance or the electrical Q-factor.
    To convert between different parameter sets, use the
    TestThieleSmallParameterInterpretation class.

    The parameters can be specified as constant values or as functions in dependency
    of the frequency, the diaphragm excursion, the diaphragm velocity or the
    voice coil temperature (the function's arguments are ordered in that order).
    This makes it possible to partially describe the nonlinear and time variant
    behavior of a loudspeaker.
    The performance is best, when the parameters are either specified as constants
    or as functions with the arguments "f", "x", "v" and "T" that have float
    default values. This allows to replace the getter methods directly with the
    given function.
    Otherwise, the function will be wrapped in another function, that has these
    arguments, with the default values of (f=1000.0, x=0.0, v=0.0 and T=20.0)

    Objects of the ThieleSmallParameters class are used by program parts where
    performance is crucial. Therefore some code readability was sacrificed for
    speedy execution.
    The getter methods are created in the constructor, to reduce the stack depth
    of functions that just pass values to another function. The getter methods
    that are implemented in this class are overridden. The documentation and the
    method's name are copied to the overrides.

    It is possible to pass a function, that returns all values as a tuple, to
    the constructor with the "all_parameters" parameter. When this function is
    specified, all getter methods for the individual parameters will call this
    function and return just the requested element of tuple. This will be slower,
    when the Thiele-Small parameters are mostly used individually. But in applications
    like the loudspeaker simulation, where all parameters are requested regularly
    with the GetAllParameters method, this might increase the performance, by
    decreasing the number of method calls and by allowing an efficient implementation
    for the calculation of the parameter set.
    Please note that the GetAllParameters method and the individual getter for
    the parameters might have differing default values for their parameters. If
    the parameters are specified individually as functions that depend on the
    loudspeaker's state, their default parameters for the loudspeaker's state are
    given in that functions, while the GetAllParameters method still uses the default
    parameters from this class's implementation. So in this case, it is recommended,
    to call the GetAllParameters method with all parameters explicitly specified.
    On the other hand, if the all_parameters parameter is given, the individual
    getter methods should be called with explicitly specified parameters.
    """
    def __init__(self,
                 voicecoil_resistance=6.5,
                 voicecoil_inductance=0.7e-3,
                 force_factor=10.0,
                 suspension_stiffness=5000.0,
                 mechanical_damping=2.0,
                 diaphragm_mass=0.01,
                 diaphragm_area=0.0233,
                 all_parameters=None):
        """
        @param voicecoil_resistance: a function or a float value for the voice coil resistance in Ohms
        @param voicecoil_inductance: a function or a float value for the voice coil inductance in Henrys
        @param force_factor: a function or a float value for the force factor in Tesla times meters
        @param suspension_stiffness: a function or a float value for the suspension stiffness in Newtons per meter
        @param mechanical_damping: a function or a float value for the mechanical damping in Newton times seconds per meter
        @param diaphragm_mass: a function or a float value for the combined mass of the diaphragm, the voice coil and the acoustic load in kilograms
        @param diaphragm_area: a function or a float value for the effective diaphragm area in square meters
        @param all_parameters: None or a function, that returns all parameters as a tuple (see the GetAllParameters method for a specification of this function)
        """
        self.__combined_parameter_definition = isinstance(all_parameters, collections.Callable)
        # store the documentation of the overridden methods
        doc_R = self.GetVoiceCoilResistance.__doc__
        doc_L = self.GetVoiceCoilInductance.__doc__
        doc_M = self.GetForceFactor.__doc__
        doc_k = self.GetSuspensionStiffness.__doc__
        doc_w = self.GetMechanicalDamping.__doc__
        doc_m = self.GetDiaphragmMass.__doc__
        doc_S = self.GetDiaphragmArea.__doc__
        if self.__combined_parameter_definition:
            # GetAllParameters
            doc_all = self.GetAllParameters.__doc__
            self.GetAllParameters = get_callable(all_parameters)
            self.GetVoiceCoilResistance = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[0]
            self.GetVoiceCoilInductance = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[1]
            self.GetForceFactor = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[2]
            self.GetSuspensionStiffness = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[3]
            self.GetMechanicalDamping = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[4]
            self.GetDiaphragmMass = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[5]
            self.GetDiaphragmArea = lambda f = 1000.0, x = 0.0, v = 0.0, T = 20.0: all_parameters(f, x, v, T)[6]
            self.GetAllParameters.__name__ = "GetAllParameters"
            self.GetAllParameters.__doc__ = doc_all
        else:
            self.GetVoiceCoilResistance = get_parameter(voicecoil_resistance)
            self.GetVoiceCoilInductance = get_parameter(voicecoil_inductance)
            self.GetForceFactor = get_parameter(force_factor)
            self.GetSuspensionStiffness = get_parameter(suspension_stiffness)
            self.GetMechanicalDamping = get_parameter(mechanical_damping)
            self.GetDiaphragmMass = get_parameter(diaphragm_mass)
            self.GetDiaphragmArea = get_parameter(diaphragm_area)
        # restore the method's names and documentation
        self.GetVoiceCoilResistance.__name__ = "GetVoiceCoilResistance"
        self.GetVoiceCoilInductance.__name__ = "GetVoiceCoilInductance"
        self.GetForceFactor.__name__ = "GetForceFactor"
        self.GetSuspensionStiffness.__name__ = "GetSuspensionStiffness"
        self.GetMechanicalDamping.__name__ = "GetMechanicalDamping"
        self.GetDiaphragmMass.__name__ = "GetDiaphragmMass"
        self.GetDiaphragmArea.__name__ = "GetDiaphragmArea"
        self.GetVoiceCoilResistance.__doc__ = doc_R
        self.GetVoiceCoilInductance.__doc__ = doc_L
        self.GetForceFactor.__doc__ = doc_M
        self.GetSuspensionStiffness.__doc__ = doc_k
        self.GetMechanicalDamping.__doc__ = doc_w
        self.GetDiaphragmMass.__doc__ = doc_m
        self.GetDiaphragmArea.__doc__ = doc_S

    def IsDefinedByAllParametersFunction(self):
        """
        Returns if the Thiele-Small parameters are defined as individual constructor
        arguments, or if they have been defined in a combined function, that was
        given as the all_parameters argument.
        @retval : True, if all_parameters was given, False, if the parameters are defined individually
        """
        return self.__combined_parameter_definition

    def GetVoiceCoilResistance(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the DC resistance of the voice coil in Ohms.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the DC resistance of the voice coil as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetVoiceCoilInductance(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the voice coil inductance in Henrys.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the inductance of the voice coil as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetForceFactor(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the force factor in Tesla times meters.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the force factor as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetSuspensionStiffness(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the suspension stiffness in Newtons per meter.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the suspension stiffness as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetMechanicalDamping(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the damping losses of the mechanical part in Newton times seconds per meter.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the mechanical damping as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetDiaphragmMass(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the mass of the diaphragm including voice coil and acoustic load in kilograms.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the diaphragm mass as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetDiaphragmArea(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns the effective surface area of the diaphragm in square meters.
        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : the effective surface area of the diaphragm as a float
        """
        # This method is overridden by a function that is created in the constructor.
        # That reduces the stack depth of functions that just pass values to another
        # function and increases the performance of calculations that access the
        # ThieleSmallParameters' values very often.
        pass

    def GetAllParameters(self, f=1000.0, x=0.0, v=0.0, T=20.0):
        """
        Returns a tuple of all parameters.
        Depending on the definition of the parameters, the performance might
        be improved, when the parameters are fetched with this function rather
        than fetching them each with their own getter function.
        The parameters are returned as a tuple with the values in the following
        order:
            0.  voice coil resistance in Ohms
            1.  voice coil inductance in Henrys
            2.  force factor in Tesla times meter
            3.  suspension stiffness in Newtons per meter
            4.  damping losses of the mechanical part in Newton times seconds per meter
            5.  mass of the diaphragm including voice coil and acoustic load in kilograms
            6.  effective surface area of the diaphragm in square meters

        Please note that the GetAllParameters method and the individual getter for
        the parameters might have differing default values for their parameters. If
        the parameters are specified individually as functions that depend on the
        loudspeaker's state, their default parameters for the loudspeaker's state are
        given in that functions, while the GetAllParameters method still uses the default
        parameters from this class's implementation. So in this case, it is recommended,
        to call the GetAllParameters method with all parameters explicitly specified.
        On the other hand, if the all_parameters parameter is given, the individual
        getter methods should be called with explicitly specified parameters.

        @param f: the frequency in Hz, in case the parameter is frequency dependent
        @param x: the excursion of the diaphragm, in case the parameter depends on the excursion
        @param v: the velocity of the diaphragm, in case the parameter depends on the velocity
        @param T: the temperature of the voice coil, in case the parameter depends on that
        @retval : a tuple (R, L, M, k, w, m, S)
        """
        # This function is overridden by a function that is created in the constructor,
        # if the all_parameters parameter is given.
        return (self.GetVoiceCoilResistance(f, x, v, T),
                self.GetVoiceCoilInductance(f, x, v, T),
                self.GetForceFactor(f, x, v, T),
                self.GetSuspensionStiffness(f, x, v, T),
                self.GetMechanicalDamping(f, x, v, T),
                self.GetDiaphragmMass(f, x, v, T),
                self.GetDiaphragmArea(f, x, v, T))

