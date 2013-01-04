# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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

import gc
import unittest

import sumpf
import _common as common


class ProgressTester(object):
	def __init__(self, progress, testcase, count_inputs=True, count_nonobserved_inputs=False, count_outputs=True):
		self.progress = progress
		self.testcase = testcase
		self.progress_indicator = None
		self.count_inputs = count_inputs
		self.count_nonobserved_inputs = count_nonobserved_inputs
		self.count_outputs = count_outputs

	def __Test(self):
		if self.progress[0] >= self.progress[1]:
			self.testcase.assertEqual(self.progress_indicator.GetProgressAsTuple(), self.progress)
			self.testcase.assertAlmostEqual(self.progress_indicator.GetProgressAsFloat(), float(self.progress[1]) / float(self.progress[0]))
			self.testcase.assertEqual(self.progress_indicator.GetProgressAsPercentage(), int(round(100.0 * float(self.progress[1]) / float(self.progress[0]))))

	def SetProgressIndicator(self, indicator):
		self.progress_indicator = indicator

	def SetProgress(self, progress):
		self.progress = progress

	@sumpf.Input(int, ["CachingOutput", "NotCachingOutput"])
	def Input(self, value):
		if self.progress_indicator is not None:
			self.__Test()
			if self.count_inputs:
				self.progress = (self.progress[0], self.progress[1] + 1)

	@sumpf.Input(int)
	def InputNoObserver(self, value):
		if self.progress_indicator is not None:
			self.__Test()
			if self.count_inputs or self.count_nonobserved_inputs:
				self.progress = (self.progress[0], self.progress[1] + 1)

	@sumpf.Trigger(["CachingOutput", "NotCachingOutput"])
	def Trigger(self, value=None):
		if self.progress_indicator is not None:
			self.__Test()
			if self.count_inputs:
				self.progress = (self.progress[0], self.progress[1] + 1)

	@sumpf.MultiInput(int, "Remove", ["CachingOutput", "NotCachingOutput"])
	def MultiInput(self, value):
		if self.progress_indicator is not None:
			self.__Test()
			if self.count_inputs:
				self.progress = (self.progress[0], self.progress[1] + 1)
		return 1

	def Remove(self, data_id):
		if self.progress_indicator is not None:
			self.__Test()

	@sumpf.Output(int, caching=True)
	def CachingOutput(self):
		if self.progress_indicator is not None:
			self.__Test()
			if self.count_outputs:
				self.progress = (self.progress[0], self.progress[1] + 1)

	@sumpf.Output(int, caching=False)
	def NotCachingOutput(self):
		if self.progress_indicator is not None:
			self.__Test()
			if self.count_outputs:
				self.progress = (self.progress[0], self.progress[1] + 1)



class TestProgressIndicators(unittest.TestCase):
	"""
	A TestCase for the ProgressIndicator classes.
	"""
	def test_ProgressIndicator_All(self):
		tester1 = ProgressTester(progress=(6, 0), testcase=self)
		tester2 = ProgressTester(progress=(6, 1), testcase=self)				# tester1.Input done
		sumpf.connect(tester1.CachingOutput, tester2.Trigger)
		tester3 = ProgressTester(progress=(6, 3), testcase=self)				# tester2.Trigger & tester2.Output done
		sumpf.connect(tester2.NotCachingOutput, tester3.MultiInput)
		tester4 = ProgressTester(progress=(6, 5), testcase=self)				# tester3.MultiInput & tester3.Output done
		sumpf.connect(tester3.CachingOutput, tester4.InputNoObserver)
		progress_indicator = sumpf.progressindicators.ProgressIndicator_All(method=tester1.Input)
		tester1.SetProgressIndicator(progress_indicator)
		tester2.SetProgressIndicator(progress_indicator)
		tester3.SetProgressIndicator(progress_indicator)
		tester4.SetProgressIndicator(progress_indicator)
		tester1.Input(1337)
		self.assertEqual(progress_indicator.GetProgressAsTuple(), (6, 6))		# tester4.InputNoObserver done
		self.assertEqual(progress_indicator.GetProgressAsFloat(), 1.0)
		self.assertEqual(progress_indicator.GetProgressAsPercentage(), 100)
		tester1.SetProgress((6, 6))
		tester2.SetProgress((6, 6))
		tester3.SetProgress((6, 6))
		tester1.Input(4711)
		progress_indicator.Destroy()
		del tester1
		del tester2
		del tester3
		del tester4
		gc.collect()
		self.assertEqual(gc.garbage, [])

	def test_ProgressIndicator_Outputs(self):
		tester1 = ProgressTester(progress=(2, 0), testcase=self, count_inputs=False)
		tester2 = ProgressTester(progress=(2, 0), testcase=self, count_inputs=False)
		sumpf.connect(tester1.CachingOutput, tester2.Trigger)
		tester3 = ProgressTester(progress=(2, 1), testcase=self, count_inputs=False)		# tester2.Output done
		sumpf.connect(tester2.NotCachingOutput, tester3.MultiInput)
		tester4 = ProgressTester(progress=(2, 2), testcase=self, count_inputs=False)		# tester3.Output done
		sumpf.connect(tester3.CachingOutput, tester4.InputNoObserver)
		progress_indicator = sumpf.progressindicators.ProgressIndicator_Outputs(method=tester1.Input)
		tester1.SetProgressIndicator(progress_indicator)
		tester2.SetProgressIndicator(progress_indicator)
		tester3.SetProgressIndicator(progress_indicator)
		tester4.SetProgressIndicator(progress_indicator)
		tester1.Input(1337)
		self.assertEqual(progress_indicator.GetProgressAsTuple(), (2, 2))
		self.assertEqual(progress_indicator.GetProgressAsFloat(), 1.0)
		self.assertEqual(progress_indicator.GetProgressAsPercentage(), 100)
		tester1.SetProgress((2, 2))
		tester2.SetProgress((2, 2))
		tester3.SetProgress((2, 2))
		tester1.Input(4711)
		progress_indicator.Destroy()
		del tester1
		del tester2
		del tester3
		del tester4
		gc.collect()
		self.assertEqual(gc.garbage, [])

	def test_ProgressIndicator_OutputsAndNonObservedInputs(self):
		tester1 = ProgressTester(progress=(3, 0), testcase=self, count_inputs=False, count_nonobserved_inputs=True)
		tester2 = ProgressTester(progress=(3, 0), testcase=self, count_inputs=False, count_nonobserved_inputs=True)
		sumpf.connect(tester1.CachingOutput, tester2.Trigger)
		tester3 = ProgressTester(progress=(3, 1), testcase=self, count_inputs=False, count_nonobserved_inputs=True)		# tester2.Output done
		sumpf.connect(tester2.NotCachingOutput, tester3.MultiInput)
		tester4 = ProgressTester(progress=(3, 2), testcase=self, count_inputs=False, count_nonobserved_inputs=True)		# tester3.Output done
		sumpf.connect(tester3.CachingOutput, tester4.InputNoObserver)
		progress_indicator = sumpf.progressindicators.ProgressIndicator_OutputsAndNonObservedInputs(method=tester1.Input)
		tester1.SetProgressIndicator(progress_indicator)
		tester2.SetProgressIndicator(progress_indicator)
		tester3.SetProgressIndicator(progress_indicator)
		tester4.SetProgressIndicator(progress_indicator)
		tester1.Input(1337)
		self.assertEqual(progress_indicator.GetProgressAsTuple(), (3, 3))												# tester4.InputNoObserver done
		self.assertEqual(progress_indicator.GetProgressAsFloat(), 1.0)
		self.assertEqual(progress_indicator.GetProgressAsPercentage(), 100)
		tester1.SetProgress((3, 3))
		tester2.SetProgress((3, 3))
		tester3.SetProgress((3, 3))
		tester1.Input(4711)
		progress_indicator.Destroy()
		del tester1
		del tester2
		del tester3
		del tester4
		gc.collect()
		self.assertEqual(gc.garbage, [])

	def test_setting_to_different_connectors(self):
		for m in ["Input", "Trigger", "MultiInput"]:
			tester1 = ProgressTester(progress=(3, 0), testcase=self)
			tester2 = ProgressTester(progress=(3, 2), testcase=self)
			sumpf.connect(tester1.CachingOutput, tester2.Input)
			progress_indicator = sumpf.progressindicators.ProgressIndicator_All(method=getattr(tester1, m))
			tester1.SetProgressIndicator(progress_indicator)
			tester2.SetProgressIndicator(progress_indicator)
			getattr(tester1, m)(1337)

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		tester = ProgressTester(progress=(1, 0), testcase=self)
		for p in [sumpf.progressindicators.ProgressIndicator_All,
		          sumpf.progressindicators.ProgressIndicator_Outputs,
		          sumpf.progressindicators.ProgressIndicator_OutputsAndNonObservedInputs]:
			pi = p(method=tester.InputNoObserver)
			self.assertEqual(pi.Report.GetType(), sumpf.internal.Connector)
			common.test_connection_observers(testcase=self,
			                                 inputs=[pi.Report],
			                                 noinputs=[],
			                                 output=pi.GetProgressAsTuple)
			common.test_connection_observers(testcase=self,
			                                 inputs=[pi.Report],
			                                 noinputs=[],
			                                 output=pi.GetProgressAsFloat)
			common.test_connection_observers(testcase=self,
			                                 inputs=[pi.Report],
			                                 noinputs=[],
			                                 output=pi.GetProgressAsPercentage)

