# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012 Jonas Schulte-Coerne
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

import unittest
import sumpf
import _common as common


class TestSignalAlgebra(unittest.TestCase):
	"""
	A test case for the algebra modules for Signals.
	"""
	def setUp(self):
		self.signal1 = sumpf.Signal(channels=((4.0, 6.0), (3.0, 5.0)), samplingrate=48000)
		self.signal2 = sumpf.Signal(channels=((2.0, 1.0), (3.0, 7.0)), samplingrate=48000)

	def test_add(self):
		"""
		Tests the addition of Signals.
		"""
		alg = sumpf.modules.AddSignals(signal1=self.signal1, signal2=self.signal2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((6.0, 7.0), (6.0, 12.0)))
		self.assertEqual(res.GetLabels(), ("Sum 1", "Sum 2"))

	def test_subtract(self):
		"""
		Tests the subtraction of Signals.
		"""
		alg = sumpf.modules.SubtractSignals(signal1=self.signal1, signal2=self.signal2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((2.0, 5.0), (0.0, -2.0)))
		self.assertEqual(res.GetLabels(), ("Difference 1", "Difference 2"))

	def test_multiply(self):
		"""
		Tests the multiplication of Signals.
		"""
		alg = sumpf.modules.MultiplySignals(signal1=self.signal1, signal2=self.signal2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((8.0, 6.0), (9.0, 35.0)))
		self.assertEqual(res.GetLabels(), ("Product 1", "Product 2"))

	def test_divide(self):
		"""
		Tests the division of Signals.
		"""
		alg = sumpf.modules.DivideSignals(signal1=self.signal1, signal2=self.signal2)
		res = alg.GetOutput()
		self.assertEqual(res.GetChannels(), ((2.0, 6.0), (1.0, (5.0 / 7.0))))
		self.assertEqual(res.GetLabels(), ("Quotient 1", "Quotient 2"))

	def test_emptysignal(self):
		"""
		Tests if empty Signals are processed as expected.
		"""
		signal = sumpf.Signal(channels=((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)), samplingrate=37.0)
		nullsignal = sumpf.Signal(channels=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), samplingrate=37.0)
		invsignal = sumpf.modules.AmplifySignal(input=signal, factor= -1.0).GetOutput()
		asignal = sumpf.modules.RelabelSignal(input=signal, labels=("Sum 1", "Sum 2")).GetOutput()
		ssignal = sumpf.modules.RelabelSignal(input=signal, labels=("Difference 1", "Difference 2")).GetOutput()
		sinvsignal = sumpf.modules.RelabelSignal(input=invsignal, labels=("Difference 1", "Difference 2")).GetOutput()
		mnullsignal = sumpf.modules.RelabelSignal(input=nullsignal, labels=("Product 1", "Product 2")).GetOutput()
		dnullsignal = sumpf.modules.RelabelSignal(input=nullsignal, labels=("Quotient 1", "Quotient 2")).GetOutput()
		donesignal = sumpf.Signal(channels=((1.0, 1.0),), labels=("Quotient 1",))
		self.assertEqual(sumpf.modules.AddSignals(signal, sumpf.Signal()).GetOutput(), asignal)
		self.assertEqual(sumpf.modules.AddSignals(sumpf.Signal(), signal).GetOutput(), asignal)
		self.assertEqual(sumpf.modules.SubtractSignals(signal, sumpf.Signal()).GetOutput(), ssignal)
		self.assertEqual(sumpf.modules.SubtractSignals(sumpf.Signal(), signal).GetOutput(), sinvsignal)
		self.assertEqual(sumpf.modules.MultiplySignals(signal, sumpf.Signal()).GetOutput(), mnullsignal)
		self.assertEqual(sumpf.modules.MultiplySignals(sumpf.Signal(), signal).GetOutput(), mnullsignal)
		self.assertRaises(ZeroDivisionError, sumpf.modules.DivideSignals(signal, sumpf.Signal()).GetOutput)
		self.assertEqual(sumpf.modules.DivideSignals(sumpf.Signal(), signal).GetOutput(), dnullsignal)
		self.assertEqual(sumpf.modules.DivideSignals(sumpf.Signal(), sumpf.Signal()).GetOutput(), donesignal)

	def test_errors(self):
		"""
		Tests if the algebra modules raise errors correctly.
		"""
		alg = sumpf.modules.AddSignals(signal1=self.signal1)
		alg.SetInput2(sumpf.Signal(channels=((0.0, 1.0, 0.0),), samplingrate=48000))
		self.assertRaises(ValueError, alg.GetOutput)									# shall fail because Signals do not have the same length
		alg.SetInput2(sumpf.Signal(channels=((0.0, 1.0),), samplingrate=44100))
		self.assertRaises(ValueError, alg.GetOutput)									# shall fail if Signals do not have the same sampling rate
		alg.SetInput2(sumpf.Signal(channels=((6.0, 4.0),), samplingrate=48000))		# adding a Signal with different channel count shall not fail. Surplus channels shall simply be cropped.
		self.assertEqual(alg.GetOutput().GetChannels(), ((10.0, 10.0),))

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		for m in [sumpf.modules.AddSignals(), sumpf.modules.SubtractSignals(), sumpf.modules.MultiplySignals(), sumpf.modules.DivideSignals()]:
			self.assertEqual(m.SetInput1.GetType(), sumpf.Signal)
			self.assertEqual(m.SetInput2.GetType(), sumpf.Signal)
			self.assertEqual(m.GetOutput.GetType(), sumpf.Signal)
			common.test_connection_observers(testcase=self,
			                                 inputs=[m.SetInput1, m.SetInput2],
			                                 noinputs=[],
			                                 output=m.GetOutput)

