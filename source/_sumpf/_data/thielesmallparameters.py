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
import inspect


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
	of the frequency, the membrane excursion, the membrane velocity or the
	voice coil temperature (the function's arguments are ordered in that order).
	This makes it possible to partially describe the nonlinear and time variant
	behavior of a loudspeaker.
	The performance is best, when the parameters are either specified as constants
	or as functions with the arguments "frequency", "membrane_excursion",
	"membrane_velocity" and "voicecoil_temperature" that default to 0.0, 0.0, 0.0
	and 20.0 respectively. This allows to replace the getter methods directly with
	the given function.

	Objects of the ThieleSmallParameters class are used by program parts where
	performance is crucial. Therefore some code readability was sacrificed for
	speedy execution.
	The getter methods are created in the constructor, to reduce the stack depth
	of functions that just pass values to another function. The getter methods
	that are implemented in this class are overridden. The documentation and the
	method's name are copied to the overrides.
	"""
	def __init__(self,
	             voicecoil_resistance=6.5,
	             voicecoil_inductance=0.7e-3,
	             force_factor=10.0,
	             suspension_stiffness=5000.0,
	             mechanical_damping=2.0,
	             membrane_mass=0.01,
	             membrane_area=0.0233):
		"""
		@param voicecoil_resistance: a function or a float value for the voice coil resistance in Ohms
		@param voicecoil_inductance: a function or a float value for the voice coil inductance in Henrys
		@param force_factor: a function or a float value for the force factor in Tesla times meters
		@param suspension_stiffness: a function or a float value for the suspension stiffness in Newtons per meter
		@param mechanical_damping: a function or a float value for the mechanical damping in Newton times seconds per meter
		@param membrane_mass: a function or a float value for the combined mass of the membrane, the voice coil and the acoustic load in kilograms
		@param membrane_area: a function or a float value for the effective membrane area in square meters
		"""
		# GetVoiceCoilResistance
		doc = self.GetVoiceCoilResistance.__doc__
		if isinstance(voicecoil_resistance, collections.Callable):
			argspec = inspect.getargspec(voicecoil_resistance)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetVoiceCoilResistance = voicecoil_resistance
			else:
				self.GetVoiceCoilResistance = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: voicecoil_resistance(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetVoiceCoilResistance = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: voicecoil_resistance
		self.GetVoiceCoilResistance.__name__ = "GetVoiceCoilResistance"
		self.GetVoiceCoilResistance.__doc__ = doc
		# GetVoiceCoilInductance
		doc = self.GetVoiceCoilInductance.__doc__
		if isinstance(voicecoil_inductance, collections.Callable):
			argspec = inspect.getargspec(voicecoil_inductance)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetVoiceCoilInductance = voicecoil_inductance
			else:
				self.GetVoiceCoilInductance = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: voicecoil_inductance(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetVoiceCoilInductance = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: voicecoil_inductance
		self.GetVoiceCoilInductance.__name__ = "GetVoiceCoilInductance"
		self.GetVoiceCoilInductance.__doc__ = doc
		# GetForceFactor
		doc = self.GetForceFactor.__doc__
		if isinstance(force_factor, collections.Callable):
			argspec = inspect.getargspec(force_factor)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetForceFactor = force_factor
			else:
				self.GetForceFactor = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: force_factor(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetForceFactor = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: force_factor
		self.GetForceFactor.__name__ = "GetForceFactor"
		self.GetForceFactor.__doc__ = doc
		# GetSuspensionStiffness
		doc = self.GetSuspensionStiffness.__doc__
		if isinstance(suspension_stiffness, collections.Callable):
			argspec = inspect.getargspec(suspension_stiffness)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetSuspensionStiffness = suspension_stiffness
			else:
				self.GetSuspensionStiffness = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: suspension_stiffness(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetSuspensionStiffness = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: suspension_stiffness
		self.GetSuspensionStiffness.__name__ = "GetSuspensionStiffness"
		self.GetSuspensionStiffness.__doc__ = doc
		# GetMechanicalDamping
		doc = self.GetMechanicalDamping.__doc__
		if isinstance(mechanical_damping, collections.Callable):
			argspec = inspect.getargspec(mechanical_damping)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetMechanicalDamping = mechanical_damping
			else:
				self.GetMechanicalDamping = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: mechanical_damping(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetMechanicalDamping = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: mechanical_damping
		self.GetMechanicalDamping.__name__ = "GetMechanicalDamping"
		self.GetMechanicalDamping.__doc__ = doc
		# GetMembraneMass
		doc = self.GetMembraneMass.__doc__
		if isinstance(membrane_mass, collections.Callable):
			argspec = inspect.getargspec(membrane_mass)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetMembraneMass = membrane_mass
			else:
				self.GetMembraneMass = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: membrane_mass(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetMembraneMass = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: membrane_mass
		self.GetMembraneMass.__name__ = "GetMembraneMass"
		self.GetMembraneMass.__doc__ = doc
		# GetMembraneArea
		doc = self.GetMembraneArea.__doc__
		if isinstance(membrane_area, collections.Callable):
			argspec = inspect.getargspec(membrane_area)
			if argspec.args == ["frequency", "membrane_excursion", "membrane_velocity", "voicecoil_temperature"] and argspec.defaults is not None and len(argspec.defaults) == 4:
				self.GetMembraneArea = membrane_area
			else:
				self.GetMembraneArea = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: membrane_area(frequency, membrane_excursion, membrane_velocity, voicecoil_temperature)
		else:
			self.GetMembraneArea = lambda frequency = 0.0, membrane_excursion = 0.0, membrane_velocity = 0.0, voicecoil_temperature = 20.0: membrane_area
		self.GetMembraneArea.__name__ = "GetMembraneArea"
		self.GetMembraneArea.__doc__ = doc

	def GetVoiceCoilResistance(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the DC resistance of the voice coil in Ohms.
		@param frequency: optional float, that can be used to model the voice coil resistance in dependency of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the voice coil resistance in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the voice coil resistance in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the voice coil resistance in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the DC resistance of the voice coil as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

	def GetVoiceCoilInductance(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the voice coil inductance in Henrys.
		@param frequency: optional float, that can be used to model the voice coil inductance in dependency of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the voice coil inductance in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the voice coil inductance in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the voice coil inductance in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the inductance of the voice coil as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

	def GetForceFactor(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the force factor in Tesla times meters.
		@param frequency: optional float, that can be used to model the force factor in dependency of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the force factor in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the force factor in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the force factor in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the force factor as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

	def GetSuspensionStiffness(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the suspension stiffness in Newtons per meter.
		@param frequency: optional float, that can be used to model the suspension stiffness in dependency of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the suspension stiffness in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the suspension stiffness in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the suspension stiffness in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the suspension stiffness as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

	def GetMechanicalDamping(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the damping losses of the mechanical part in Newton times seconds per meter.
		@param frequency: optional float, that can be used to model the mechanical damping in dependency of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the mechanical damping in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the mechanical damping in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the mechanical damping in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the mechanical damping as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

	def GetMembraneMass(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the mass of the membrane including voice coil and acoustic load in kilograms.
		@param frequency: optional float, that can be used to model the membrane mass in dependency of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the membrane mass in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the membrane mass in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the membrane mass in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the membrane mass as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

	def GetMembraneArea(self, frequency=0.0, membrane_excursion=0.0, membrane_velocity=0.0, voicecoil_temperature=20.0):
		"""
		Returns the effective surface area of the membrane in square meters.
		@param frequency: optional float, that can be used to model the membrane area of the frequency (in Hz)
		@param membrane_excursion: optional float, that can be used to model the membrane area in dependency of the membrane excursion (in meters)
		@param membrane_velocity: optional float, that can be used to model the membrane area in dependency of the membrane velocity (in meters per second)
		@param voicecoil_temperature: optional float, that can be used to model the membrane area in dependency of the voice coil temperature (in degrees Celsius)
		@retval : the effective surface area of the membrane as a float
		"""
		# This method is overridden by a function that is created in the constructor.
		# That reduces the stack depth of functions that just pass values to another
		# function and increases the performance of calculations that access the
		# ThieleSmallParameters' values very often.
		pass

